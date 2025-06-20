"""Data module for ccusage command interaction."""

import json
import shutil
import subprocess


def check_ccusage_installed():
    """Check if ccusage is installed."""
    # Use shutil.which for more reliable command detection
    if shutil.which("ccusage"):
        return True

    # ccusage not found
    print("❌ 'ccusage' command not found!")
    print("\nThis tool requires 'ccusage' to be installed globally via npm.")
    print("\nTo install ccusage:")
    print("1. Install Node.js from https://nodejs.org/ (if not already installed)")
    print("2. Run: npm install -g ccusage")
    print("\nFor more information, visit: https://github.com/ryoppippi/ccusage")
    return False


def run_ccusage():
    """Execute ccusage blocks --json command and return parsed JSON data."""
    try:
        result = subprocess.run(
            ["ccusage", "blocks", "--offline", "--json"], capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout)
    except FileNotFoundError:
        print("❌ ccusage command not found. Please install it with: npm install -g ccusage")
        return None
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running ccusage: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        print("\nPossible solutions:")
        print("1. Make sure you're logged into Claude in your browser")
        print("2. Try running 'ccusage login' if authentication is required")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON from ccusage: {e}")
        return None


def get_token_limit(plan, blocks=None):
    """Get token limit based on plan type."""
    if plan == "custom_max" and blocks:
        # Find the highest token count from all previous blocks
        max_tokens = 0
        for block in blocks:
            if not block.get("isGap", False) and not block.get("isActive", False):
                tokens = block.get("totalTokens", 0)
                if tokens > max_tokens:
                    max_tokens = tokens
        # Return the highest found, or default to pro if none found
        return max_tokens if max_tokens > 0 else 7000

    limits = {"pro": 7000, "max5": 35000, "max20": 140000}
    return limits.get(plan, 7000)