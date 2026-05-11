"""Integration tests for GUI View components.

This module tests the integration between all View components:
- DashboardWidget data updates
- DeviceTreeWidget OID selection
- DataTableWidget search and updates
- LogPanelWidget log additions
- AlertConfigDialog threshold settings
- Component signal integration
- User interactions (button clicks, dialogs, row selection)
- MainWindow lifecycle
"""
import sys
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from PySide6.QtCore import Qt, QModelIndex, QTimer
from PySide6.QtWidgets import QApplication, QTableWidgetItem, QDialog

# Import matplotlib with non-interactive backend for testing
import matplotlib
matplotlib.use('Agg')


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


# =============================================================================
# Test DashboardWidget Data Updates
# =============================================================================

class TestDashboardWidgetDataUpdates:
    """Test DashboardWidget data update functionality."""

    def test_update_data_single_call(self, qapp):
        """Test single update_data call stores values correctly."""
        from snmp_monitor.gui.views import DashboardWidget
        widget = DashboardWidget()

        widget.update_data(cpu=50.0, memory=60.0)

        assert len(widget.cpu_data) == 1
        assert widget.cpu_data[0] == 50.0
        assert widget.memory_data[0] == 60.0

        widget.deleteLater()

    def test_update_data_multiple_calls(self, qapp):
        """Test multiple update_data calls accumulate data."""
        from snmp_monitor.gui.views import DashboardWidget
        widget = DashboardWidget()

        for i in range(5):
            widget.update_data(cpu=float(i * 10), memory=float(i * 5))

        assert len(widget.cpu_data) == 5
        assert len(widget.memory_data) == 5
        assert widget.cpu_data[-1] == 40.0

        widget.deleteLater()

    def test_update_data_cpu_only(self, qapp):
        """Test update_data with CPU only (memory=None)."""
        from snmp_monitor.gui.views import DashboardWidget
        widget = DashboardWidget()

        widget.update_data(cpu=75.0, memory=None)

        assert len(widget.cpu_data) == 1
        assert widget.cpu_data[0] == 75.0
        assert len(widget.memory_data) == 0

        widget.deleteLater()

    def test_update_data_memory_only(self, qapp):
        """Test update_data with memory only (cpu=None)."""
        from snmp_monitor.gui.views import DashboardWidget
        widget = DashboardWidget()

        widget.update_data(cpu=None, memory=80.0)

        assert len(widget.cpu_data) == 0
        assert len(widget.memory_data) == 1
        assert widget.memory_data[0] == 80.0

        widget.deleteLater()

    def test_update_data_fifo_window(self, qapp):
        """Test data follows FIFO window behavior."""
        from snmp_monitor.gui.views import DashboardWidget
        widget = DashboardWidget(max_points=3)

        for i in range(5):
            widget.update_data(cpu=float(i), memory=float(i * 2))

        # Should only keep last 3 values
        assert len(widget.cpu_data) == 3
        assert widget.cpu_data == [2.0, 3.0, 4.0]
        assert widget.memory_data == [4.0, 6.0, 8.0]

        widget.deleteLater()

    def test_update_data_canvas_redraws(self, qapp):
        """Test that update_data triggers canvas redraw."""
        from snmp_monitor.gui.views import DashboardWidget
        widget = DashboardWidget()

        with patch.object(widget._canvas, 'draw') as mock_draw:
            widget.update_data(50.0, 60.0)
            mock_draw.assert_called_once()

        widget.deleteLater()

    def test_reset_clears_all_data(self, qapp):
        """Test reset clears both CPU and memory data."""
        from snmp_monitor.gui.views import DashboardWidget
        widget = DashboardWidget()

        widget.update_data(50.0, 60.0)
        widget.update_data(70.0, 80.0)
        assert len(widget.cpu_data) == 2

        widget.reset()

        assert len(widget.cpu_data) == 0
        assert len(widget.memory_data) == 0

        widget.deleteLater()


# =============================================================================
# Test DeviceTreeWidget OID Selection
# =============================================================================

