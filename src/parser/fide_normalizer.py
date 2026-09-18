"""
Arcana Chess Data Cloud - FIDE Player & Rating Normalizer
Standardizes chess player names, handles alias variations (e.g. "Carlsen, M." -> "Carlsen, Magnus"),
strips extraneous title tags, and normalizes Elo ratings.
"""

import re
from typing import Optional, Tuple


# Known Grandmaster Aliases and abbreviations mapping
PLAYER_CANONICAL_MAP = {
    # Top Historical & Contemporary GMs
    "carlsen, m": "Carlsen, Magnus",
    "carlsen, m.": "Carlsen, Magnus",
    "carlsen, magnus": "Carlsen, Magnus",
    "kasparov, g": "Kasparov, Garry",
    "kasparov, g.": "Kasparov, Garry",
    "kasparov, garry": "Kasparov, Garry",
    "karpov, a": "Karpov, Anatoly",
    "karpov, a.": "Karpov, Anatoly",
    "karpov, anatoly": "Karpov, Anatoly",
    "fischer, r": "Fischer, Robert J.",
    "fischer, r.": "Fischer, Robert J.",
    "fischer, robert j": "Fischer, Robert J.",
    "fischer, robert j.": "Fischer, Robert J.",
    "fischer, bobby": "Fischer, Robert J.",
    "caruana, f": "Caruana, Fabiano",
    "caruana, f.": "Caruana, Fabiano",
    "caruana, fabiano": "Caruana, Fabiano",
    "nakamura, h": "Nakamura, Hikaru",
    "nakamura, h.": "Nakamura, Hikaru",
    "nakamura, hikaru": "Nakamura, Hikaru",
    "anand, v": "Anand, Viswanathan",
    "anand, v.": "Anand, Viswanathan",
    "anand, viswanathan": "Anand, Viswanathan",
    "kramnik, v": "Kramnik, Vladimir",
    "kramnik, v.": "Kramnik, Vladimir",
    "kramnik, vladimir": "Kramnik, Vladimir",
    "ding, l": "Ding, Liren",
    "ding, l.": "Ding, Liren",
    "ding, liren": "Ding, Liren",
    "gukesh, d": "Gukesh, D",
    "gukesh, d.": "Gukesh, D",
    "gukesh, dommaraju": "Gukesh, D",
    "firouzja, a": "Firouzja, Alireza",
    "firouzja, a.": "Firouzja, Alireza",
    "firouzja, alireza": "Firouzja, Alireza",
    "nepomniachtchi, i": "Nepomniachtchi, Ian",
    "nepomniachtchi, i.": "Nepomniachtchi, Ian",
    "nepomniachtchi, ian": "Nepomniachtchi, Ian",
    "aronian, l": "Aronian, Levon",
    "aronian, l.": "Aronian, Levon",
    "aronian, levon": "Aronian, Levon",
    "so, w": "So, Wesley",
    "so, w.": "So, Wesley",
    "so, wesley": "So, Wesley",
    "giri, a": "Giri, Anish",
    "giri, a.": "Giri, Anish",
    "giri, anish": "Giri, Anish",
    "erigaisi, a": "Erigaisi, Arjun",
    "erigaisi, a.": "Erigaisi, Arjun",
    "erigaisi, arjun": "Erigaisi, Arjun",
    "praggnanandhaa, r": "Praggnanandhaa, R",
    "praggnanandhaa, r.": "Praggnanandhaa, R",
    "praggnanandhaa, rameshbabu": "Praggnanandhaa, R",
    "vachier-lagrave, m": "Vachier-Lagrave, Maxime",
    "vachier-lagrave, m.": "Vachier-Lagrave, Maxime",
    "vachier-lagrave, maxime": "Vachier-Lagrave, Maxime",
    "vachier lagrave, m": "Vachier-Lagrave, Maxime",
    "vachier lagrave, m.": "Vachier-Lagrave, Maxime",
    "vachier lagrave, maxime": "Vachier-Lagrave, Maxime",
    "mamedyarov, s": "Mamedyarov, Shakhriyar",
    "mamedyarov, s.": "Mamedyarov, Shakhriyar",
    "mamedyarov, shakhriyar": "Mamedyarov, Shakhriyar",
    "grischuk, a": "Grischuk, Alexander",
    "grischuk, a.": "Grischuk, Alexander",
    "grischuk, alexander": "Grischuk, Alexander",
    "topalov, v": "Topalov, Veselin",
    "topalov, v.": "Topalov, Veselin",
    "topalov, veselin": "Topalov, Veselin",
    "ivanchuk, v": "Ivanchuk, Vassily",
    "ivanchuk, v.": "Ivanchuk, Vassily",
    "ivanchuk, vassily": "Ivanchuk, Vassily",
    "shiroov, a": "Shirov, Alexei",
    "shirov, a": "Shirov, Alexei",
    "shirov, a.": "Shirov, Alexei",
    "shirov, alexei": "Shirov, Alexei",
    "svidler, p": "Svidler, Peter",
    "svidler, p.": "Svidler, Peter",
    "svidler, peter": "Svidler, Peter",
    "morozevich, a": "Morozevich, Alexander",
    "morozevich, a.": "Morozevich, Alexander",
    "morozevich, alexander": "Morozevich, Alexander",
    "leko, p": "Leko, Peter",
    "leko, p.": "Leko, Peter",
    "leko, peter": "Leko, Peter",
    "radjabov, t": "Radjabov, Teimour",
    "radjabov, t.": "Radjabov, Teimour",
    "radjabov, teimour": "Radjabov, Teimour",
    "karjakin, s": "Karjakin, Sergey",
    "karjakin, s.": "Karjakin, Sergey",
    "karjakin, sergey": "Karjakin, Sergey",
    "keymer, v": "Keymer, Vincent",
    "keymer, v.": "Keymer, Vincent",
    "keymer, vincent": "Keymer, Vincent",
    "abdusattorov, n": "Abdusattorov, Nodirbek",
    "abdusattorov, n.": "Abdusattorov, Nodirbek",
    "abdusattorov, nodirbek": "Abdusattorov, Nodirbek",
    "polgar, j": "Polgar, Judit",
    "polgar, j.": "Polgar, Judit",
    "polgar, judit": "Polgar, Judit",
    "hou, y": "Hou, Yifan",
    "hou, y.": "Hou, Yifan",
    "hou, yifan": "Hou, Yifan",
    "ju, w": "Ju, Wenjun",
    "ju, w.": "Ju, Wenjun",
    "ju, wenjun": "Ju, Wenjun",
}

