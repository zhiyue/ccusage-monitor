#!/usr/bin/env python3
"""Check if a version already exists on PyPI or Test PyPI."""

import argparse
import json
import sys
import urllib.error
import urllib.request


def check_version_exists(package_name, version, test_pypi=False):
    """Check if a specific version of a package exists on PyPI."""
    if test_pypi:
        base_url = f"https://test.pypi.org/pypi/{package_name}/json"
    else:
        base_url = f"https://pypi.org/pypi/{package_name}/json"

    try:
        with urllib.request.urlopen(base_url) as response:
            data = json.loads(response.read().decode())
            releases = data.get("releases", {})
            return version in releases
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Package doesn't exist yet
            return False
        raise
    except Exception as e:
        print(f"Error checking PyPI: {e}", file=sys.stderr)
        return False


def get_latest_version(package_name, test_pypi=False):
    """Get the latest version of a package from PyPI."""
    if test_pypi:
        base_url = f"https://test.pypi.org/pypi/{package_name}/json"
    else:
        base_url = f"https://pypi.org/pypi/{package_name}/json"

    try:
        with urllib.request.urlopen(base_url) as response:
            data = json.loads(response.read().decode())
            info = data.get("info", {})
            return info.get("version", "0.0.0")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "0.0.0"
        raise


def main():
    parser = argparse.ArgumentParser(description="Check PyPI version existence")
    parser.add_argument("--package", default="ccusage-monitor", help="Package name")
    parser.add_argument("--version", required=True, help="Version to check")
    parser.add_argument("--test-pypi", action="store_true", help="Check Test PyPI")

    args = parser.parse_args()

    exists = check_version_exists(args.package, args.version, args.test_pypi)
    latest = get_latest_version(args.package, args.test_pypi)

    pypi_name = "Test PyPI" if args.test_pypi else "PyPI"

    if exists:
        print(f"Version {args.version} already exists on {pypi_name}")
        sys.exit(1)
    else:
        print(f"Version {args.version} does not exist on {pypi_name}")
        print(f"Latest version on {pypi_name}: {latest}")
        sys.exit(0)


if __name__ == "__main__":
    main()
