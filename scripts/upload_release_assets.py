#!/usr/bin/env python3
"""
Uploads compiled master assets to GitHub Release via REST API.
"""

import os
import ssl
import sys
import time
import urllib.request
import urllib.error
import json
from pathlib import Path

TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or ""
REPO = "orlsm87/arcana-chess-data"
TAG = "v1662"

ctx = ssl._create_unverified_context()

def get_release():
    url = f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "ArcanaUploader"
    })
    with urllib.request.urlopen(req, context=ctx) as res:
        return json.load(res)

def delete_asset(asset_id, name):
    print(f"Deleting existing release asset: {name} (id: {asset_id})...")
    url = f"https://api.github.com/repos/{REPO}/releases/assets/{asset_id}"
    req = urllib.request.Request(url, method="DELETE", headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "ArcanaUploader"
    })
    try:
        with urllib.request.urlopen(req, context=ctx) as res:
            pass
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise

def upload_asset(release_id, file_path):
    path = Path(file_path)
    file_size = os.path.getsize(path)
    filename = path.name
    print(f"\nUploading {filename} ({file_size / (1024*1024):.1f} MB)...")

    upload_url = f"https://uploads.github.com/repos/{REPO}/releases/{release_id}/assets?name={filename}"

    # Use curl for reliable large file streaming with progress
    import subprocess
    cmd = [
        "curl",
        "-L",
        "-X", "POST",
        "-H", f"Authorization: Bearer {TOKEN}",
        "-H", "Content-Type: application/octet-stream",
        "-H", f"Content-Length: {file_size}",
        "--data-binary", f"@{path}",
        "--progress-bar",
        upload_url
    ]

    t0 = time.time()
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"✅ {filename} uploaded successfully in {time.time() - t0:.1f}s!")
    else:
        print(f"❌ Upload failed: {res.stderr}")
        sys.exit(1)

def main():
    rel = get_release()
    rel_id = rel["id"]
    existing_assets = {a["name"]: a["id"] for a in rel["assets"]}

    files_to_upload = [
        "dist/arcana_twic_master.db.zst",
        "dist/arcana_twic_master.pgn.zip",
        "dist/twic_1662.zip",
        "manifest.json"
    ]

    for f in files_to_upload:
        fname = Path(f).name
        if fname in existing_assets:
            delete_asset(existing_assets[fname], fname)
        upload_asset(rel_id, f)

    print("\n🎉 ALL ASSETS SUCCESSFULLY UPLOADED TO GITHUB RELEASE v1662!")

if __name__ == "__main__":
    main()
