#!/usr/bin/env python3
"""
Claude Code Usage Monitor - Entry point for backward compatibility.

This file exists to maintain backward compatibility with existing installations.
The main code has been refactored into the ccusage_monitor package.
"""

from ccusage_monitor.main import main

if __name__ == "__main__":
    main()
