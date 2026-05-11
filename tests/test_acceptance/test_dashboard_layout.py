import sys

from PySide6.QtWidgets import QApplication

from snmp_monitor.gui.app import MainWindow
from snmp_monitor.gui.views import DashboardWidget


def _app():
    return QApplication.instance() or QApplication(sys.argv)


def test_dashboard_widget_declares_readable_minimum_height(qapp):
    widget = DashboardWidget()

    assert widget.minimumHeight() >= 360
    assert widget._canvas.minimumHeight() >= 360


def test_main_window_keeps_dashboard_readable_at_default_size(qapp):
    window = MainWindow()

    try:
        window.show()
        qapp.processEvents()

        assert window._dashboard_widget.height() >= 360
        assert window._dashboard_widget._canvas.height() >= 360
    finally:
        window.close()