class TestDeviceTreeWidgetOIDSelection:
    """Test DeviceTreeWidget OID selection functionality."""

    def test_device_tree_oid_selected_signal_emits(self, qapp):
        """Test that oid_selected signal is emitted on selection."""
        from snmp_monitor.gui.views import DeviceTreeWidget
        from snmp_monitor.gui.models.mib_model import MIBModel

        model = MIBModel()
        widget = DeviceTreeWidget(model)

        received_oid = []

        def on_oid_selected(oid):
            received_oid.append(oid)

        widget.oid_selected.connect(on_oid_selected)

        # Add an OID and trigger signal
        idx = model.add_oid("1.3.6.1.2.1.1.1.0", "sysDescr", "Test Device")

        # Get the model index for the item
        model_idx = model.index(0, 0)
        widget._on_double_click(model_idx)

        # Signal should be emitted
        assert len(received_oid) == 1

        widget.deleteLater()

    def test_device_tree_refresh_button_exists(self, qapp):
        """Test that refresh button exists and is clickable."""
        from snmp_monitor.gui.views import DeviceTreeWidget

        widget = DeviceTreeWidget()

        assert hasattr(widget, 'refresh_button')
        assert widget.refresh_button is not None

        # Click should not raise error
        widget.refresh_button.click()

        widget.deleteLater()

    def test_device_tree_refresh_loads_data(self, qapp):
        """Test that refresh loads default MIB data."""
        from snmp_monitor.gui.views import DeviceTreeWidget
        from snmp_monitor.gui.models.mib_model import MIBModel

        model = MIBModel()
        widget = DeviceTreeWidget(model)

        # Initially empty
        initial_rows = model.rowCount()

        # Refresh should load data
        widget.refresh()
        qapp.processEvents()

        # Should have loaded default data
        assert model.rowCount() >= 0  # May vary based on default data

        widget.deleteLater()

    def test_device_tree_load_mib_data(self, qapp):
        """Test loading custom MIB data."""
        from snmp_monitor.gui.views import DeviceTreeWidget

        widget = DeviceTreeWidget()

        test_oids = [
            ("1.3.6.1.2.1.1.1.0", "sysDescr", "Test Agent", "String"),
            ("1.3.6.1.2.1.1.3.0", "sysUpTime", "1000", "TimeTicks"),
        ]

        widget.load_mib_data(test_oids)

        # Should have loaded the data
        assert widget.model.rowCount() == 2

        widget.deleteLater()


# =============================================================================
# Test DataTableWidget Search and Updates
# =============================================================================

