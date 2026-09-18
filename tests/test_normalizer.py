"""
Tests for FIDE name and ELO normalization.
"""

import unittest
from src.parser.fide_normalizer import normalize_elo, normalize_player_name


class TestFideNormalizer(unittest.TestCase):

    def test_canonical_aliases(self):
        self.assertEqual(normalize_player_name("Carlsen, M."), "Carlsen, Magnus")
        self.assertEqual(normalize_player_name("carlsen, m"), "Carlsen, Magnus")
        self.assertEqual(normalize_player_name("Carlsen, Magnus"), "Carlsen, Magnus")
        self.assertEqual(normalize_player_name("Kasparov, G."), "Kasparov, Garry")
        self.assertEqual(normalize_player_name("Kramnik, V."), "Kramnik, Vladimir")
        self.assertEqual(normalize_player_name("Anand, V."), "Anand, Viswanathan")
        self.assertEqual(normalize_player_name("Fischer, Bobby"), "Fischer, Robert J.")

    def test_title_stripping(self):
        self.assertEqual(normalize_player_name("GM Carlsen, Magnus"), "Carlsen, Magnus")
        self.assertEqual(normalize_player_name("Carlsen, Magnus GM"), "Carlsen, Magnus")
        self.assertEqual(normalize_player_name("IM Polgar, Judit"), "Polgar, Judit")

    def test_capitalization_and_hyphens(self):
        self.assertEqual(normalize_player_name("CARLSEN, MAGNUS"), "Carlsen, Magnus")
        self.assertEqual(normalize_player_name("vachier-lagrave, m."), "Vachier-Lagrave, Maxime")

    def test_unknown_and_empty(self):
        self.assertEqual(normalize_player_name(""), "Unknown")
        self.assertEqual(normalize_player_name("?"), "Unknown")
        self.assertEqual(normalize_player_name("NN"), "Unknown")
        self.assertEqual(normalize_player_name(None), "Unknown")

    def test_elo_normalization(self):
        self.assertEqual(normalize_elo("2882"), 2882)
        self.assertEqual(normalize_elo("2850.0"), 2850)
        self.assertEqual(normalize_elo("  2750  "), 2750)
        self.assertIsNone(normalize_elo(""))
        self.assertIsNone(normalize_elo("0"))
        self.assertIsNone(normalize_elo("none"))
        self.assertIsNone(normalize_elo("-"))
        self.assertIsNone(normalize_elo("500"))  # Out of competitive bounds
        self.assertIsNone(normalize_elo(None))


if __name__ == "__main__":
    unittest.main()
