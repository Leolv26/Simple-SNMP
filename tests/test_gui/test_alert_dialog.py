"""Tests for AlertConfigDialog class in alert_dialog.py."""
import sys
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

# Create a temporary config file for testing
@pytest.fixture(scope="module")
def temp_config():
    """Create a temporary config file for testing."""
    content = """# SNMP Agent Configuration
snmp_agent:
  host: "0.0.0.0"
  port: 161
  community: "public"

# NMS Configuration
nms:
  agent_host: "127.0.0.1"
  trap_port: 162

# Alert Thresholds
alert_thresholds:
  cpu: 80
  memory: 85
  disk: 90
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(content)
        temp_path = f.name
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for testing."""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestAlertConfigDialogImports:
    """Test that AlertConfigDialog can be imported correctly."""

    def test_alert_dialog_module_import(self):
        """Test that alert_dialog module can be imported."""
        from snmp_monitor.gui.views import alert_dialog
        assert alert_dialog is not None

    def test_alert_config_dialog_class_exists(self):
        """Test that AlertConfigDialog class exists in alert_dialog module."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        assert AlertConfigDialog is not None

    def test_alert_config_dialog_import_from_views(self):
        """Test that AlertConfigDialog can be imported from views package."""
        from snmp_monitor.gui.views import AlertConfigDialog
        assert AlertConfigDialog is not None


class TestAlertConfigDialogInheritance:
    """Test AlertConfigDialog class inheritance."""

    def test_alert_config_dialog_inherits_qdialog(self, qapp):
        """Test that AlertConfigDialog inherits from QDialog."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        from PySide6.QtWidgets import QDialog
        assert issubclass(AlertConfigDialog, QDialog)

    def test_alert_config_dialog_can_be_instantiated(self, qapp):
        """Test that AlertConfigDialog can be instantiated."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        dialog = AlertConfigDialog()
        assert dialog is not None


class TestAlertConfigDialogComponents:
    """Test AlertConfigDialog internal components."""

    def test_widget_has_cpu_spinbox(self, qapp):
        """Test that dialog has a CPU threshold spinbox."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        dialog = AlertConfigDialog()
        assert hasattr(dialog, '_cpu_spinbox')
        from PySide6.QtWidgets import QSpinBox
        assert isinstance(dialog._cpu_spinbox, QSpinBox)

    def test_widget_has_memory_spinbox(self, qapp):
        """Test that dialog has a Memory threshold spinbox."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        dialog = AlertConfigDialog()
        assert hasattr(dialog, '_memory_spinbox')
        from PySide6.QtWidgets import QSpinBox
        assert isinstance(dialog._memory_spinbox, QSpinBox)

    def test_widget_has_disk_spinbox(self, qapp):
        """Test that dialog has a Disk threshold spinbox."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        dialog = AlertConfigDialog()
        assert hasattr(dialog, '_disk_spinbox')
        from PySide6.QtWidgets import QSpinBox
        assert isinstance(dialog._disk_spinbox, QSpinBox)

    def test_widget_has_ok_button(self, qapp):
        """Test that dialog has an OK button."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        dialog = AlertConfigDialog()
        assert hasattr(dialog, '_ok_btn')
        from PySide6.QtWidgets import QPushButton
        assert isinstance(dialog._ok_btn, QPushButton)

    def test_widget_has_cancel_button(self, qapp):
        """Test that dialog has a Cancel button."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        dialog = AlertConfigDialog()
        assert hasattr(dialog, '_cancel_btn')
        from PySide6.QtWidgets import QPushButton
        assert isinstance(dialog._cancel_btn, QPushButton)


