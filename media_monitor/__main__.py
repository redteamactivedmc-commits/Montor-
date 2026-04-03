"""
__main__.py
-----------
Entry point for running media_monitor as a module: python -m media_monitor
"""

import sys
from media_monitor.cli import main

if __name__ == "__main__":
    sys.exit(main())