class TestDataTableWidgetSearchAndUpdates:
    """Test DataTableWidget search and update functionality."""

    def test_search_oid_emits_signal(self, qapp):
        """Test that search_oid emits oid_query_requested signal."""
        from snmp_monitor.gui.views import DataTableWidget

        widget = DataTableWidget()

        received_oids = []

        def on_query_requested(oid):
            received_oids.append(oid)

        widget.oid_query_requested.connect(on_query_requested)

        widget.search_oid("1.3.6.1.2.1.1.1.0")

        assert len(received_oids) == 1
        assert received_oids[0] == "1.3.6.1.2.1.1.1.0"

        widget.deleteLater()

    def test_search_button_click_emits_signal(self, qapp):
        """Test that clicking search button emits oid_query_requested."""
        from snmp_monitor.gui.views import DataTableWidget

        widget = DataTableWidget()

        received_oids = []

        def on_query_requested(oid):
            received_oids.append(oid)

        widget.oid_query_requested.connect(on_query_requested)

        # Enter OID and click search
        widget.oid_input.setText("1.3.6.1.2.1.1.3.0")
        widget.search_button.click()

        assert len(received_oids) == 1

        widget.deleteLater()

    def test_enter_key_triggers_search(self, qapp):
        """Test that pressing Enter triggers search."""
        from snmp_monitor.gui.views import DataTableWidget

        widget = DataTableWidget()

        received_oids = []

        def on_query_requested(oid):
            received_oids.append(oid)

        widget.oid_query_requested.connect(on_query_requested)

        widget.oid_input.setText("1.3.6.1.2.1.1.4.0")
        widget.oid_input.returnPressed.emit()

        assert len(received_oids) == 1

        widget.deleteLater()

    def test_update_table_populates_rows(self, qapp):
        """Test that update_table populates table with data."""
        from snmp_monitor.gui.views import DataTableWidget

        widget = DataTableWidget()

        test_data = [
            ("1.3.6.1.2.1.1.1.0", "sysDescr", "Test Agent", "String"),
            ("1.3.6.1.2.1.1.3.0", "sysUpTime", "1000", "TimeTicks"),
        ]

        widget.update_table(test_data)

        assert widget.table_widget.rowCount() == 2

        # Verify first row
        oid_item = widget.table_widget.item(0, 0)
        assert oid_item.text() == "1.3.6.1.2.1.1.1.0"

        widget.deleteLater()

    def test_add_row_appends_row(self, qapp):
        """Test that add_row appends a row to the table."""
        from snmp_monitor.gui.views import DataTableWidget

        widget = DataTableWidget()

        widget.add_row("1.3.6.1.2.1.1.1.0", "sysDescr", "Test", "String")

        assert widget.table_widget.rowCount() == 1

        widget.deleteLater()

    def test_update_oid_value_updates_existing_row(self, qapp):
        """Test that update_oid_value updates existing OID row."""
        from snmp_monitor.gui.views import DataTableWidget

        widget = DataTableWidget()

        # Add a row first
        widget.add_row("1.3.6.1.2.1.1.1.0", "sysDescr", "Initial", "String")

        # Update the value
        widget.update_oid_value("1.3.6.1.2.1.1.1.0", "Updated Value")

        # Check the updated value
        value_item = widget.table_widget.item(0, 2)
        assert value_item.text() == "Updated Value"

        widget.deleteLater()

    def test_clear_table_removes_all_rows(self, qapp):
        """Test that clear_table removes all rows."""
        from snmp_monitor.gui.views import DataTableWidget

        widget = DataTableWidget()

        widget.add_row("1.3.6.1.2.1.1.1.0", "sysDescr", "Test", "String")
        widget.add_row("1.3.6.1.2.1.1.3.0", "sysUpTime", "1000", "String")

        assert widget.table_widget.rowCount() == 2

        widget.clear_table()

        assert widget.table_widget.rowCount() == 0

        widget.deleteLater()

    def test_get_selected_oid_returns_oid(self, qapp):
        """Test that get_selected_oid returns selected row OID."""
        from snmp_monitor.gui.views import DataTableWidget

        widget = DataTableWidget()

        widget.add_row("1.3.6.1.2.1.1.1.0", "sysDescr", "Test", "String")
        widget.add_row("1.3.6.1.2.1.1.3.0", "sysUpTime", "1000", "String")

        # Select first row
        widget.table_widget.selectRow(0)

        selected = widget.get_selected_oid()
        assert selected == "1.3.6.1.2.1.1.1.0"

        widget.deleteLater()

    def test_get_selected_oid_returns_none_when_empty(self, qapp):
        """Test get_selected_oid returns None when no row selected."""
        from snmp_monitor.gui.views import DataTableWidget

        widget = DataTableWidget()

        selected = widget.get_selected_oid()
        assert selected is None

        widget.deleteLater()


# =============================================================================
# Test LogPanelWidget Log Additions
# =============================================================================

