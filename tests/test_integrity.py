"""
Tests for integrity verification script.
"""

import os
import shutil
import tempfile
import unittest

from scripts.verify_integrity import verify_database_integrity, verify_manifest_checksums
from src.database.master_builder import MasterDatabase
from src.parser.pgn_cleaner import stream_pgn_games

SAMPLE_GAME = """
[Event "Test Tournament"]
[Site "Online"]
[Date "2024.01.01"]
[Round "1"]
[White "Carlsen, Magnus"]
[Black "Nakamura, Hikaru"]
[Result "1-0"]
[WhiteElo "2882"]
[BlackElo "2789"]
[ECO "B90"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 1-0
"""


class TestIntegrity(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test.db")
        db = MasterDatabase(self.db_path)
        games = list(stream_pgn_games(SAMPLE_GAME))
        db.ingest_games(1500, games)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_database_integrity(self):
        self.assertTrue(verify_database_integrity(self.db_path))

    def test_manifest_verification(self):
        manifest_path = os.path.join(self.test_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write('{"service": "Arcana Chess Data Cloud", "version": "1.0", "updated_at": "2024-01-01T00:00:00Z", "latest_issue": 1500, "total_games": 1, "master_database": {}}')

        self.assertTrue(verify_manifest_checksums(manifest_path))


if __name__ == "__main__":
    unittest.main()
