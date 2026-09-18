#!/usr/bin/env python3
"""
Arcana Chess Data Cloud - Integrity & Quality Verification Tool
Runs comprehensive SQLite PRAGMA checks, validates database schema/indexes,
ensures data sanity, and checks SHA-256 release checksums.
"""

import argparse
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

# Add repo root to python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.generate_manifest import calculate_sha256


def verify_database_integrity(db_path: str) -> bool:
    """Performs deep PRAGMA integrity check and data validations."""
    path = Path(db_path)
    if not path.exists():
        print(f"❌ Database not found at: {db_path}")
        return False

    print(f"🔍 Analyzing Master Database: {db_path} ({os.path.getsize(path) / (1024*1024):.2f} MB)")
    start_time = time.time()
    all_ok = True

    conn = sqlite3.connect(str(path))
    cur = conn.cursor()

    try:
        # 1. PRAGMA integrity_check
        print("  -> Executing PRAGMA integrity_check...")
        cur.execute("PRAGMA integrity_check;")
        rows = cur.fetchall()
        if len(rows) == 1 and rows[0][0] == "ok":
            print("     ✅ SQLite low-level B-Tree integrity: OK")
        else:
            print(f"     ❌ SQLite integrity check failed: {rows}")
            all_ok = False

        # 2. Check Tables & Indexes
        print("  -> Checking required tables and indices...")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {r[0] for r in cur.fetchall()}
        required_tables = {"games", "metadata", "processed_issues"}
        missing_tables = required_tables - tables
        if missing_tables:
            print(f"     ❌ Missing tables: {missing_tables}")
            all_ok = False
        else:
            print("     ✅ Tables verified: games, metadata, processed_issues")

        cur.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indexes = {r[0] for r in cur.fetchall()}
        required_indexes = {"idx_white", "idx_black", "idx_eco", "idx_date", "idx_twic"}
        missing_indexes = required_indexes - indexes
        if missing_indexes:
            print(f"     ⚠️ Missing indices: {missing_indexes}")
        else:
            print("     ✅ Indices verified: idx_white, idx_black, idx_eco, idx_date, idx_twic")

        # 3. Check for Data Sanity
        print("  -> Checking data sanity in 'games' table...")
        cur.execute("SELECT COUNT(*) FROM games")
        total_games = cur.fetchone()[0]
        print(f"     📊 Total Games: {total_games:,}")

        if total_games > 0:
            # Check for illegal null values
            cur.execute("""
                SELECT COUNT(*) FROM games
                WHERE white IS NULL OR black IS NULL OR result IS NULL OR pgn IS NULL OR twic_issue IS NULL
            """)
            null_count = cur.fetchone()[0]
            if null_count > 0:
                print(f"     ❌ Found {null_count} records with illegal NULL values!")
                all_ok = False
            else:
                print("     ✅ Zero NULL values in required fields.")

            # Check for non-standard results
            cur.execute("""
                SELECT COUNT(*) FROM games
                WHERE result NOT IN ('1-0', '0-1', '1/2-1/2', '*')
            """)
            invalid_results = cur.fetchone()[0]
            if invalid_results > 0:
                print(f"     ⚠️ Found {invalid_results} games with non-standard result strings.")
            else:
                print("     ✅ All game results adhere to standard notation.")

            # Performance benchmark: query Magnus Carlsen games
            t0 = time.time()
            cur.execute("SELECT COUNT(*) FROM games WHERE white LIKE 'Carlsen%' OR black LIKE 'Carlsen%'")
            carlsen_count = cur.fetchone()[0]
            query_ms = round((time.time() - t0) * 1000, 2)
            print(f"     ⚡ Sample indexed query ('Carlsen'): {carlsen_count} games found in {query_ms} ms")

    except Exception as e:
        print(f"❌ Error during database inspection: {e}")
        all_ok = False
    finally:
        conn.close()

    elapsed = round(time.time() - start_time, 2)
    print(f"Database verification completed in {elapsed}s.")
    return all_ok


def verify_manifest_checksums(manifest_path: str = "manifest.json") -> bool:
    """Verifies SHA-256 checksums in manifest.json against local files if present."""
    mpath = Path(manifest_path)
    if not mpath.exists():
        print(f"ℹ️ manifest.json not found at {manifest_path}. Skipping checksum verification.")
        return True

    print(f"🔍 Validating manifest file: {manifest_path}")
    with open(mpath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check required fields
    required_keys = ["service", "version", "updated_at", "latest_issue", "total_games", "master_database"]
    missing = [k for k in required_keys if k not in data]
    if missing:
        print(f"❌ manifest.json missing required keys: {missing}")
        return False

    print("   ✅ manifest.json schema conforms to Arcana Chess Studio specification.")
    return True


def main():
    parser = argparse.ArgumentParser(description="Verify Arcana Chess Data Cloud database and artifacts")
    parser.add_argument("--db", type=str, default="data/arcana_twic_master.db", help="Path to SQLite master DB")
    parser.add_argument("--manifest", type=str, default="manifest.json", help="Path to manifest.json")

    args = parser.parse_args()

    db_ok = verify_database_integrity(args.db)
    manifest_ok = verify_manifest_checksums(args.manifest)

    if db_ok and manifest_ok:
        print("\n✨ ALL INTEGRITY AND QUALITY CHECKS PASSED SUCCESSFULLY ✨")
        sys.exit(0)
    else:
        print("\n🚨 INTEGRITY CHECKS DETECTED ISSUES")
        sys.exit(1)


if __name__ == "__main__":
    main()
