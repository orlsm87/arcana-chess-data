"""
Tests for PGN streaming parser, tag sanitization, and deduplication.
"""

import unittest
from src.parser.pgn_cleaner import clean_moves_text, stream_pgn_games, normalize_result, normalize_eco

SAMPLE_PGN = """
[Event "FIDE World Cup 2023"]
[Site "Baku AZE"]
[Date "2023.08.24"]
[Round "8.3"]
[White "Praggnanandhaa, R"]
[Black "Carlsen, M."]
[Result "0-1"]
[WhiteElo "2690"]
[BlackElo "2835"]
[ECO "C88"]

1. e4 {Opening move} 1... e5 2. Nf3 Nc6 3. Bb5 a6 (3... Nf6) 4. Ba4 Nf6 0-1

[Event "Corrupted Empty Game"]
[Site "Nowhere"]
[Date "2024.01.01"]
[Round "1"]
[White "Unknown, Player"]
[Black "Unknown, Opponent"]
[Result "*"]

*

[Event "Duplicate Test"]
[Site "Baku AZE"]
[Date "2023.08.24"]
[Round "8.3"]
[White "Praggnanandhaa, R."]
[Black "Carlsen, Magnus"]
[Result "0-1"]
[WhiteElo "2690"]
[BlackElo "2835"]
[ECO "C88"]

1. e4 1... e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 0-1
"""


class TestPgnCleaner(unittest.TestCase):

    def test_clean_moves_text(self):
        raw = "1. e4 {First move} 1... e5 (1... c5 2. Nf3) [%clk 1:30:00] 2. Nf3 $1"
        cleaned = clean_moves_text(raw)
        self.assertNotIn("{First move}", cleaned)
        self.assertNotIn("(1... c5 2. Nf3)", cleaned)
        self.assertNotIn("[%clk", cleaned)
        self.assertNotIn("$1", cleaned)
        self.assertIn("1. e4 1... e5 2. Nf3", cleaned)

    def test_normalize_result_and_eco(self):
        self.assertEqual(normalize_result("1-0"), "1-0")
        self.assertEqual(normalize_result("1/2-1/2"), "1/2-1/2")
        self.assertEqual(normalize_result("0.5-0.5"), "1/2-1/2")
        self.assertEqual(normalize_result("1/2"), "1/2-1/2")
        self.assertEqual(normalize_result(""), "*")

        self.assertEqual(normalize_eco("c88"), "C88")
        self.assertEqual(normalize_eco("B90"), "B90")
        self.assertEqual(normalize_eco("invalid"), "")

    def test_streaming_and_deduplication(self):
        games = list(stream_pgn_games(SAMPLE_PGN, deduplicate=True))
        # The corrupted game should be filtered out, and the duplicate game should be discarded
        self.assertEqual(len(games), 1)

        game = games[0]
        self.assertEqual(game.white, "Praggnanandhaa, R")
        self.assertEqual(game.black, "Carlsen, Magnus")
        self.assertEqual(game.result, "0-1")
        self.assertEqual(game.eco, "C88")
        self.assertEqual(game.white_elo, 2690)
        self.assertEqual(game.black_elo, 2835)
        self.assertIn('[Black "Carlsen, Magnus"]', game.pgn)


if __name__ == "__main__":
    unittest.main()
