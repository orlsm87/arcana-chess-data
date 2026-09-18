"""
Arcana Chess Data Cloud - SQLite Master Database Builder
Handles WAL-mode batch ingestion, incremental synchronizations, master PGN export,
and compression with Zstandard and Zip.
"""

import datetime
import os
import shutil
import sqlite3
import subprocess
import zipfile
from pathlib import Path
from typing import Dict, Generator, Iterable, List, Optional, Tuple

from src.parser.pgn_cleaner import CleanedGame, stream_pgn_games

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


class MasterDatabase:
    """Manages the Master SQLite database for Arcana Chess Data Cloud."""

    def __init__(self, db_path: str = "data/arcana_twic_master.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Opens a SQLite connection with high-performance PRAGMAs."""
        conn = sqlite3.connect(str(self.db_path), timeout=60.0)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode = WAL;")
        cur.execute("PRAGMA synchronous = NORMAL;")
        cur.execute("PRAGMA busy_timeout = 60000;")
        cur.execute("PRAGMA cache_size = -64000;")  # 64 MB RAM cache
        cur.execute("PRAGMA temp_store = MEMORY;")
        cur.close()
        return conn

    def init_db(self) -> None:
        """Applies DDL schema and indexes if not already created."""
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            ddl = f.read()

        with self.get_connection() as conn:
            conn.executescript(ddl)

    def is_issue_processed(self, issue: int) -> bool:
        """Checks if a TWIC issue has already been indexed."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM processed_issues WHERE issue = ?", (issue,))
            return cur.fetchone() is not None

    def ingest_games(self, issue: int, games: Iterable[CleanedGame], batch_size: int = 5000) -> int:
        """
        Inserts a stream of CleanedGame objects in fast batches.
        Returns the number of games inserted.
        """
        insert_sql = """
        INSERT INTO games (
            twic_issue, event, site, date, round,
            white, black, result, white_elo, black_elo, eco, pgn
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        conn = self.get_connection()
        total_inserted = 0
        batch: List[Tuple] = []

        try:
            cur = conn.cursor()
            for game in games:
                batch.append((
                    issue,
                    game.event,
                    game.site,
                    game.date,
                    game.round,
                    game.white,
                    game.black,
                    game.result,
                    game.white_elo,
                    game.black_elo,
                    game.eco,
                    game.pgn
                ))

                if len(batch) >= batch_size:
                    cur.executemany(insert_sql, batch)
                    total_inserted += len(batch)
                    batch.clear()

            if batch:
                cur.executemany(insert_sql, batch)
                total_inserted += len(batch)
                batch.clear()

            # Record issue in tracking table
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            cur.execute(
                "INSERT OR REPLACE INTO processed_issues (issue, processed_at, games_count) VALUES (?, ?, ?)",
                (issue, now_iso, total_inserted)
            )

            # Update master metadata efficiently
            try:
                cur.execute("SELECT SUM(games_count) FROM processed_issues")
                sum_row = cur.fetchone()
                total_db_games = sum_row[0] if sum_row and sum_row[0] else total_inserted
                cur.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('total_games', ?)", (str(total_db_games),))
                cur.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('latest_issue', ?)", (str(issue),))
                cur.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('updated_at', ?)", (now_iso,))
            except Exception:
                pass

            conn.commit()
        finally:
            conn.close()

        return total_inserted

    def get_stats(self) -> Dict:
        """Returns key metrics from the database."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM games")
            total_games = cur.fetchone()[0]

            cur.execute("SELECT MAX(issue), MIN(issue) FROM processed_issues")
            max_issue, min_issue = cur.fetchone()

            approx_players = 0
            try:
                cur.execute("SELECT value FROM metadata WHERE key = 'approx_players'")
                row = cur.fetchone()
                if row:
                    approx_players = int(row[0])
            except Exception:
                pass

            file_size_mb = round(os.path.getsize(self.db_path) / (1024 * 1024), 2) if self.db_path.exists() else 0.0

            return {
                "total_games": total_games,
                "latest_issue": max_issue or 0,
                "oldest_issue": min_issue or 0,
                "approx_players": approx_players,
                "file_size_mb": file_size_mb,
                "db_path": str(self.db_path)
            }

    def export_master_pgn(self, output_pgn_path: str) -> int:
        """
        Streams all games from SQLite into a master .pgn file.
        Returns the number of games exported.
        """
        out_path = Path(output_pgn_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with self.get_connection() as conn, open(out_path, "w", encoding="utf-8") as f:
            cur = conn.cursor()
            cur.execute("SELECT pgn FROM games ORDER BY id ASC")
            count = 0
            while True:
                rows = cur.fetchmany(10000)
                if not rows:
                    break
                for row in rows:
                    f.write(row[0])
                    f.write("\n")
                    count += 1
        return count

    def compress_with_zstd(self, source_file: str, target_zst: Optional[str] = None) -> str:
        """
        Compresses a file using Zstandard (.zst).
        Supports Python zstandard module, CLI zstd, or falls back to zip.
        """
        src = Path(source_file)
        dst = Path(target_zst if target_zst else f"{src}.zst")
        dst.parent.mkdir(parents=True, exist_ok=True)

        # 1. Try python zstandard module
        try:
            import zstandard as zstd
            cctx = zstd.ZstdCompressor(level=15, threads=-1)
            with open(src, "rb") as f_in, open(dst, "wb") as f_out:
                cctx.copy_stream(f_in, f_out)
            return str(dst)
        except ImportError:
            pass

        # 2. Try system CLI zstd command
        if shutil.which("zstd"):
            cmd = ["zstd", "-15", "-f", str(src), "-o", str(dst)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and dst.exists():
                return str(dst)

        # 3. Fallback: create high-compression zip
        fallback_zip = src.with_suffix(src.suffix + ".zip")
        with zipfile.ZipFile(fallback_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            zf.write(src, arcname=src.name)
        return str(fallback_zip)

    def create_weekly_delta_package(self, issue: int, cleaned_pgn_path: str, output_dir: str = "dist") -> str:
        """
        Creates a weekly delta zip bundle containing the cleaned issue PGN
        and metadata JSON for direct download or app consumption.
        """
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        zip_path = out_dir / f"twic_{issue}.zip"

        pgn_file = Path(cleaned_pgn_path)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            zf.write(pgn_file, arcname=f"twic_{issue}.pgn")

        return str(zip_path)