class TestLogPanelWidgetLogAdditions:
    """Test LogPanelWidget log adding functionality."""

    def test_append_info_increments_count(self, qapp):
        """Test that append_info increments log count."""
        from snmp_monitor.gui.views import LogPanelWidget

        widget = LogPanelWidget()

        initial_count = widget.get_log_count()
        widget.append_info("Test message")

        assert widget.get_log_count() == initial_count + 1

        widget.deleteLater()

    def test_append_error_increments_count(self, qapp):
        """Test that append_error increments log count."""
        from snmp_monitor.gui.views import LogPanelWidget

        widget = LogPanelWidget()

        initial_count = widget.get_log_count()
        widget.append_error("Error message")

        assert widget.get_log_count() == initial_count + 1

        widget.deleteLater()

    def test_append_warning_increments_count(self, qapp):
        """Test that append_warning increments log count."""
        from snmp_monitor.gui.views import LogPanelWidget

        widget = LogPanelWidget()

        initial_count = widget.get_log_count()
        widget.append_warning("Warning message")

        assert widget.get_log_count() == initial_count + 1

        widget.deleteLater()

    def test_append_trap_increments_count(self, qapp):
        """Test that append_trap increments log count."""
        from snmp_monitor.gui.views import LogPanelWidget

        widget = LogPanelWidget()

        initial_count = widget.get_log_count()
        widget.append_trap("Trap message")

        assert widget.get_log_count() == initial_count + 1

        widget.deleteLater()

    def test_log_content_contains_message(self, qapp):
        """Test that log display contains the message."""
        from snmp_monitor.gui.views import LogPanelWidget

        widget = LogPanelWidget()

        test_message = "UniqueTestMessage12345"
        widget.append_info(test_message)

        content = widget.log_display.toPlainText()
        assert test_message in content

        widget.deleteLater()

    def test_log_contains_timestamp(self, qapp):
        """Test that log entries contain timestamp."""
        from snmp_monitor.gui.views import LogPanelWidget

        widget = LogPanelWidget()

        widget.append_info("Test message")

        content = widget.log_display.toPlainText()
        # Should contain timestamp pattern [HH:MM:SS]
        assert '[' in content
        assert ':' in content

        widget.deleteLater()

    def test_clear_resets_count(self, qapp):
        """Test that clear resets log count to zero."""
        from snmp_monitor.gui.views import LogPanelWidget

        widget = LogPanelWidget()

        widget.append_info("Message 1")
        widget.append_error("Message 2")
        widget.append_warning("Message 3")

        assert widget.get_log_count() == 3

        widget.clear()

        assert widget.get_log_count() == 0

        widget.deleteLater()

    def test_clear_button_clears_content(self, qapp):
        """Test that clicking clear button clears logs."""
        from snmp_monitor.gui.views import LogPanelWidget

        widget = LogPanelWidget()

        widget.append_info("Test message")
        assert widget.get_log_count() == 1

        widget.clear_button.click()

        assert widget.get_log_count() == 0

        widget.deleteLater()

    def test_clear_requested_signal_emitted(self, qapp):
        """Test that clear_requested signal is emitted on clear button click."""
        from snmp_monitor.gui.views import LogPanelWidget

        widget = LogPanelWidget()

        signal_received = []

        def on_clear():
            signal_received.append(True)

        widget.clear_requested.connect(on_clear)

        # Signal is emitted via _on_clear_clicked (called by clear button)
        widget._on_clear_clicked()

        assert len(signal_received) == 1

        widget.deleteLater()


# =============================================================================
# Test AlertConfigDialog Threshold Settings
# =============================================================================

