import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from snmp_monitor.gui.app import MainWindow
from snmp_monitor.gui.workers.snmp_worker import SNMPWorker


def _app():
    return QApplication.instance() or QApplication(sys.argv)


def test_dashboard_appends_one_float_point_for_real_snmp_string_values(monkeypatch):
    app = _app()
    window = MainWindow()

    try:
        draw_calls = []
        monkeypatch.setattr(window._dashboard_widget._canvas, "draw", lambda: draw_calls.append(True))

        window._on_worker_data_ready({
            MainWindow.CPU_OID: "12",
            MainWindow.MEMORY_OID: "34",
        })
        app.processEvents()

        assert window._dashboard_widget.cpu_data == [12.0]
        assert window._dashboard_widget.memory_data == [34.0]
        assert all(isinstance(value, float) for value in window._dashboard_widget.cpu_data)
        assert all(isinstance(value, float) for value in window._dashboard_widget.memory_data)
        assert len(draw_calls) == 1
    finally:
        window.close()


def test_dashboard_updates_from_realistic_worker_poll_result(monkeypatch):
    app = _app()
    window = MainWindow()

    def fake_poll(self):
        return {
            MainWindow.CPU_OID: "21",
            MainWindow.MEMORY_OID: "43",
            MainWindow.DISK_OID: "9",
        }

    monkeypatch.setattr(SNMPWorker, "_poll", fake_poll)

    worker = SNMPWorker("127.0.0.1", port=1161, poll_interval=0.1, timeout=0.1, retries=0)
    worker.data_ready.connect(window._on_worker_data_ready)

    try:
        data = worker._poll()
        worker.data_ready.emit(data)
        app.processEvents()

        assert window._dashboard_widget.cpu_data == [21.0]
        assert window._dashboard_widget.memory_data == [43.0]
    finally:
        worker.stop()
        window.close()
