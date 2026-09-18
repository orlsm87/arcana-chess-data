"""
Tests for API manifest generation and checksum calculations.
"""

import json
import os
import tempfile
import unittest

from src.api.generate_manifest import build_manifest_payload, calculate_sha256, write_manifest_files


class TestManifest(unittest.TestCase):

    def test_calculate_sha256(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
            tf.write("arcana chess data test payload")
            tf_path = tf.name

        try:
            sha = calculate_sha256(tf_path)
            self.assertTrue(len(sha) == 64)
            self.assertEqual(sha, "94dadd2b1db57bd0bd6f5df4e47db84a10baff9f3eb315b7f7e3fab8a36a0ede")
        finally:
            os.unlink(tf_path)

    def test_build_manifest(self):
        payload = build_manifest_payload(
            latest_issue=1662,
            total_games=4918250,
            repo_owner="orlsm87",
            repo_name="arcana-chess-data",
            delta_games_count=3680
        )

        self.assertEqual(payload["service"], "Arcana Chess Data Cloud")
        self.assertEqual(payload["version"], "1.0")
        self.assertEqual(payload["latest_issue"], 1662)
        self.assertEqual(payload["total_games"], 4918250)
        self.assertIn("releases/download/v1662/arcana_twic_master.db.zst", payload["master_database"]["download_url"])
        self.assertIn("releases/download/v1662/twic_1662.zip", payload["weekly_delta"]["download_url"])
        self.assertEqual(payload["weekly_delta"]["games_count"], 3680)

    def test_write_manifest_files(self):
        with tempfile.TemporaryDirectory() as td:
            out_file = os.path.join(td, "manifest.json")
            payload = {"test": "ok", "service": "Arcana Chess Data Cloud"}
            write_manifest_files(payload, (out_file,))

            with open(out_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)

            self.assertEqual(loaded["test"], "ok")


if __name__ == "__main__":
    unittest.main()