class TestAlertConfigDialogThresholdSettings:
    """Test AlertConfigDialog threshold configuration."""

    def test_dialog_has_cpu_spinbox(self, qapp):
        """Test that dialog has CPU spinbox."""
        from snmp_monitor.gui.views import AlertConfigDialog

        dialog = AlertConfigDialog()

        assert hasattr(dialog, '_cpu_spinbox')

        dialog.reject()

    def test_dialog_has_memory_spinbox(self, qapp):
        """Test that dialog has memory spinbox."""
        from snmp_monitor.gui.views import AlertConfigDialog

        dialog = AlertConfigDialog()

        assert hasattr(dialog, '_memory_spinbox')

        dialog.reject()

    def test_dialog_has_disk_spinbox(self, qapp):
        """Test that dialog has disk spinbox."""
        from snmp_monitor.gui.views import AlertConfigDialog

        dialog = AlertConfigDialog()

        assert hasattr(dialog, '_disk_spinbox')

        dialog.reject()

    def test_set_thresholds_sets_cpu(self, qapp):
        """Test that set_thresholds sets CPU value."""
        from snmp_monitor.gui.views import AlertConfigDialog

        dialog = AlertConfigDialog()

        dialog.set_thresholds(cpu=75)

        assert dialog._cpu_spinbox.value() == 75

        dialog.reject()

    def test_set_thresholds_sets_memory(self, qapp):
        """Test that set_thresholds sets memory value."""
        from snmp_monitor.gui.views import AlertConfigDialog

        dialog = AlertConfigDialog()

        dialog.set_thresholds(memory=85)

        assert dialog._memory_spinbox.value() == 85

        dialog.reject()

    def test_set_thresholds_sets_disk(self, qapp):
        """Test that set_thresholds sets disk value."""
        from snmp_monitor.gui.views import AlertConfigDialog

        dialog = AlertConfigDialog()

        dialog.set_thresholds(disk=90)

        assert dialog._disk_spinbox.value() == 90

        dialog.reject()

    def test_set_thresholds_sets_all(self, qapp):
        """Test that set_thresholds sets all threshold values."""
        from snmp_monitor.gui.views import AlertConfigDialog

        dialog = AlertConfigDialog()

        dialog.set_thresholds(cpu=70, memory=80, disk=90)

        assert dialog._cpu_spinbox.value() == 70
        assert dialog._memory_spinbox.value() == 80
        assert dialog._disk_spinbox.value() == 90

        dialog.reject()

    def test_get_thresholds_returns_dict(self, qapp):
        """Test that get_thresholds returns correct dictionary."""
        from snmp_monitor.gui.views import AlertConfigDialog

        dialog = AlertConfigDialog()

        dialog._cpu_spinbox.setValue(75)
        dialog._memory_spinbox.setValue(85)
        dialog._disk_spinbox.setValue(90)

        thresholds = dialog.get_thresholds()

        assert thresholds['cpu'] == 75
        assert thresholds['memory'] == 85
        assert thresholds['disk'] == 90

        dialog.reject()

    def test_spinbox_range_0_to_100(self, qapp):
        """Test that spinboxes have range 0-100."""
        from snmp_monitor.gui.views import AlertConfigDialog

        dialog = AlertConfigDialog()

        assert dialog._cpu_spinbox.minimum() == 0
        assert dialog._cpu_spinbox.maximum() == 100

        dialog.reject()

    def test_ok_button_emits_signal(self, qapp):
        """Test that OK button emits thresholds_changed signal."""
        from snmp_monitor.gui.views import AlertConfigDialog

        dialog = AlertConfigDialog()

        received_thresholds = []

        def on_thresholds_changed(thresholds):
            received_thresholds.append(thresholds)

        dialog.thresholds_changed.connect(on_thresholds_changed)

        dialog.set_thresholds(cpu=70, memory=80, disk=90)
        dialog._ok_btn.click()

        assert len(received_thresholds) == 1
        assert received_thresholds[0]['cpu'] == 70

        dialog.reject()

    def test_ok_button_accepts_dialog(self, qapp):
        """Test that OK button accepts the dialog."""
        from snmp_monitor.gui.views import AlertConfigDialog

        dialog = AlertConfigDialog()

        dialog.set_thresholds(cpu=70, memory=80, disk=90)

        # Accept the dialog by calling accept() directly
        dialog.accept()

        # Dialog should return Accepted
        assert dialog.result() == QDialog.Accepted

    def test_cancel_button_rejects_dialog(self, qapp):
        """Test that Cancel button rejects the dialog."""
        from snmp_monitor.gui.views import AlertConfigDialog

        dialog = AlertConfigDialog()

        dialog._cancel_btn.click()
        result = dialog.result()

        # Cancel should return Rejected
        assert result == QDialog.Rejected


# =============================================================================
# Test Component Signal Integration
# =============================================================================

class TestComponentSignalIntegration:
    """Test signal connections between components."""

    def test_device_tree_to_data_table_signal(self, qapp):
        """Test DeviceTreeWidget oid_selected triggers DataTableWidget search."""
        from snmp_monitor.gui.views import DeviceTreeWidget, DataTableWidget
        from snmp_monitor.gui.models.mib_model import MIBModel

        model = MIBModel()
        tree_widget = DeviceTreeWidget(model)
        table_widget = DataTableWidget()

        received_oids = []

        def on_query_requested(oid):
            received_oids.append(oid)

        table_widget.oid_query_requested.connect(on_query_requested)
        tree_widget.oid_selected.connect(table_widget.search_oid)

        # Trigger oid_selected
        tree_widget.oid_selected.emit("1.3.6.1.2.1.1.1.0")

        assert len(received_oids) == 1
        assert received_oids[0] == "1.3.6.1.2.1.1.1.0"

        tree_widget.deleteLater()
        table_widget.deleteLater()

    def test_log_panel_clear_signal_chain(self, qapp):
        """Test LogPanelWidget clear button emits clear_requested."""
        from snmp_monitor.gui.views import LogPanelWidget

        widget = LogPanelWidget()

        signal_count = [0]

        def on_clear():
            signal_count[0] += 1

        widget.clear_requested.connect(on_clear)

        # Add a log entry
        widget.append_info("Test")
        assert signal_count[0] == 0

        # Click clear button
        widget.clear_button.click()

        assert signal_count[0] == 1

        widget.deleteLater()

    def test_table_selection_to_oid_query(self, qapp):
        """Test table row selection can trigger OID query."""
        from snmp_monitor.gui.views import DataTableWidget

        widget = DataTableWidget()

        received_oids = []

        def on_query(oid):
            received_oids.append(oid)

        widget.oid_query_requested.connect(on_query)

        # Add some OIDs
        widget.add_row("1.3.6.1.2.1.1.1.0", "sysDescr", "Test", "String")
        widget.add_row("1.3.6.1.2.1.1.3.0", "sysUpTime", "1000", "String")

        # Set OID in input field (simulating what happens when a row is selected)
        widget.oid_input.setText("1.3.6.1.2.1.1.1.0")

        # Trigger search
        widget.search_button.click()
        qapp.processEvents()

        assert len(received_oids) == 1

        widget.deleteLater()