class TestAlertConfigDialogSpinboxRanges:
    """Test AlertConfigDialog spinbox ranges."""

    def test_cpu_spinbox_range(self, qapp):
        """Test that CPU spinbox has range 0-100."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        dialog = AlertConfigDialog()
        assert dialog._cpu_spinbox.minimum() == 0
        assert dialog._cpu_spinbox.maximum() == 100

    def test_memory_spinbox_range(self, qapp):
        """Test that Memory spinbox has range 0-100."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        dialog = AlertConfigDialog()
        assert dialog._memory_spinbox.minimum() == 0
        assert dialog._memory_spinbox.maximum() == 100

    def test_disk_spinbox_range(self, qapp):
        """Test that Disk spinbox has range 0-100."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        dialog = AlertConfigDialog()
        assert dialog._disk_spinbox.minimum() == 0
        assert dialog._disk_spinbox.maximum() == 100


class TestAlertConfigDialogButtons:
    """Test AlertConfigDialog button properties."""

    def test_ok_button_text(self, qapp):
        """Test that OK button has correct text."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        dialog = AlertConfigDialog()
        assert dialog._ok_btn.text() == "确定"

    def test_cancel_button_text(self, qapp):
        """Test that Cancel button has correct text."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        dialog = AlertConfigDialog()
        assert dialog._cancel_btn.text() == "取消"


class TestAlertConfigDialogSignals:
    """Test AlertConfigDialog signals."""

    def test_dialog_has_thresholds_changed_signal(self, qapp):
        """Test that dialog has thresholds_changed signal."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        from PySide6.QtCore import Signal
        dialog = AlertConfigDialog()
        assert hasattr(dialog, 'thresholds_changed')
        signal = getattr(dialog, 'thresholds_changed', None)
        assert signal is not None
        assert isinstance(signal, Signal)

    def test_ok_button_emits_signal_on_click(self, qapp):
        """Test that OK button click emits thresholds_changed signal."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        dialog = AlertConfigDialog()

        signal_received = []

        def on_thresholds_changed(thresholds):
            signal_received.append(thresholds)

        dialog.thresholds_changed.connect(on_thresholds_changed)

        # Click OK button
        dialog._ok_btn.click()

        # Verify signal was emitted
        assert len(signal_received) == 1
        # Verify the signal contains the expected keys
        assert 'cpu' in signal_received[0]
        assert 'memory' in signal_received[0]
        assert 'disk' in signal_received[0]


class TestAlertConfigDialogLayout:
    """Test AlertConfigDialog layout."""

    def test_dialog_has_layout(self, qapp):
        """Test that dialog has a layout."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        dialog = AlertConfigDialog()
        assert dialog.layout() is not None
        from PySide6.QtWidgets import QLayout
        assert isinstance(dialog.layout(), QLayout)


class TestAlertConfigDialogDialogFlags:
    """Test AlertConfigDialog dialog flags."""

    def test_dialog_is_modal(self, qapp):
        """Test that dialog is modal."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        dialog = AlertConfigDialog()
        # Modal dialogs should have the Modal flag set
        assert dialog.isModal()


class TestAlertConfigDialogMethods:
    """Test AlertConfigDialog methods."""

    def test_get_thresholds_method_exists(self, qapp):
        """Test that get_thresholds method exists."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        dialog = AlertConfigDialog()
        assert hasattr(dialog, 'get_thresholds')
        assert callable(dialog.get_thresholds)

    def test_get_thresholds_returns_dict(self, qapp):
        """Test that get_thresholds returns a dictionary."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        dialog = AlertConfigDialog()
        thresholds = dialog.get_thresholds()
        assert isinstance(thresholds, dict)

    def test_get_thresholds_contains_all_keys(self, qapp):
        """Test that get_thresholds returns dict with cpu, memory, disk keys."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        dialog = AlertConfigDialog()
        thresholds = dialog.get_thresholds()
        assert 'cpu' in thresholds
        assert 'memory' in thresholds
        assert 'disk' in thresholds

    def test_get_thresholds_values_in_range(self, qapp):
        """Test that get_thresholds values are in valid range 0-100."""
        from snmp_monitor.gui.views.alert_dialog import AlertConfigDialog
        dialog = AlertConfigDialog()
        thresholds = dialog.get_thresholds()
        for key in ['cpu', 'memory', 'disk']:
            assert 0 <= thresholds[key] <= 100
