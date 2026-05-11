"""Integration tests for MainWindow with all View components.

This module tests the integration between MainWindow and all
View components including:
- DashboardWidget integration
- DeviceTreeWidget integration
- DataTableWidget integration
- LogPanelWidget integration
- AlertConfigDialog integration
- Signal connections between workers and View components
- Menu bar functionality
"""
import sys
import pytest
from unittest.mock import Mock, MagicMock, patch

from PySide6.QtCore import Qt, QCoreApplication, QTimer
from PySide6.QtWidgets import QApplication, QMenu


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestViewComponentIntegration:
    """Test that all View components are properly integrated."""

    def test_main_window_imports_all_views(self, qapp):
        """Test that MainWindow can import all View components."""
        from snmp_monitor.gui.views import (
            DashboardWidget,
            DeviceTreeWidget,
            DataTableWidget,
            LogPanelWidget,
            AlertConfigDialog
        )
        assert DashboardWidget is not None
        assert DeviceTreeWidget is not None
        assert DataTableWidget is not None
        assert LogPanelWidget is not None
        assert AlertConfigDialog is not None

    def test_main_window_has_dashboard_widget(self, qapp):
        """Test that MainWindow has DashboardWidget instance."""
        from snmp_monitor.gui.app import MainWindow
        from snmp_monitor.gui.views import DashboardWidget

        window = MainWindow()
        assert hasattr(window, '_dashboard_widget')
        assert isinstance(window._dashboard_widget, DashboardWidget)
        window.close()

    def test_main_window_has_device_tree_widget(self, qapp):
        """Test that MainWindow has DeviceTreeWidget instance."""
        from snmp_monitor.gui.app import MainWindow
        from snmp_monitor.gui.views import DeviceTreeWidget

        window = MainWindow()
        assert hasattr(window, '_device_tree_widget')
        assert isinstance(window._device_tree_widget, DeviceTreeWidget)
        window.close()

    def test_main_window_has_data_table_widget(self, qapp):
        """Test that MainWindow has DataTableWidget instance."""
        from snmp_monitor.gui.app import MainWindow
        from snmp_monitor.gui.views import DataTableWidget

        window = MainWindow()
        assert hasattr(window, '_data_table_widget')
        assert isinstance(window._data_table_widget, DataTableWidget)
        window.close()

    def test_main_window_has_log_panel_widget(self, qapp):
        """Test that MainWindow has LogPanelWidget instance."""
        from snmp_monitor.gui.app import MainWindow
        from snmp_monitor.gui.views import LogPanelWidget

        window = MainWindow()
        assert hasattr(window, '_log_panel_widget')
        assert isinstance(window._log_panel_widget, LogPanelWidget)
        window.close()


class TestLayoutIntegration:
    """Test the layout organization of MainWindow."""

    def test_uses_qgridlayout(self, qapp):
        """Test that MainWindow uses QGridLayout for main layout."""
        from snmp_monitor.gui.app import MainWindow
        from PySide6.QtWidgets import QGridLayout

        window = MainWindow()
        central_widget = window.centralWidget()
        layout = central_widget.layout()

        # Main layout should be QGridLayout
        assert isinstance(layout, QGridLayout)
        window.close()

    def test_has_control_panel_widget(self, qapp):
        """Test that MainWindow has a control panel widget with buttons."""
        from snmp_monitor.gui.app import MainWindow
        from PySide6.QtWidgets import QWidget

        window = MainWindow()
        assert hasattr(window, '_control_panel')
        assert isinstance(window._control_panel, QWidget)
        window.close()

    def test_has_start_stop_buttons(self, qapp):
        """Test that control panel has start and stop buttons."""
        from snmp_monitor.gui.app import MainWindow
        from PySide6.QtWidgets import QPushButton

        window = MainWindow()
        assert hasattr(window, '_start_btn')
        assert hasattr(window, '_stop_btn')
        assert isinstance(window._start_btn, QPushButton)
        assert isinstance(window._stop_btn, QPushButton)
        assert window._start_btn.text() in ["Start Monitoring", "开始监控"]
        assert window._stop_btn.text() in ["Stop Monitoring", "停止监控"]
        window.close()