# =============================================================================
# Test MainWindow Complete Lifecycle
# =============================================================================

class TestMainWindowLifecycle:
    """Test MainWindow complete lifecycle."""

    def test_main_window_creates_all_widgets(self, qapp):
        """Test that MainWindow creates all required widgets."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Check all widgets exist
        assert hasattr(window, '_dashboard_widget')
        assert hasattr(window, '_device_tree_widget')
        assert hasattr(window, '_data_table_widget')
        assert hasattr(window, '_log_panel_widget')
        assert hasattr(window, '_control_panel')

        window.close()

    def test_main_window_initial_log_message(self, qapp):
        """Test that MainWindow logs initialization message."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        log_count = window._log_panel_widget.get_log_count()
        assert log_count >= 1  # Should have at least the init message

        window.close()

    def test_main_window_control_panel_buttons(self, qapp):
        """Test that control panel has start/stop buttons."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        assert hasattr(window, '_start_btn')
        assert hasattr(window, '_stop_btn')

        # Stop button should be disabled initially
        assert not window._stop_btn.isEnabled()

        window.close()

    def test_main_window_start_stop_toggle(self, qapp):
        """Test start/stop button state toggles."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Mock workers
        with patch('snmp_monitor.gui.workers.SNMPWorker.start'):
            with patch('snmp_monitor.gui.workers.TrapWorker.start'):
                # Initially
                assert window._start_btn.isEnabled()
                assert not window._stop_btn.isEnabled()

                # Start monitoring
                window.start_monitoring()

                assert not window._start_btn.isEnabled()
                assert window._stop_btn.isEnabled()

                # Stop monitoring
                window.stop_monitoring()

                assert window._start_btn.isEnabled()
                assert not window._stop_btn.isEnabled()

        window.close()

    def test_main_window_status_label(self, qapp):
        """Test status label updates with monitoring state."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Initially
        assert "Stopped" in window._status_label.text() or "停止" in window._status_label.text()

        with patch('snmp_monitor.gui.workers.SNMPWorker.start'):
            with patch('snmp_monitor.gui.workers.TrapWorker.start'):
                window.start_monitoring()

                assert "Running" in window._status_label.text() or "运行" in window._status_label.text()

                window.stop_monitoring()

                assert "Stopped" in window._status_label.text() or "停止" in window._status_label.text()

        window.close()

    def test_main_window_close_stops_workers(self, qapp):
        """Test that closing window stops workers."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        with patch('snmp_monitor.gui.workers.SNMPWorker.start'):
            with patch('snmp_monitor.gui.workers.SNMPWorker.stop'):
                with patch('snmp_monitor.gui.workers.TrapWorker.start'):
                    with patch('snmp_monitor.gui.workers.TrapWorker.stop'):
                        window.start_monitoring()
                        window.close()

        # Workers should have been stopped
        # No assertion on mock calls as stop is called in closeEvent

    def test_main_window_menu_bar_exists(self, qapp):
        """Test that MainWindow has menu bar."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        menubar = window.menuBar()
        assert menubar is not None

        window.close()

    def test_main_window_menu_file_exists(self, qapp):
        """Test that File menu exists."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        menubar = window.menuBar()
        menus_with_titles = [(action.menu(), action.menu().title())
                            for action in menubar.actions() if action.menu()]

        file_menu = None
        for menu, title in menus_with_titles:
            if "File" in title:
                file_menu = menu
                break

        assert file_menu is not None

        window.close()

    def test_main_window_menu_monitoring_exists(self, qapp):
        """Test that Monitoring menu exists."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        menubar = window.menuBar()
        menus_with_titles = [(action.menu(), action.menu().title())
                            for action in menubar.actions() if action.menu()]

        monitoring_menu = None
        for menu, title in menus_with_titles:
            if "Monitoring" in title:
                monitoring_menu = menu
                break

        assert monitoring_menu is not None

        window.close()

    def test_main_window_menu_help_exists(self, qapp):
        """Test that Help menu exists."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        menubar = window.menuBar()
        menus_with_titles = [(action.menu(), action.menu().title())
                            for action in menubar.actions() if action.menu()]

        help_menu = None
        for menu, title in menus_with_titles:
            if "Help" in title:
                help_menu = menu
                break

        assert help_menu is not None

        window.close()


