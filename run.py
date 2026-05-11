#!/usr/bin/env python3
"""Root entry point for launching the SNMP Monitor GUI.

Usage:
    python run.py
"""
import os
import sys
from pathlib import Path


def main() -> int:
    """Start the GUI application from the project root."""
    project_root = Path(__file__).resolve().parent
    os.chdir(project_root)

    from snmp_monitor.gui.__main__ import main as gui_main

    return int(gui_main())


if __name__ == "__main__":
    sys.exit(main())
