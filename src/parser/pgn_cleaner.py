"""
Arcana Chess Data Cloud - PGN Cleaner and Sanitizer
High-performance streaming PGN parser, tag validator, move sanitizer, and deduplicator.
"""

import hashlib
import re
from typing import Dict, Generator, Optional, Tuple, Set

from src.parser.fide_normalizer import normalize_elo, normalize_player_name


# Regex patterns for fast PGN parsing
TAG_REGEX = re.compile(r'^\[(\w+)\s+"(.*)"\]\s*$')
COMMENT_REGEX = re.compile(r"\{[^}]*\}")
VARIATION_REGEX = re.compile(r"\([^()]*\)")
CLK_EVAL_REGEX = re.compile(r"\[%(?:clk|eval|emt)[^]]*\]", re.IGNORECASE)
NAG_REGEX = re.compile(r"\$\d+")
RESULT_VALUES = {"1-0", "0-1", "1/2-1/2", "*"}
ECO_REGEX = re.compile(r"^[A-E]\d{2}$")


class CleanedGame:
    """Represents a validated and sanitized chess game."""
    __slots__ = (
        "event", "site", "date", "round", "white", "black",
        "result", "white_elo", "black_elo", "eco", "moves", "pgn", "fingerprint"
    )

    def __init__(
        self,
        event: str,
        site: str,
        date: str,
        round_str: str,
        white: str,
        black: str,
        result: str,
        white_elo: Optional[int],
        black_elo: Optional[int],
        eco: str,
        moves: str,
        pgn: str,
        fingerprint: str
    ):
        self.event = event
        self.site = site
        self.date = date
        self.round = round_str
        self.white = white
        self.black = black
        self.result = result
        self.white_elo = white_elo
        self.black_elo = black_elo
        self.eco = eco
        self.moves = moves
        self.pgn = pgn
        self.fingerprint = fingerprint

    def to_dict(self) -> Dict:
        return {
            "event": self.event,
            "site": self.site,
            "date": self.date,
            "round": self.round,
            "white": self.white,
            "black": self.black,
            "result": self.result,
            "white_elo": self.white_elo,
            "black_elo": self.black_elo,
            "eco": self.eco,
            "pgn": self.pgn,
            "fingerprint": self.fingerprint
        }


def normalize_result(result_str: Optional[str]) -> str:
    """Standardizes chess game results into 1-0, 0-1, 1/2-1/2, or *."""
    if not result_str:
        return "*"
    clean = result_str.strip().replace(" ", "")
    if clean in ("1-0", "1:0"):
        return "1-0"
    if clean in ("0-1", "0:1"):
        return "0-1"
    if clean in ("1/2-1/2", "0.5-0.5", "1/2", "0.5"):
        return "1/2-1/2"
    return "*"


def normalize_eco(eco_str: Optional[str]) -> str:
    """Validates and formats ECO code (e.g. B90, C88)."""
    if not eco_str:
        return ""
    clean = eco_str.strip().upper()
    if ECO_REGEX.match(clean):
        return clean
    return ""


def clean_moves_text(raw_moves: str) -> str:
    """
    Cleans raw move text by removing comments, clock stamps, and variations
    while preserving standard algebraic notation and move numbering.
    """
    moves = CLK_EVAL_REGEX.sub("", raw_moves)
    # Remove nested variations iteratively
    while "(" in moves and ")" in moves:
        new_moves = VARIATION_REGEX.sub("", moves)
        if new_moves == moves:
            break
        moves = new_moves

    # Remove standard comments { ... }
    moves = COMMENT_REGEX.sub("", moves)
    # Remove NAGs ($1, $2, etc.)
    moves = NAG_REGEX.sub("", moves)
    # Collapse multiple whitespaces and linebreaks into single spaces
    moves = re.sub(r"\s+", " ", moves).strip()
    return moves