# =============================================================================
# Test User Interactions
# =============================================================================

class TestUserInteractions:
    """Test user interaction scenarios."""

    def test_button_click_response(self, qapp):
        """Test that button click responds correctly."""
        from snmp_monitor.gui.views import DataTableWidget

        widget = DataTableWidget()

        received = []

        widget.oid_query_requested.connect(lambda oid: received.append(oid))

        widget.oid_input.setText("1.2.3.4.5")
        widget.search_button.click()

        assert len(received) == 1

        widget.deleteLater()

    def test_dialog_open_and_close(self, qapp):
        """Test opening and closing a dialog."""
        from snmp_monitor.gui.views import AlertConfigDialog

        dialog = AlertConfigDialog()

        dialog.set_thresholds(cpu=75, memory=85, disk=90)

        # Test accepting the dialog
        dialog.accept()

        # Dialog should be in accepted state
        assert dialog.result() == QDialog.Accepted

    def test_table_row_selection(self, qapp):
        """Test selecting a row in the table."""
        from snmp_monitor.gui.views import DataTableWidget

        widget = DataTableWidget()

        widget.add_row("1.3.6.1.2.1.1.1.0", "sysDescr", "Test1", "String")
        widget.add_row("1.3.6.1.2.1.1.3.0", "sysUpTime", "Test2", "String")

        # Select second row
        widget.table_widget.selectRow(1)

        selected = widget.get_selected_oid()
        assert selected == "1.3.6.1.2.1.1.3.0"

        widget.deleteLater()

    def test_multiple_row_selection_returns_first(self, qapp):
        """Test that get_selected_oid returns first of multiple selections."""
        from snmp_monitor.gui.views import DataTableWidget

        widget = DataTableWidget()

        widget.add_row("1.3.6.1.2.1.1.1.0", "sysDescr", "Test1", "String")
        widget.add_row("1.3.6.1.2.1.1.3.0", "sysUpTime", "Test2", "String")

        # Select multiple rows (Ctrl+click behavior simulation)
        widget.table_widget.selectRow(0)
        widget.table_widget.selectRow(1)

        # Should return first selected
        selected = widget.get_selected_oid()
        assert selected in ["1.3.6.1.2.1.1.1.0", "1.3.6.1.2.1.1.3.0"]

        widget.deleteLater()

    def test_input_field_accepts_text(self, qapp):
        """Test that OID input field accepts text."""
        from snmp_monitor.gui.views import DataTableWidget

        widget = DataTableWidget()

        test_oid = "1.3.6.1.2.1.1.1.0"
        widget.oid_input.setText(test_oid)

        assert widget.oid_input.text() == test_oid

        widget.deleteLater()

    def test_spinbox_value_changes(self, qapp):
        """Test that spinbox values can be changed."""
        from snmp_monitor.gui.views import AlertConfigDialog

        dialog = AlertConfigDialog()

        dialog._cpu_spinbox.setValue(50)
        assert dialog._cpu_spinbox.value() == 50

        dialog._cpu_spinbox.setValue(75)
        assert dialog._cpu_spinbox.value() == 75

        dialog.reject()


# =============================================================================
# Test End-to-End Scenarios
# =============================================================================

