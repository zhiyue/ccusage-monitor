#!/usr/bin/env python3
"""Check if package files with same hash already exist on PyPI."""

import sys
import json
import hashlib
import urllib.request
import urllib.error
import argparse
from pathlib import Path


def calculate_blake2_256(file_path):
    """Calculate BLAKE2-256 hash of a file."""
    h = hashlib.blake2b(digest_size=32)
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def get_package_files_info(package_name, version, test_pypi=False):
    """Get file information for a specific version from PyPI."""
    if test_pypi:
        base_url = f"https://test.pypi.org/pypi/{package_name}/{version}/json"
    else:
        base_url = f"https://pypi.org/pypi/{package_name}/{version}/json"
    
    try:
        with urllib.request.urlopen(base_url) as response:
            data = json.loads(response.read().decode())
            urls = data.get("urls", [])
            
            files_info = {}
            for file_info in urls:
                filename = file_info.get("filename")
                digests = file_info.get("digests", {})
                blake2_256 = digests.get("blake2b_256")
                if filename and blake2_256:
                    files_info[filename] = blake2_256
            
            return files_info
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Version doesn't exist
            return {}
        raise
    except Exception as e:
        print(f"Error checking PyPI: {e}", file=sys.stderr)
        return {}


def check_files_exist(dist_dir, package_name, version, test_pypi=False):
    """Check if built files already exist on PyPI with same hash."""
    pypi_files = get_package_files_info(package_name, version, test_pypi)
    
    if not pypi_files:
        return False, []
    
    dist_path = Path(dist_dir)
    duplicate_files = []
    
    for file_path in dist_path.glob("*"):
        if file_path.is_file():
            filename = file_path.name
            local_hash = calculate_blake2_256(file_path)
            
            if filename in pypi_files and pypi_files[filename] == local_hash:
                duplicate_files.append({
                    'filename': filename,
                    'hash': local_hash
                })
    
    return len(duplicate_files) > 0, duplicate_files


def main():
    parser = argparse.ArgumentParser(description="Check if package files already exist on PyPI")
    parser.add_argument("--package", default="ccusage-monitor", help="Package name")
    parser.add_argument("--version", required=True, help="Package version")
    parser.add_argument("--dist-dir", default="dist", help="Distribution directory")
    parser.add_argument("--test-pypi", action="store_true", help="Check Test PyPI")
    
    args = parser.parse_args()
    
    pypi_name = "Test PyPI" if args.test_pypi else "PyPI"
    
    # Check if files exist
    exists, duplicate_files = check_files_exist(
        args.dist_dir, args.package, args.version, args.test_pypi
    )
    
    if exists:
        print(f"❌ Files already exist on {pypi_name} with same hash:")
        for file_info in duplicate_files:
            print(f"  - {file_info['filename']} (blake2_256: {file_info['hash'][:16]}...)")
        print("\nNo need to publish - files are identical to existing ones.")
        sys.exit(1)
    else:
        print(f"✅ Files can be published to {pypi_name}")
        
        # List files that will be uploaded
        dist_path = Path(args.dist_dir)
        print(f"\nFiles to upload:")
        for file_path in dist_path.glob("*"):
            if file_path.is_file():
                print(f"  - {file_path.name}")
        
        sys.exit(0)


if __name__ == "__main__":
    main()