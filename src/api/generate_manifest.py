"""
Arcana Chess Data Cloud - Manifest & API Generator
Calculates SHA-256 checksums, compiles database metrics, and exports
the static manifest.json specification for Arcana Chess Studio and community CDNs.
"""

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Optional


def calculate_sha256(file_path: str) -> str:
    """Calculates SHA-256 checksum of a file using streaming chunks."""
    path = Path(file_path)
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def get_file_size_mb(file_path: str) -> float:
    """Returns file size in megabytes rounded to 1 decimal place."""
    path = Path(file_path)
    if not path.exists():
        return 0.0
    return round(os.path.getsize(path) / (1024 * 1024), 1)


def build_manifest_payload(
    latest_issue: int,
    total_games: int,
    repo_owner: str = "orlsm87",
    repo_name: str = "arcana-chess-data",
    db_file: Optional[str] = None,
    pgn_zip_file: Optional[str] = None,
    delta_zip_file: Optional[str] = None,
    delta_games_count: int = 0,
    issue_date: Optional[str] = None
) -> Dict:
    """Constructs the canonical Arcana Chess Data Cloud manifest dictionary."""
    now = datetime.datetime.now(datetime.timezone.utc)
    updated_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    issue_date_str = issue_date or now.strftime("%Y-%m-%d")

    base_release_url = f"https://github.com/{repo_owner}/{repo_name}/releases/download/v{latest_issue}"

    # Master DB info
    db_format = "sqlite3+zstd" if (db_file and db_file.endswith(".zst")) else "sqlite3+zip"
    db_filename = Path(db_file).name if db_file else f"arcana_twic_master.db.zst"
    db_size = get_file_size_mb(db_file) if db_file else 420.5
    db_sha256 = calculate_sha256(db_file) if db_file else ""

    # Master PGN info
    pgn_filename = Path(pgn_zip_file).name if pgn_zip_file else "arcana_twic_master.pgn.zip"
    pgn_size = get_file_size_mb(pgn_zip_file) if pgn_zip_file else 510.2
    pgn_sha256 = calculate_sha256(pgn_zip_file) if pgn_zip_file else ""

    # Delta info
    delta_filename = Path(delta_zip_file).name if delta_zip_file else f"twic_{latest_issue}.zip"

    manifest = {
        "service": "Arcana Chess Data Cloud",
        "version": "1.0",
        "updated_at": updated_at,
        "latest_issue": latest_issue,
        "latest_issue_date": issue_date_str,
        "total_games": total_games,
        "master_database": {
            "version_issue": latest_issue,
            "size_mb": db_size,
            "format": db_format,
            "download_url": f"{base_release_url}/{db_filename}",
            "sha256": db_sha256
        },
        "master_pgn": {
            "version_issue": latest_issue,
            "size_mb": pgn_size,
            "format": "pgn+zip",
            "download_url": f"{base_release_url}/{pgn_filename}",
            "sha256": pgn_sha256
        },
        "weekly_delta": {
            "issue": latest_issue,
            "games_count": delta_games_count,
            "download_url": f"{base_release_url}/{delta_filename}"
        }
    }
    return manifest


def write_manifest_files(
    manifest_data: Dict,
    output_paths: tuple = ("manifest.json", "web/manifest.json")
) -> None:
    """Writes the manifest data formatted as JSON to one or more paths."""
    json_content = json.dumps(manifest_data, indent=2, ensure_ascii=False) + "\n"
    for out_path in output_paths:
        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(json_content)


def main():
    parser = argparse.ArgumentParser(description="Generate manifest.json for Arcana Chess Data Cloud")
    parser.add_argument("--issue", type=int, required=True, help="Latest TWIC issue number")
    parser.add_argument("--total-games", type=int, required=True, help="Total games in SQLite database")
    parser.add_argument("--repo-owner", type=str, default=os.getenv("GITHUB_REPOSITORY_OWNER", "orlsm87"))
    parser.add_argument("--repo-name", type=str, default="arcana-chess-data")
    parser.add_argument("--db-file", type=str, default=None, help="Path to master DB archive")
    parser.add_argument("--pgn-zip", type=str, default=None, help="Path to master PGN zip")
    parser.add_argument("--delta-zip", type=str, default=None, help="Path to weekly delta zip")
    parser.add_argument("--delta-games", type=int, default=0, help="Number of games in weekly delta")
    parser.add_argument("--issue-date", type=str, default=None, help="Publication date YYYY-MM-DD")
    parser.add_argument("--out", type=str, nargs="+", default=["manifest.json", "web/manifest.json"])

    args = parser.parse_args()

    manifest = build_manifest_payload(
        latest_issue=args.issue,
        total_games=args.total_games,
        repo_owner=args.repo_owner,
        repo_name=args.repo_name,
        db_file=args.db_file,
        pgn_zip_file=args.pgn_zip,
        delta_zip_file=args.delta_zip,
        delta_games_count=args.delta_games,
        issue_date=args.issue_date
    )

    write_manifest_files(manifest, tuple(args.out))
    print(f"Generated manifest.json for issue {args.issue} ({args.total_games} total games)")


if __name__ == "__main__":
    main()