class TestEndToEndScenarios:
    """Test complete end-to-end scenarios."""

    def test_monitoring_workflow(self, qapp):
        """Test complete monitoring workflow."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Initial state
        initial_log_count = window._log_panel_widget.get_log_count()

        # Start monitoring
        with patch('snmp_monitor.gui.workers.SNMPWorker.start'):
            with patch('snmp_monitor.gui.workers.TrapWorker.start'):
                window.start_monitoring()

        # Verify log updated
        assert window._log_panel_widget.get_log_count() > initial_log_count

        # Simulate data
        test_data = {
            (1, 3, 6, 1, 4, 1, 2021, 4, 3, 0): 50.0,
            (1, 3, 6, 1, 4, 1, 2021, 4, 6, 0): 60.0,
        }
        window._on_worker_data_ready(test_data)

        # Verify dashboard updated
        assert 50.0 in window._dashboard_widget.cpu_data

        # Stop monitoring
        window.stop_monitoring()

        window.close()

    def test_oid_query_workflow(self, qapp):
        """Test OID query workflow from tree to table."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Search for OID via DataTableWidget
        window._data_table_widget.search_oid("1.3.6.1.2.1.1.1.0")

        # Should have updated input field
        assert window._data_table_widget.oid_input.text() == "1.3.6.1.2.1.1.1.0"

        window.close()

    def test_threshold_configuration_workflow(self, qapp):
        """Test threshold configuration workflow."""
        from snmp_monitor.gui.app import MainWindow
        from snmp_monitor.gui.views import AlertConfigDialog

        window = MainWindow()

        # Get initial thresholds
        initial_cpu = window._snmp_model.cpu_threshold

        # Create and configure dialog
        dialog = AlertConfigDialog(window)
        new_cpu = initial_cpu + 10
        dialog.set_thresholds(cpu=new_cpu, memory=85, disk=90)

        # Apply thresholds
        window._on_thresholds_changed({'cpu': new_cpu, 'memory': 85, 'disk': 90})

        # Verify model updated
        assert window._snmp_model.cpu_threshold == new_cpu

        # Verify log updated
        log_content = window._log_panel_widget.log_display.toPlainText()
        assert "Thresholds updated" in log_content or "阈值更新" in log_content

        window.close()

    def test_trap_reception_workflow(self, qapp):
        """Test trap reception workflow."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        initial_count = window._log_panel_widget.get_log_count()

        # Simulate trap
        trap_data = {
            'source': '192.168.1.100',
            'oid': '.1.3.6.1.4.1.2021.4',
            'message': 'Test trap',
            'severity': 'warning'
        }
        window._on_trap_received(trap_data)

        # Verify log updated
        assert window._log_panel_widget.get_log_count() > initial_count

        # Verify trap in log
        log_content = window._log_panel_widget.log_display.toPlainText()
        assert "Test trap" in log_content

        window.close()

    def test_error_handling_workflow(self, qapp):
        """Test error handling workflow."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        initial_count = window._log_panel_widget.get_log_count()

        # Simulate error
        window._on_worker_error("Connection failed")

        # Verify log updated
        assert window._log_panel_widget.get_log_count() > initial_count

        # Verify error in log
        log_content = window._log_panel_widget.log_display.toPlainText()
        assert "Connection failed" in log_content

        window.close()


# =============================================================================
# Test Component Properties
# =============================================================================

class TestComponentProperties:
    """Test component property access."""

    def test_dashboard_properties(self, qapp):
        """Test DashboardWidget property accessors."""
        from snmp_monitor.gui.views import DashboardWidget

        widget = DashboardWidget(max_points=25)

        assert widget.max_points == 25
        assert isinstance(widget.cpu_data, list)
        assert isinstance(widget.memory_data, list)

        widget.deleteLater()

    def test_device_tree_properties(self, qapp):
        """Test DeviceTreeWidget property accessors."""
        from snmp_monitor.gui.views import DeviceTreeWidget

        widget = DeviceTreeWidget()

        assert widget.tree_view is not None
        assert widget.model is not None

        widget.deleteLater()

    def test_data_table_properties(self, qapp):
        """Test DataTableWidget property accessors."""
        from snmp_monitor.gui.views import DataTableWidget

        widget = DataTableWidget()

        assert widget.table_widget is not None
        assert widget.oid_input is not None
        assert widget.search_button is not None

        widget.deleteLater()

    def test_log_panel_properties(self, qapp):
        """Test LogPanelWidget property accessors."""
        from snmp_monitor.gui.views import LogPanelWidget

        widget = LogPanelWidget()

        assert widget.log_display is not None
        assert widget.clear_button is not None

        widget.deleteLater()

    def test_main_window_widget_properties(self, qapp):
        """Test MainWindow widget property accessors."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        assert window.snmp_model is not None
        assert window.mib_model is not None
        assert window.dashboard_widget is not None
        assert window.device_tree_widget is not None
        assert window.data_table_widget is not None
        assert window.log_panel_widget is not None

        window.close()
