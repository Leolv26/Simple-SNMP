import sys
from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication

from snmp_monitor.gui.app import MainWindow
from snmp_monitor.gui.workers.snmp_worker import SNMPWorker


def _app():
    return QApplication.instance() or QApplication(sys.argv)


def _table_rows(table_widget):
    rows = []
    for row in range(table_widget.rowCount()):
        rows.append([
            table_widget.item(row, column).text() if table_widget.item(row, column) else ""
            for column in range(table_widget.columnCount())
        ])
    return rows


def test_oid_query_result_creates_visible_table_row_when_oid_was_not_preloaded(qapp):
    window = MainWindow()
    oid = "1.3.6.1.2.1.1.1.0"
    snmp_result = ((1, 3, 6, 1, 2, 1, 1, 1, 0), "SNMP Agent")

    try:
        window._on_oid_query_result(oid, snmp_result)
        qapp.processEvents()

        rows = _table_rows(window._data_table_widget.table_widget)
        assert rows == [[oid, "OID Query Result", "SNMP Agent", ""]]
    finally:
        window.close()


def test_oid_query_signal_flow_displays_realistic_worker_get_result(qapp, monkeypatch):
    window = MainWindow()
    oid = "1.3.6.1.2.1.1.1.0"
    snmp_result = ((1, 3, 6, 1, 2, 1, 1, 1, 0), "Linux test host")

    worker = SNMPWorker("127.0.0.1", port=1161, poll_interval=10, timeout=0.1, retries=0)
    worker.client.get = MagicMock(return_value=snmp_result)
    worker.oid_query_result.connect(window._on_oid_query_result)
    window._snmp_worker = worker

    try:
        window._data_table_widget._oid_input.setText(oid)
        window._data_table_widget._on_search_clicked()
        qapp.processEvents()

        rows = _table_rows(window._data_table_widget.table_widget)
        assert rows == [[oid, "OID Query Result", "Linux test host", ""]]
        worker.client.get.assert_called_once_with((1, 3, 6, 1, 2, 1, 1, 1, 0))
    finally:
        worker.stop()
        window.close()