def compute_game_fingerprint(white: str, black: str, date: str, moves: str) -> str:
    """
    Computes a deterministic hash fingerprint for game deduplication.
    Uses normalized players, date, and move sequence.
    """
    # Extract just the first 15 move tokens to remain resilient to minor notation diffs
    move_tokens = moves.split()[:30]
    simplified_moves = " ".join(move_tokens)
    key = f"{white.lower()}|{black.lower()}|{date.strip()}|{simplified_moves}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def format_standard_pgn(
    event: str,
    site: str,
    date: str,
    round_str: str,
    white: str,
    black: str,
    result: str,
    white_elo: Optional[int],
    black_elo: Optional[int],
    eco: str,
    clean_moves: str
) -> str:
    """Constructs a clean, standard seven-tag roster PGN."""
    tags = [
        f'[Event "{event}"]',
        f'[Site "{site}"]',
        f'[Date "{date}"]',
        f'[Round "{round_str}"]',
        f'[White "{white}"]',
        f'[Black "{black}"]',
        f'[Result "{result}"]'
    ]
    if white_elo:
        tags.append(f'[WhiteElo "{white_elo}"]')
    if black_elo:
        tags.append(f'[BlackElo "{black_elo}"]')
    if eco:
        tags.append(f'[ECO "{eco}"]')

    # Ensure result is at the end of moves
    moves_text = clean_moves
    if result != "*" and not moves_text.endswith(result):
        moves_text = f"{moves_text} {result}".strip()

    return "\n".join(tags) + "\n\n" + moves_text + "\n"


def stream_pgn_games(pgn_text_or_lines, deduplicate: bool = True) -> Generator[CleanedGame, None, None]:
    """
    High-performance generator that parses and yields CleanedGame objects.
    Accepts an iterable of lines or a single string.
    Filters out invalid, empty, or corrupted games.
    """
    seen_fingerprints: Set[str] = set()

    if isinstance(pgn_text_or_lines, str):
        lines = pgn_text_or_lines.splitlines()
    else:
        lines = pgn_text_or_lines

    current_tags: Dict[str, str] = {}
    current_moves: list = []
    in_moves = False

    def build_game() -> Optional[CleanedGame]:
        if not current_tags and not current_moves:
            return None

        raw_moves = " ".join(current_moves).strip()
        clean_moves = clean_moves_text(raw_moves)

        # Discard games without moves (empty games / forfeit without moves)
        if not clean_moves or len(clean_moves) < 3:
            return None

        # Check for presence of move numbers (e.g. "1." or "1...")
        if not re.search(r"\b1\s*\.", clean_moves):
            return None

        white = normalize_player_name(current_tags.get("White"))
        black = normalize_player_name(current_tags.get("Black"))

        # If both players are Unknown, discard game
        if white == "Unknown" and black == "Unknown":
            return None

        event = current_tags.get("Event", "Unknown Event").strip() or "Unknown Event"
        site = current_tags.get("Site", "Unknown Site").strip() or "Unknown Site"
        date = current_tags.get("Date", "????.??.??").strip() or "????.??.??"
        round_str = current_tags.get("Round", "?").strip() or "?"
        result = normalize_result(current_tags.get("Result"))
        white_elo = normalize_elo(current_tags.get("WhiteElo"))
        black_elo = normalize_elo(current_tags.get("BlackElo"))
        eco = normalize_eco(current_tags.get("ECO"))

        fingerprint = compute_game_fingerprint(white, black, date, clean_moves)
        if deduplicate and fingerprint in seen_fingerprints:
            return None

        if deduplicate:
            seen_fingerprints.add(fingerprint)

        pgn_text = format_standard_pgn(
            event, site, date, round_str, white, black,
            result, white_elo, black_elo, eco, clean_moves
        )

        return CleanedGame(
            event=event,
            site=site,
            date=date,
            round_str=round_str,
            white=white,
            black=black,
            result=result,
            white_elo=white_elo,
            black_elo=black_elo,
            eco=eco,
            moves=clean_moves,
            pgn=pgn_text,
            fingerprint=fingerprint
        )

    for line in lines:
        line_str = line.strip()
        if not line_str:
            if in_moves and current_moves:
                # Potential end of game moves
                continue
            continue

        tag_match = TAG_REGEX.match(line_str)
        if tag_match:
            if in_moves:
                # New game starting, process previous
                game = build_game()
                if game:
                    yield game
                current_tags = {}
                current_moves = []
                in_moves = False

            current_tags[tag_match.group(1)] = tag_match.group(2)
        else:
            in_moves = True
            current_moves.append(line_str)

    # Process final game in file
    if current_tags or current_moves:
        game = build_game()
        if game:
            yield game