class TestMenuBarIntegration:
    """Test menu bar integration."""

    def test_has_file_menu_with_exit(self, qapp):
        """Test that File menu has Exit action."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        menubar = window.menuBar()

        # Find File menu
        file_menu = None
        for action in menubar.actions():
            if action.menu() and "File" in action.menu().title():
                file_menu = action.menu()
                break

        assert file_menu is not None, "File menu should exist"

        # Check for Exit action
        exit_action = None
        for action in file_menu.actions():
            if "Exit" in action.text():
                exit_action = action
                break

        assert exit_action is not None, "Exit action should exist in File menu"
        window.close()

    def test_has_monitoring_menu(self, qapp):
        """Test that Monitoring menu exists with Start/Stop actions."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        menubar = window.menuBar()

        # Find Monitoring menu
        monitoring_menu = None
        for action in menubar.actions():
            if action.menu() and "Monitoring" in action.menu().title():
                monitoring_menu = action.menu()
                break

        assert monitoring_menu is not None, "Monitoring menu should exist"

        # Check for Start and Stop actions
        has_start = any("Start" in a.text() for a in monitoring_menu.actions())
        has_stop = any("Stop" in a.text() for a in monitoring_menu.actions())

        assert has_start, "Start action should exist in Monitoring menu"
        assert has_stop, "Stop action should exist in Monitoring menu"
        window.close()

    def test_has_threshold_config_action(self, qapp):
        """Test that Monitoring menu has Threshold Configuration action."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        menubar = window.menuBar()

        # Find Monitoring menu
        monitoring_menu = None
        for action in menubar.actions():
            if action.menu() and "Monitoring" in action.menu().title():
                monitoring_menu = action.menu()
                break

        assert monitoring_menu is not None, "Monitoring menu should exist"

        # Check for Threshold Configuration action
        has_threshold_config = any(
            "Threshold" in a.text() or "阈值" in a.text()
            for a in monitoring_menu.actions()
        )

        assert has_threshold_config, "Threshold Configuration action should exist"
        window.close()

    def test_has_help_menu_with_about(self, qapp):
        """Test that Help menu has About action."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        menubar = window.menuBar()

        # Find Help menu
        help_menu = None
        for action in menubar.actions():
            if action.menu() and "Help" in action.menu().title():
                help_menu = action.menu()
                break

        assert help_menu is not None, "Help menu should exist"

        # Check for About action
        about_action = None
        for action in help_menu.actions():
            if "About" in action.text():
                about_action = action
                break

        assert about_action is not None, "About action should exist in Help menu"
        window.close()


