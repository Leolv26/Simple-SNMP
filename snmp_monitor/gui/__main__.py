"""GUI module entry point for SNMP Monitor.

This module serves as the entry point for the GUI application.
It can be run with: python -m snmp_monitor.gui
"""

import sys
import logging

import matplotlib
# Configure matplotlib to use available fonts instead of DejaVu Sans
# Must be set before any matplotlib imports
# Use fonts that support Chinese characters
# Priority: WenQuanYi > SimSun > Microsoft YaHei > Arial > Helvetica
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei', 'SimSun', 'Microsoft YaHei', 'Arial', 'Helvetica', 'sans-serif']

from PySide6.QtWidgets import QApplication

from snmp_monitor.gui.app import MainWindow


def _configure_logging():
    """Configure logging for the GUI application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Initialize and run the GUI application."""
    try:
        _configure_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting SNMP Monitor GUI")

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        window = MainWindow()
        window.show()
        logger.info("GUI window displayed")
        return app.exec()
    except Exception as e:
        logging.error(f"Failed to start GUI application: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
