"""
Arcana Chess Data Cloud - Respectful TWIC Crawler & Downloader
Automates respectful retrieval of The Week In Chess (TWIC) zip files,
rate-limiting requests, caching local archives, and extracting weekly PGNs.
"""

import os
import re
import ssl
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional

BASE_TWIC_ZIP_URL = "https://theweekinchess.com/zips/twic{issue}g.zip"
DOWNLOADS_PAGE_URL = "https://theweekinchess.com/twic-downloads"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 (ArcanaDataBot/1.0)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/zip,*/*;q=0.8",
    "Referer": "https://theweekinchess.com/twic-downloads",
    "Connection": "keep-alive"
}


def _create_ssl_context() -> ssl.SSLContext:
    """Creates a resilient SSL context, handling unverified certificates if needed."""
    try:
        ctx = ssl.create_default_context()
        return ctx
    except Exception:
        return ssl._create_unverified_context()


def download_twic_zip(
    issue: int,
    dest_dir: str = "data/raw_zips",
    delay_seconds: float = 1.0,
    force: bool = False
) -> Path:
    """
    Respectfully downloads a TWIC issue zip archive (twic{N}g.zip).
    Uses local cache if already present to avoid hitting TWIC servers.
    """
    dest_path = Path(dest_dir)
    dest_path.mkdir(parents=True, exist_ok=True)
    zip_target = dest_path / f"twic{issue}g.zip"

    if zip_target.exists() and not force:
        try:
            with zipfile.ZipFile(zip_target, "r") as zf:
                if zf.testzip() is None:
                    # Valid cached zip
                    return zip_target
        except zipfile.BadZipFile:
            zip_target.unlink(missing_ok=True)

    url = BASE_TWIC_ZIP_URL.format(issue=issue)
    req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
    ctx = _create_ssl_context()

    # Polite delay before network request
    if delay_seconds > 0:
        time.sleep(delay_seconds)

    max_retries = 3
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
                content = response.read()

            with open(zip_target, "wb") as f:
                f.write(content)

            # Verify it's a valid zip
            with zipfile.ZipFile(zip_target, "r") as zf:
                if zf.testzip() is not None:
                    raise zipfile.BadZipFile("Corrupted zip downloaded")

            return zip_target
        except (urllib.error.HTTPError, urllib.error.URLError, zipfile.BadZipFile, TimeoutError) as e:
            last_error = e
            if zip_target.exists():
                zip_target.unlink(missing_ok=True)
            time.sleep(2.0 * attempt)

    raise RuntimeError(f"Failed to download TWIC issue {issue} from {url}: {last_error}")


def extract_pgn_from_zip(zip_path: Path, extract_dir: str = "data/extracted_pgns") -> Path:
    """
    Extracts the .pgn file from a TWIC zip archive.
    Returns the path to the extracted .pgn file.
    """
    out_dir = Path(extract_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        pgn_files = [name for name in zf.namelist() if name.lower().endswith(".pgn")]
        if not pgn_files:
            raise ValueError(f"No PGN file found inside {zip_path.name}")

        pgn_filename = pgn_files[0]
        extracted_path = zf.extract(pgn_filename, out_dir)
        return Path(extracted_path)


def get_latest_twic_issue(start_probe: int = 1660) -> int:
    """
    Detects the latest published TWIC issue.
    First tries parsing the downloads index page; falls back to probe verification.
    """
    ctx = _create_ssl_context()
    req = urllib.request.Request(DOWNLOADS_PAGE_URL, headers=DEFAULT_HEADERS)

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
            html = res.read().decode("utf-8", errors="ignore")
            # Find all twic{N}g.zip patterns
            matches = re.findall(r"twic(\d{3,4})g\.zip", html, re.IGNORECASE)
            if matches:
                return max(int(m) for m in matches)
    except Exception:
        pass

    # Fallback: probe consecutive issues
    current = start_probe
    latest_found = current
    while True:
        url = BASE_TWIC_ZIP_URL.format(issue=current)
        probe_req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
        try:
            with urllib.request.urlopen(probe_req, context=ctx, timeout=10) as probe_res:
                if probe_res.status == 200:
                    latest_found = current
                    current += 1
                    time.sleep(0.5)
                else:
                    break
        except Exception:
            break

    return latest_found
