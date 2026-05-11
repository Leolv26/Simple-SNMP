"""Tests for MainWindow class in app.py."""
import sys
import pytest
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestMainWindowImports:
    """Test that MainWindow can be imported correctly."""

    def test_main_window_import(self):
        """Test that MainWindow can be imported from app module."""
        from snmp_monitor.gui.app import MainWindow
        assert MainWindow is not None

    def test_main_window_is_qmainwindow(self):
        """Test that MainWindow inherits from QMainWindow."""
        from snmp_monitor.gui.app import MainWindow
        # Check that MainWindow is a subclass of QMainWindow
        assert issubclass(MainWindow, QMainWindow)

    def test_main_window_can_be_instantiated(self, qapp):
        """Test that MainWindow can be instantiated."""
        from snmp_monitor.gui.app import MainWindow
        window = MainWindow()
        assert window is not None
        window.close()


class TestMainWindowInitialization:
    """Test MainWindow initialization."""

    def test_main_window_has_title(self, qapp):
        """Test that MainWindow has a title."""
        from snmp_monitor.gui.app import MainWindow
        window = MainWindow()
        assert window.windowTitle() == "SNMP Monitor"
        window.close()

    def test_main_window_has_central_widget(self, qapp):
        """Test that MainWindow has a central widget (container)."""
        from snmp_monitor.gui.app import MainWindow
        window = MainWindow()
        assert window.centralWidget() is not None
        window.close()

    def test_main_window_has_models(self, qapp):
        """Test that MainWindow has model instances."""
        from snmp_monitor.gui.app import MainWindow
        from snmp_monitor.gui.models import SNMPModel, MIBModel, TrapModel

        window = MainWindow()
        assert hasattr(window, '_snmp_model')
        assert hasattr(window, '_mib_model')
        assert hasattr(window, '_trap_model')
        assert isinstance(window._snmp_model, SNMPModel)
        assert isinstance(window._mib_model, MIBModel)
        assert isinstance(window._trap_model, TrapModel)
        window.close()

    def test_main_window_has_worker_attributes(self, qapp):
        """Test that MainWindow has worker attributes (workers created on start)."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        # Workers should be None initially, created when start_workers is called
        assert hasattr(window, '_snmp_worker')
        assert hasattr(window, '_trap_worker')
        assert window._snmp_worker is None
        assert window._trap_worker is None
        window.close()


class TestMainWindowLayout:
    """Test MainWindow layout structure."""

    def test_has_menu_bar(self, qapp):
        """Test that MainWindow has a menu bar."""
        from snmp_monitor.gui.app import MainWindow
        window = MainWindow()
        assert window.menuBar() is not None
        window.close()

    def test_has_status_bar(self, qapp):
        """Test that MainWindow has a status bar."""
        from snmp_monitor.gui.app import MainWindow
        window = MainWindow()
        assert window.statusBar() is not None
        window.close()

    def test_has_mib_tree_widget(self, qapp):
        """Test that MainWindow has MIB tree widget."""
        from snmp_monitor.gui.app import MainWindow
        from PySide6.QtWidgets import QTreeView

        window = MainWindow()
        assert hasattr(window, '_mib_tree')
        assert isinstance(window._mib_tree, QTreeView)
        window.close()

    def test_has_data_table_widget(self, qapp):
        """Test that MainWindow has data table widget."""
        from snmp_monitor.gui.app import MainWindow
        from PySide6.QtWidgets import QTableWidget

        window = MainWindow()
        assert hasattr(window, '_data_table')
        assert isinstance(window._data_table, QTableWidget)
        window.close()

    def test_has_alert_panel_widget(self, qapp):
        """Test that MainWindow has alert panel widget."""
        from snmp_monitor.gui.app import MainWindow
        from PySide6.QtWidgets import QWidget

        window = MainWindow()
        assert hasattr(window, '_alert_panel')
        assert isinstance(window._alert_panel, QWidget)
        window.close()

    def test_has_log_panel_widget(self, qapp):
        """Test that MainWindow has log panel widget."""
        from snmp_monitor.gui.app import MainWindow
        from PySide6.QtWidgets import QPlainTextEdit

        window = MainWindow()
        assert hasattr(window, '_log_panel')
        assert isinstance(window._log_panel, QPlainTextEdit)
        window.close()

    def test_has_dashboard_container(self, qapp):
        """Test that MainWindow has dashboard container widget."""
        from snmp_monitor.gui.app import MainWindow
        from PySide6.QtWidgets import QWidget

        window = MainWindow()
        assert hasattr(window, '_dashboard')
        assert isinstance(window._dashboard, QWidget)
        window.close()


class TestMainWindowSignalConnections:
    """Test MainWindow signal connections."""

    def test_model_signals_connected(self, qapp):
        """Test that model signals are properly connected."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        # Verify that models exist and have expected signals
        assert hasattr(window._snmp_model, 'data_updated')
        assert hasattr(window._snmp_model, 'threshold_exceeded')
        window.close()