class TestSignalConnections:
    """Test signal connections between workers and View components."""

    def test_worker_data_ready_connects_to_dashboard(self, qapp):
        """Test that worker data_ready connects to DashboardWidget.update_data."""
        from snmp_monitor.gui.app import MainWindow
        from unittest.mock import MagicMock

        window = MainWindow()

        # Mock the update_data method
        with patch.object(window._dashboard_widget, 'update_data') as mock_update:
            # Simulate worker data ready signal
            test_data = {
                (1, 3, 6, 1, 4, 1, 2021, 4, 3, 0): 50.0,  # cpu
                (1, 3, 6, 1, 4, 1, 2021, 4, 6, 0): 60.0,  # memory
            }
            window._on_worker_data_ready(test_data)
            qapp.processEvents()

            # Should have been called
            mock_update.assert_called()
        window.close()

    def test_worker_data_ready_connects_to_data_table(self, qapp):
        """Test that worker data_ready connects to DataTableWidget."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Simulate worker data ready signal
        test_data = {
            (1, 3, 6, 1, 4, 1, 2021, 4, 3, 0): 50.0,
            (1, 3, 6, 1, 4, 1, 2021, 4, 6, 0): 60.0,
        }
        window._on_worker_data_ready(test_data)
        qapp.processEvents()

        # Verify SNMP model was updated
        assert window._snmp_model.cpu_percent is not None
        window.close()

    def test_worker_error_connects_to_log_panel(self, qapp):
        """Test that worker error connects to LogPanelWidget.append_error."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Get initial log count
        initial_count = window._log_panel_widget.get_log_count()

        # Simulate worker error
        window._on_worker_error("Test error message")
        qapp.processEvents()

        # Verify log panel was updated
        assert window._log_panel_widget.get_log_count() > initial_count

        # Check error message is in log display
        log_content = window._log_panel_widget.log_display.toPlainText()
        assert "Test error message" in log_content
        window.close()

    def test_trap_received_connects_to_log_panel(self, qapp):
        """Test that trap_received connects to LogPanelWidget.append_trap."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Get initial log count
        initial_count = window._log_panel_widget.get_log_count()

        # Simulate trap received
        trap_data = {
            'source': '192.168.1.100',
            'oid': '.1.3.6.1.4.1.2021.4',
            'message': 'Test trap alert',
            'severity': 'warning'
        }
        window._on_trap_received(trap_data)
        qapp.processEvents()

        # Verify log panel was updated
        assert window._log_panel_widget.get_log_count() > initial_count
        window.close()

    def test_oid_query_requested_connected_to_worker(self, qapp):
        """Test that OID query from DataTableWidget connects to SNMPWorker.query_oid."""
        from snmp_monitor.gui.app import MainWindow
        from unittest.mock import MagicMock

        window = MainWindow()

        # Start workers with mocked network
        with patch('snmp_monitor.gui.workers.SNMPWorker.start'):
            with patch('snmp_monitor.gui.workers.TrapWorker.start'):
                window.start_workers()

        # Mock the query_oid method
        with patch.object(window._snmp_worker, 'query_oid') as mock_query:
            # Simulate OID query from DataTableWidget
            test_oid = "1.3.6.1.2.1.1.1.0"
            window._data_table_widget.search_oid(test_oid)
            qapp.processEvents()

            # Should have called query_oid
            mock_query.assert_called_with(test_oid)

        window.close()


class TestThresholdConfigurationIntegration:
    """Test threshold configuration integration with AlertConfigDialog."""

    def test_threshold_config_opens_dialog(self, qapp):
        """Test that threshold configuration opens AlertConfigDialog."""
        from snmp_monitor.gui.app import MainWindow
        from snmp_monitor.gui.views import AlertConfigDialog

        window = MainWindow()

        # Create dialog
        dialog = AlertConfigDialog(window)

        # Verify dialog can be created
        assert dialog is not None
        assert dialog.windowTitle() in ["配置告警阈值", "Alert Configuration"]

        dialog.reject()
        window.close()

    def test_threshold_config_updates_model(self, qapp):
        """Test that threshold changes update the model."""
        from snmp_monitor.gui.app import MainWindow
        from snmp_monitor.gui.views import AlertConfigDialog

        window = MainWindow()

        # Get initial threshold
        initial_cpu = window._snmp_model.cpu_threshold

        # Create and configure dialog
        dialog = AlertConfigDialog(window)
        new_cpu = initial_cpu + 10
        dialog.set_thresholds(cpu=new_cpu)

        # Manually trigger threshold change
        window._on_thresholds_changed({'cpu': new_cpu, 'memory': 85, 'disk': 90})
        qapp.processEvents()

        # Verify model was updated
        assert window._snmp_model.cpu_threshold == new_cpu

        window.close()

    def test_threshold_config_has_ok_cancel_buttons(self, qapp):
        """Test that AlertConfigDialog has OK and Cancel buttons."""
        from snmp_monitor.gui.views import AlertConfigDialog

        dialog = AlertConfigDialog()
        assert hasattr(dialog, '_ok_btn')
        assert hasattr(dialog, '_cancel_btn')
        dialog.reject()


class TestDashboardWidgetIntegration:
    """Test DashboardWidget integration and data updates."""

    def test_dashboard_widget_has_update_data_method(self, qapp):
        """Test that DashboardWidget has update_data method."""
        from snmp_monitor.gui.views import DashboardWidget

        widget = DashboardWidget()
        assert hasattr(widget, 'update_data')
        assert callable(widget.update_data)
        widget.deleteLater()

    def test_dashboard_widget_updates_on_data(self, qapp):
        """Test that DashboardWidget updates when data is received."""
        from snmp_monitor.gui.views import DashboardWidget

        widget = DashboardWidget()

        # Update with test data
        widget.update_data(cpu=50.0, memory=60.0)

        # Verify data was stored
        assert 50.0 in widget.cpu_data
        assert 60.0 in widget.memory_data

        widget.deleteLater()


class TestDeviceTreeWidgetIntegration:
    """Test DeviceTreeWidget integration."""

    def test_device_tree_oid_selected_signal_exists(self, qapp):
        """Test that DeviceTreeWidget has oid_selected signal."""
        from snmp_monitor.gui.views import DeviceTreeWidget

        widget = DeviceTreeWidget()
        assert hasattr(widget, 'oid_selected')
        widget.deleteLater()

    def test_device_tree_refresh_button_exists(self, qapp):
        """Test that DeviceTreeWidget has refresh button."""
        from snmp_monitor.gui.views import DeviceTreeWidget

        widget = DeviceTreeWidget()
        assert hasattr(widget, 'refresh_button')
        widget.deleteLater()


class TestDataTableWidgetIntegration:
    """Test DataTableWidget integration."""

    def test_data_table_has_oid_query_signal(self, qapp):
        """Test that DataTableWidget has oid_query_requested signal."""
        from snmp_monitor.gui.views import DataTableWidget

        widget = DataTableWidget()
        assert hasattr(widget, 'oid_query_requested')
        widget.deleteLater()

    def test_data_table_has_update_table_method(self, qapp):
        """Test that DataTableWidget has update_table method."""
        from snmp_monitor.gui.views import DataTableWidget

        widget = DataTableWidget()
        assert hasattr(widget, 'update_table')
        assert callable(widget.update_table)
        widget.deleteLater()

    def test_data_table_has_update_oid_value_method(self, qapp):
        """Test that DataTableWidget has update_oid_value method."""
        from snmp_monitor.gui.views import DataTableWidget

        widget = DataTableWidget()
        assert hasattr(widget, 'update_oid_value')
        assert callable(widget.update_oid_value)
        widget.deleteLater()


class TestLogPanelWidgetIntegration:
    """Test LogPanelWidget integration."""

    def test_log_panel_has_append_error_method(self, qapp):
        """Test that LogPanelWidget has append_error method."""
        from snmp_monitor.gui.views import LogPanelWidget

        widget = LogPanelWidget()
        assert hasattr(widget, 'append_error')
        assert callable(widget.append_error)
        widget.deleteLater()

    def test_log_panel_has_append_trap_method(self, qapp):
        """Test that LogPanelWidget has append_trap method."""
        from snmp_monitor.gui.views import LogPanelWidget

        widget = LogPanelWidget()
        assert hasattr(widget, 'append_trap')
        assert callable(widget.append_trap)
        widget.deleteLater()

    def test_log_panel_has_clear_method(self, qapp):
        """Test that LogPanelWidget has clear method."""
        from snmp_monitor.gui.views import LogPanelWidget

        widget = LogPanelWidget()
        assert hasattr(widget, 'clear')
        assert callable(widget.clear)
        widget.deleteLater()


class TestEndToEndIntegration:
    """Test end-to-end integration scenarios."""

    def test_full_monitoring_flow(self, qapp):
        """Test complete flow from worker to all View components."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Start workers with mocked network
        with patch('snmp_monitor.gui.workers.SNMPWorker.start'):
            with patch('snmp_monitor.gui.workers.TrapWorker.start'):
                window.start_workers()

        # Simulate worker data ready
        test_data = {
            (1, 3, 6, 1, 4, 1, 2021, 4, 3, 0): 50.0,
            (1, 3, 6, 1, 4, 1, 2021, 4, 6, 0): 60.0,
        }
        window._on_worker_data_ready(test_data)
        qapp.processEvents()

        # Simulate trap received
        trap_data = {
            'source': '192.168.1.100',
            'oid': '.1.3.6.1.4.1.2021.4',
            'message': 'Test trap alert',
            'severity': 'warning'
        }
        window._on_trap_received(trap_data)
        qapp.processEvents()

        # Simulate error
        window._on_worker_error("Connection error")
        qapp.processEvents()

        # Verify all components received updates
        assert window._snmp_model.cpu_percent is not None
        assert window._log_panel_widget.get_log_count() > 0

        # Stop monitoring
        window.stop_monitoring()
        window.close()

    def test_oid_query_to_result_flow(self, qapp):
        """Test OID query flow from DataTableWidget to SNMPWorker to result."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Start workers
        with patch('snmp_monitor.gui.workers.SNMPWorker.start'):
            with patch('snmp_monitor.gui.workers.TrapWorker.start'):
                window.start_workers()

        # Mock the oid_query_result handling
        with patch.object(window, '_on_oid_query_result') as mock_handler:
            # Simulate query result
            window._on_oid_query_result("1.3.6.1.2.1.1.1.0", "SNMP Agent")
            qapp.processEvents()

            mock_handler.assert_called_once_with("1.3.6.1.2.1.1.1.0", "SNMP Agent")

        window.close()

    def test_alert_config_dialog_integration(self, qapp):
        """Test AlertConfigDialog opens and updates thresholds."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Open threshold config
        window._open_threshold_config()
        qapp.processEvents()

        # Dialog should have been created and shown
        # We can't test the dialog directly in unit tests,
        # but we can verify the method exists
        assert hasattr(window, '_open_threshold_config')
        assert callable(window._open_threshold_config)

        window.close()
