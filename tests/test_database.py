"""
Tests for SQLite master database builder, WAL mode, queries, and compression.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from src.database.master_builder import MasterDatabase
from src.parser.pgn_cleaner import stream_pgn_games

SAMPLE_PGN = """
[Event "Candidates Tournament 2024"]
[Site "Toronto CAN"]
[Date "2024.04.14"]
[Round "10"]
[White "Nakamura, H."]
[Black "Caruana, F."]
[Result "1-0"]
[WhiteElo "2789"]
[BlackElo "2803"]
[ECO "C54"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. c3 Nf6 5. d3 d6 1-0

[Event "Candidates Tournament 2024"]
[Site "Toronto CAN"]
[Date "2024.04.14"]
[Round "10"]
[White "Gukesh, D."]
[Black "Nepomniachtchi, I."]
[Result "1/2-1/2"]
[WhiteElo "2743"]
[BlackElo "2758"]
[ECO "C42"]

1. e4 e5 2. Nf3 Nf6 3. Nxe5 d6 4. Nf3 Nxe4 1/2-1/2
"""


class TestMasterDatabase(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_master.db")
        self.master_db = MasterDatabase(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_schema_and_ingestion(self):
        # Database should be initialized
        self.assertTrue(Path(self.db_path).exists())

        # Ingest games for issue 1540
        games = list(stream_pgn_games(SAMPLE_PGN))
        inserted = self.master_db.ingest_games(1540, games)
        self.assertEqual(inserted, 2)

        # Verify tracking table
        self.assertTrue(self.master_db.is_issue_processed(1540))
        self.assertFalse(self.master_db.is_issue_processed(1541))

        # Check stats
        stats = self.master_db.get_stats()
        self.assertEqual(stats["total_games"], 2)
        self.assertEqual(stats["latest_issue"], 1540)

        # Check queries
        conn = self.master_db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT white, black, eco FROM games WHERE result = '1-0'")
        row = cur.fetchone()
        self.assertEqual(row["white"], "Nakamura, Hikaru")
        self.assertEqual(row["black"], "Caruana, Fabiano")
        self.assertEqual(row["eco"], "C54")
        conn.close()

    def test_export_and_compression(self):
        games = list(stream_pgn_games(SAMPLE_PGN))
        self.master_db.ingest_games(1540, games)

        # Test master PGN export
        export_pgn = os.path.join(self.test_dir, "master_export.pgn")
        exported_count = self.master_db.export_master_pgn(export_pgn)
        self.assertEqual(exported_count, 2)
        self.assertTrue(os.path.exists(export_pgn))

        # Test compression
        zst_path = self.master_db.compress_with_zstd(self.db_path)
        self.assertTrue(os.path.exists(zst_path))


if __name__ == "__main__":
    unittest.main()