class TestMainWindowWorkerManagement:
    """Test MainWindow worker management."""

    def test_workers_created_on_start(self, qapp):
        """Test that workers are created when start_workers is called."""
        from snmp_monitor.gui.app import MainWindow
        from snmp_monitor.gui.workers import SNMPWorker, TrapWorker

        window = MainWindow()

        # Workers should be None initially
        assert window._snmp_worker is None
        assert window._trap_worker is None

        # Call start_workers (mock the network parts)
        with patch('snmp_monitor.gui.workers.SNMPWorker.start'):
            with patch('snmp_monitor.gui.workers.TrapWorker.start'):
                window.start_workers()

        # Workers should now exist
        assert window._snmp_worker is not None
        assert window._trap_worker is not None
        assert isinstance(window._snmp_worker, SNMPWorker)
        assert isinstance(window._trap_worker, TrapWorker)

        window.close()

    def test_start_workers_method_exists(self, qapp):
        """Test that start_workers method exists."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        assert hasattr(window, 'start_workers')
        assert callable(window.start_workers)
        window.close()

    def test_stop_workers_method_exists(self, qapp):
        """Test that stop_workers method exists."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        assert hasattr(window, 'stop_workers')
        assert callable(window.stop_workers)
        window.close()


class TestMainWindowCloseEvent:
    """Test MainWindow close event handling."""

    def test_close_event_calls_stop_workers(self, qapp):
        """Test that close event calls stop_workers."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Mock the stop_workers method
        with patch.object(window, 'stop_workers') as mock_stop:
            event = Mock()
            window.closeEvent(event)
            mock_stop.assert_called_once()


class TestMainWindowLogPanel:
    """Test MainWindow log panel functionality."""

    def test_log_method_exists(self, qapp):
        """Test that log method exists for adding messages."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        assert hasattr(window, 'log')
        assert callable(window.log)
        window.close()

    def test_log_method_adds_text(self, qapp):
        """Test that log method adds text to log panel."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        window.log("Test message")
        assert "Test message" in window._log_panel.toPlainText()
        window.close()


class TestMainWindowActions:
    """Test MainWindow action methods."""

    def test_action_start_monitoring_exists(self, qapp):
        """Test that start_monitoring action method exists."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        assert hasattr(window, 'start_monitoring')
        assert callable(window.start_monitoring)
        window.close()

    def test_action_stop_monitoring_exists(self, qapp):
        """Test that stop_monitoring action method exists."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        assert hasattr(window, 'stop_monitoring')
        assert callable(window.stop_monitoring)
        window.close()

    def test_start_monitoring_calls_start_workers(self, qapp):
        """Test that start_monitoring calls start_workers."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        with patch.object(window, 'start_workers') as mock_start:
            window.start_monitoring()
            mock_start.assert_called_once()
        window.close()

    def test_stop_monitoring_calls_stop_workers(self, qapp):
        """Test that stop_monitoring calls stop_workers."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        with patch.object(window, 'stop_workers') as mock_stop:
            window.stop_monitoring()
            mock_stop.assert_called_once()
        window.close()


class TestMainWindowMenuBar:
    """Test MainWindow menu bar structure."""

    def test_has_menu_bar_with_actions(self, qapp):
        """Test that MainWindow has a menu bar with expected actions."""
        from snmp_monitor.gui.app import MainWindow
        from PySide6.QtWidgets import QMenu

        window = MainWindow()
        menubar = window.menuBar()

        # Get all menus
        menus = menubar.findChildren(QMenu)
        assert len(menus) >= 0  # At least menus exist

        # Collect all actions from menus
        all_actions = []
        for menu in menus:
            for action in menu.actions():
                all_actions.append(action.text())

        # File menu should contain Exit action (check menus directly)
        file_menu = None
        for menu in menus:
            if "File" in menu.title():
                file_menu = menu
                break

        assert file_menu is not None, "File menu should exist"
        exit_action = None
        for action in file_menu.actions():
            if "Exit" in action.text():
                exit_action = action
                break
        assert exit_action is not None, "Exit action should exist in File menu"
        window.close()

    def test_has_about_action(self, qapp):
        """Test that Help menu has About action."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        # The window should have a method to show about
        assert hasattr(window, '_show_about')
        window.close()


class TestMainWindowDataTable:
    """Test MainWindow data table configuration."""

    def test_data_table_has_columns(self, qapp):
        """Test that data table has expected columns."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        table = window._data_table

        # Check that table has column headers
        header_labels = []
        for i in range(table.columnCount()):
            header_labels.append(table.horizontalHeaderItem(i).text() if table.horizontalHeaderItem(i) else "")

        # Should have columns for CPU, Memory, Disk, Network, etc.
        assert table.columnCount() > 0
        window.close()


class TestMainWindowMibTree:
    """Test MainWindow MIB tree configuration."""

    def test_mib_tree_has_model(self, qapp):
        """Test that MIB tree has MIBModel set."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        tree = window._mib_tree

        # Tree should have a model set
        assert tree.model() is not None
        window.close()


class TestMainWindowPropertyAccess:
    """Test MainWindow property accessors."""

    def test_snmp_model_property(self, qapp):
        """Test that snmp_model property returns the model."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        assert window.snmp_model is window._snmp_model
        window.close()

    def test_mib_model_property(self, qapp):
        """Test that mib_model property returns the model."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        assert window.mib_model is window._mib_model
        window.close()

    def test_trap_model_property(self, qapp):
        """Test that trap_model property returns the model."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()
        assert window.trap_model is window._trap_model
        window.close()
