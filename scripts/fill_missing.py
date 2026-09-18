#!/usr/bin/env python3
"""
Arcana Chess Data Cloud - Fill Missing Issues Tool
Identifies any skipped/failed TWIC issues between start and end,
and retries downloading and ingesting only those gaps until 100% complete.
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crawler.twic_downloader import download_twic_zip
from src.database.master_builder import MasterDatabase
from scripts.bootstrap_historical import process_zip_issue


def fill_missing(db_path: str = "data/arcana_twic_master.db", start: int = 920, end: int = 1661, delay: float = 0.5):
    db = MasterDatabase(db_path=db_path)
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT issue FROM processed_issues WHERE issue BETWEEN ? AND ?", (start, end))
    present = {r[0] for r in cur.fetchall()}
    conn.close()

    missing = [i for i in range(start, end + 1) if i not in present]
    if not missing:
        print(f"🎉 Perfect! No missing issues found between {start} and {end}.")
        return

    print(f"🔍 Found {len(missing)} missing issues to retrieve: {missing}")

    recovered = 0
    for issue in missing:
        print(f"🔄 Retrying missing TWIC issue #{issue}...")
        try:
            zip_path = download_twic_zip(issue, dest_dir="data/raw_zips", delay_seconds=delay, force=True)
            added = process_zip_issue(db, zip_path, issue)
            if added > 0:
                recovered += 1
        except Exception as e:
            print(f"   ⚠️ Could not recover issue #{issue}: {e}")
            time.sleep(delay * 2)

    stats = db.get_stats()
    print(f"\n✨ Gap recovery finished! Successfully recovered {recovered}/{len(missing)} issues.")
    print(f"📊 Total Games in Master DB: {stats['total_games']:,}")


def main():
    parser = argparse.ArgumentParser(description="Fill missing TWIC issues")
    parser.add_argument("--db", type=str, default="data/arcana_twic_master.db")
    parser.add_argument("--start", type=int, default=920)
    parser.add_argument("--end", type=int, default=1661)
    parser.add_argument("--delay", type=float, default=0.5)

    args = parser.parse_args()
    fill_missing(args.db, args.start, args.end, args.delay)


if __name__ == "__main__":
    main()