# Regex to strip chess titles like GM, IM, FM, WGM, WIM, WFM, CM, WCM
TITLES_REGEX = re.compile(r"\b(GM|WGM|IM|WIM|FM|WFM|CM|WCM)\b", re.IGNORECASE)

# Lowercase particles that should stay lowercase unless at the start
PARTICLES = {"van", "von", "de", "der", "den", "la", "le", "da", "di", "del", "della", "du"}


def title_case_name(name: str) -> str:
    """
    Intelligently capitalizes a name component, keeping hyphenated names
    and specific particles formatted properly.
    """
    tokens = name.split()
    formatted_tokens = []
    for i, token in enumerate(tokens):
        # Handle hyphenated parts (e.g. Vachier-Lagrave, Saint-Amant)
        subparts = token.split("-")
        formatted_subparts = []
        for j, sub in enumerate(subparts):
            sub_clean = sub.strip()
            if not sub_clean:
                continue
            lower_sub = sub_clean.lower()
            if lower_sub in PARTICLES and (i > 0 or j > 0):
                formatted_subparts.append(lower_sub)
            else:
                # Handle initials like 'A.' or 'M.'
                if len(sub_clean) == 1 or (len(sub_clean) == 2 and sub_clean.endswith(".")):
                    formatted_subparts.append(sub_clean.upper())
                else:
                    formatted_subparts.append(sub_clean.capitalize())
        formatted_tokens.append("-".join(formatted_subparts))
    return " ".join(formatted_tokens)


def normalize_player_name(raw_name: Optional[str]) -> str:
    """
    Standardizes a chess player name into canonical 'Lastname, Firstname' format.
    Strips titles, resolves common Grandmaster aliases, and trims punctuation.
    """
    if not raw_name:
        return "Unknown"

    # Remove enclosing quotes, leading/trailing whitespace
    name = raw_name.strip().strip('"').strip("'")
    if not name or name in ("?", "-", "Unknown", "NN", "n.n."):
        return "Unknown"

    # Strip title acronyms like 'GM Carlsen, Magnus' or 'Carlsen, Magnus GM'
    name = TITLES_REGEX.sub("", name).strip()

    # Collapse multiple spaces
    name = re.sub(r"\s+", " ", name).strip()

    # Check against known canonical aliases (case-insensitive)
    lookup_key = name.lower().rstrip(".")
    if lookup_key in PLAYER_CANONICAL_MAP:
        return PLAYER_CANONICAL_MAP[lookup_key]
    if name.lower() in PLAYER_CANONICAL_MAP:
        return PLAYER_CANONICAL_MAP[name.lower()]

    # Format 'Lastname, Firstname' if comma exists
    if "," in name:
        parts = name.split(",", 1)
        last = title_case_name(parts[0].strip())
        first = title_case_name(parts[1].strip())
        normalized = f"{last}, {first}".strip()
        # Clean double commas or trailing commas
        normalized = re.sub(r",\s*$", "", normalized)
    else:
        # Single name without comma (e.g. 'Garry Kasparov' or mononym)
        tokens = name.split()
        if len(tokens) >= 2:
            # Assume 'First Last' -> convert to 'Last, First'
            last = title_case_name(tokens[-1])
            first = title_case_name(" ".join(tokens[:-1]))
            normalized = f"{last}, {first}"
        else:
            normalized = title_case_name(name)

    # Final check on normalized name
    lookup_clean = normalized.lower()
    if lookup_clean in PLAYER_CANONICAL_MAP:
        return PLAYER_CANONICAL_MAP[lookup_clean]

    return normalized


def normalize_elo(raw_elo: Optional[str]) -> Optional[int]:
    """
    Converts and validates an Elo rating string into an integer.
    Returns None if missing, unrated, or out of reasonable bounds.
    """
    if not raw_elo:
        return None

    cleaned = str(raw_elo).strip().replace(".0", "")
    match = re.search(r"\b(\d{3,4})\b", cleaned)
    if not match:
        return None

    try:
        elo = int(match.group(1))
        # Valid competitive Elo range
        if 800 <= elo <= 3300:
            return elo
        return None
    except (ValueError, TypeError):
        return None
