#!/usr/bin/env python3
"""
Arcana Chess Data Cloud - Historical Bootstrap Tool
Performs initial bulk ingestion of historical TWIC archives into the Master SQLite database.
Supports local zip folders, batch downloading with polite delays, and master artifact bundling.
"""

import argparse
import glob
import os
import re
import sys
import time
from pathlib import Path

# Add repo root to python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.generate_manifest import build_manifest_payload, write_manifest_files
from src.crawler.twic_downloader import download_twic_zip, extract_pgn_from_zip, get_latest_twic_issue
from src.database.master_builder import MasterDatabase
from src.parser.pgn_cleaner import stream_pgn_games


def process_zip_issue(master_db: MasterDatabase, zip_file: Path, issue_num: int) -> int:
    """Extracts, cleans, and indexes a single TWIC zip archive."""
    if master_db.is_issue_processed(issue_num):
        print(f"⏩ Issue {issue_num} already indexed. Skipping.")
        return 0

    print(f"📦 Indexing TWIC Issue {issue_num} from {zip_file.name}...")
    try:
        pgn_file = extract_pgn_from_zip(zip_file, extract_dir="data/extracted_pgns")
        with open(pgn_file, "r", encoding="utf-8", errors="ignore") as f:
            game_stream = stream_pgn_games(f, deduplicate=True)
            inserted = master_db.ingest_games(issue_num, game_stream, batch_size=5000)

        # Cleanup extracted raw PGN to conserve disk space
        pgn_file.unlink(missing_ok=True)
        print(f"   ✅ Issue {issue_num}: {inserted:,} games successfully indexed.")
        return inserted
    except Exception as e:
        print(f"   ❌ Error processing issue {issue_num}: {e}")
        return 0


def bootstrap_from_local_dir(master_db: MasterDatabase, local_dir: str) -> None:
    """Scans and indexes a directory of existing TWIC zip files."""
    zips = glob.glob(os.path.join(local_dir, "twic*g.zip")) + glob.glob(os.path.join(local_dir, "twic*.zip"))
    if not zips:
        print(f"No TWIC zip files found in {local_dir}")
        return

    # Extract issue numbers and sort
    issue_zips = []
    for z in zips:
        match = re.search(r"twic(\d+)", Path(z).name, re.IGNORECASE)
        if match:
            issue_zips.append((int(match.group(1)), Path(z)))

    issue_zips.sort(key=lambda x: x[0])
    print(f"Found {len(issue_zips)} local TWIC archives to process.")

    total_added = 0
    start_time = time.time()
    for issue_num, zip_path in issue_zips:
        total_added += process_zip_issue(master_db, zip_path, issue_num)

    elapsed = round(time.time() - start_time, 1)
    stats = master_db.get_stats()
    print(f"\n🎉 Local bootstrap completed in {elapsed}s!")
    print(f"Total Database Games: {stats['total_games']:,} across issues {stats['oldest_issue']}-{stats['latest_issue']}")


def bootstrap_from_web(master_db: MasterDatabase, start_issue: int, end_issue: int, delay: float) -> None:
    """Sequentially downloads and ingests TWIC issues from the web."""
    print(f"Starting respectful web bootstrap from issue {start_issue} to {end_issue} (delay: {delay}s)...")
    total_added = 0
    start_time = time.time()

    for issue in range(start_issue, end_issue + 1):
        if master_db.is_issue_processed(issue):
            print(f"⏩ Issue {issue} already in database. Skipping download.")
            continue

        try:
            zip_path = download_twic_zip(issue, dest_dir="data/raw_zips", delay_seconds=delay)
            total_added += process_zip_issue(master_db, zip_path, issue)
        except Exception as e:
            print(f"⚠️ Could not fetch issue {issue}: {e}")
            time.sleep(delay * 2)

    elapsed = round(time.time() - start_time, 1)
    stats = master_db.get_stats()
    print(f"\n🎉 Web bootstrap finished in {elapsed}s! Total games in database: {stats['total_games']:,}")


def main():
    parser = argparse.ArgumentParser(description="Arcana Chess Data Cloud - Historical Bootstrapper")
    parser.add_argument("--db", type=str, default="data/arcana_twic_master.db", help="Path to master SQLite file")
    parser.add_argument("--local-dir", type=str, help="Directory containing pre-downloaded TWIC zips")
    parser.add_argument("--start", type=int, default=1, help="Start issue number for web download")
    parser.add_argument("--end", type=int, default=None, help="End issue number (defaults to latest available)")
    parser.add_argument("--delay", type=float, default=1.5, help="Polite delay between HTTP requests in seconds")
    parser.add_argument("--export-pgn", action="store_true", help="Export full master PGN file after indexing")
    parser.add_argument("--compress", action="store_true", help="Compress master SQLite DB with Zstandard")

    args = parser.parse_args()

    db = MasterDatabase(db_path=args.db)

    if args.local_dir:
        bootstrap_from_local_dir(db, args.local_dir)
    else:
        end_issue = args.end if args.end else get_latest_twic_issue()
        bootstrap_from_web(db, args.start, end_issue, args.delay)

    stats = db.get_stats()

    pgn_zip_path = None
    if args.export_pgn:
        print("\nExporting master consolidated PGN...")
        pgn_count = db.export_master_pgn("dist/arcana_twic_master.pgn")
        print(f"Exported {pgn_count:,} games to dist/arcana_twic_master.pgn")
        import zipfile
        pgn_zip_path = "dist/arcana_twic_master.pgn.zip"
        with zipfile.ZipFile(pgn_zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            zf.write("dist/arcana_twic_master.pgn", arcname="arcana_twic_master.pgn")
        Path("dist/arcana_twic_master.pgn").unlink(missing_ok=True)
        print(f"Compressed master PGN to: {pgn_zip_path}")

    compressed_path = None
    if args.compress:
        print("\nCompressing master SQLite database with Zstandard...")
        compressed_path = db.compress_with_zstd(str(db.db_path), "dist/arcana_twic_master.db.zst")
        print(f"Compressed master database to: {compressed_path}")

    # Generate updated manifest
    manifest = build_manifest_payload(
        latest_issue=stats["latest_issue"],
        total_games=stats["total_games"],
        db_file=compressed_path,
        pgn_zip_file=pgn_zip_path
    )
    write_manifest_files(manifest)
    print("Updated manifest.json")


if __name__ == "__main__":
    main()
