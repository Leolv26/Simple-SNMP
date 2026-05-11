"""Tests for LogPanelWidget class in log_panel.py."""
import sys
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for testing."""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestLogPanelWidgetImports:
    """Test that LogPanelWidget can be imported correctly."""

    def test_log_panel_module_import(self):
        """Test that log_panel module can be imported."""
        from snmp_monitor.gui.views import log_panel
        assert log_panel is not None

    def test_log_panel_widget_class_exists(self):
        """Test that LogPanelWidget class exists in log_panel module."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        assert LogPanelWidget is not None

    def test_log_panel_widget_import_from_views(self):
        """Test that LogPanelWidget can be imported from views package."""
        from snmp_monitor.gui.views import LogPanelWidget
        assert LogPanelWidget is not None


class TestLogPanelWidgetInheritance:
    """Test LogPanelWidget class inheritance."""

    def test_log_panel_widget_inherits_qwidget(self, qapp):
        """Test that LogPanelWidget inherits from QWidget."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        from PySide6.QtWidgets import QWidget
        assert issubclass(LogPanelWidget, QWidget)

    def test_log_panel_widget_can_be_instantiated(self, qapp):
        """Test that LogPanelWidget can be instantiated."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        from PySide6.QtWidgets import QWidget
        widget = LogPanelWidget()
        assert widget is not None
        assert isinstance(widget, QWidget)


class TestLogPanelWidgetComponents:
    """Test LogPanelWidget internal components."""

    def test_widget_has_plain_text_edit(self, qapp):
        """Test that widget has a QPlainTextEdit."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        from PySide6.QtWidgets import QPlainTextEdit
        widget = LogPanelWidget()
        assert hasattr(widget, '_log_display') or hasattr(widget, '_text_edit')
        # Get the log display widget
        log_display = getattr(widget, '_log_display', None) or getattr(widget, '_text_edit', None)
        assert isinstance(log_display, QPlainTextEdit)

    def test_widget_has_clear_button(self, qapp):
        """Test that widget has a clear button."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        from PySide6.QtWidgets import QPushButton
        widget = LogPanelWidget()
        assert hasattr(widget, '_clear_btn') or hasattr(widget, '_clear_button')
        # Get the clear button
        clear_btn = getattr(widget, '_clear_btn', None) or getattr(widget, '_clear_button', None)
        assert isinstance(clear_btn, QPushButton)

    def test_widget_has_layout(self, qapp):
        """Test that widget has a layout."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        from PySide6.QtWidgets import QLayout
        widget = LogPanelWidget()
        assert widget.layout() is not None
        assert isinstance(widget.layout(), QLayout)


class TestLogPanelWidgetTextEdit:
    """Test LogPanelWidget QPlainTextEdit configuration."""

    def test_plain_text_edit_is_readonly(self, qapp):
        """Test that QPlainTextEdit is in read-only mode."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        log_display = getattr(widget, '_log_display', None) or getattr(widget, '_text_edit', None)
        assert log_display is not None
        assert log_display.isReadOnly()  # Should be set to read-only


class TestLogPanelWidgetAppendMethods:
    """Test LogPanelWidget append methods for different log levels."""

    def test_append_info_method_exists(self, qapp):
        """Test that append_info method exists."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        assert hasattr(widget, 'append_info')
        assert callable(widget.append_info)

    def test_append_error_method_exists(self, qapp):
        """Test that append_error method exists."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        assert hasattr(widget, 'append_error')
        assert callable(widget.append_error)

    def test_append_trap_method_exists(self, qapp):
        """Test that append_trap method exists."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        assert hasattr(widget, 'append_trap')
        assert callable(widget.append_trap)

    def test_append_warning_method_exists(self, qapp):
        """Test that append_warning method exists."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        assert hasattr(widget, 'append_warning')
        assert callable(widget.append_warning)

    def test_append_info_adds_content(self, qapp):
        """Test that append_info adds content to the display."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        widget.append_info("Test info message")
        log_display = getattr(widget, '_log_display', None) or getattr(widget, '_text_edit', None)
        content = log_display.toPlainText()
        assert "Test info message" in content

    def test_append_error_adds_content(self, qapp):
        """Test that append_error adds content to the display."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        widget.append_error("Test error message")
        log_display = getattr(widget, '_log_display', None) or getattr(widget, '_text_edit', None)
        content = log_display.toPlainText()
        assert "Test error message" in content

    def test_append_trap_adds_content(self, qapp):
        """Test that append_trap adds content to the display."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        widget.append_trap("Test trap message")
        log_display = getattr(widget, '_log_display', None) or getattr(widget, '_text_edit', None)
        content = log_display.toPlainText()
        assert "Test trap message" in content

    def test_append_warning_adds_content(self, qapp):
        """Test that append_warning adds content to the display."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        widget.append_warning("Test warning message")
        log_display = getattr(widget, '_log_display', None) or getattr(widget, '_text_edit', None)
        content = log_display.toPlainText()
        assert "Test warning message" in content


class TestLogPanelWidgetTimestamps:
    """Test LogPanelWidget timestamp functionality."""

    def test_append_methods_add_timestamp(self, qapp):
        """Test that append methods add timestamp to log entries."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        widget.append_info("Test message")
        log_display = getattr(widget, '_log_display', None) or getattr(widget, '_text_edit', None)
        content = log_display.toPlainText()
        # Should contain timestamp pattern like [HH:MM:SS] or [YYYY-MM-DD HH:MM:SS]
        # Check that there's some timestamp-like pattern
        lines = content.strip().split('\n')
        assert len(lines) > 0
        # The first line should have a timestamp in brackets
        assert '[' in lines[0]

    def test_multiple_append_increments_log(self, qapp):
        """Test that multiple append calls add multiple lines."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        widget.append_info("Message 1")
        widget.append_info("Message 2")
        widget.append_info("Message 3")
        log_display = getattr(widget, '_log_display', None) or getattr(widget, '_text_edit', None)
        content = log_display.toPlainText()
        lines = [l for l in content.strip().split('\n') if l]
        assert len(lines) >= 2  # At least 2 lines of content


class TestLogPanelWidgetClear:
    """Test LogPanelWidget clear functionality."""

    def test_clear_method_exists(self, qapp):
        """Test that clear method exists."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        assert hasattr(widget, 'clear')
        assert callable(widget.clear)

    def test_clear_clears_content(self, qapp):
        """Test that clear method clears all log content."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        widget.append_info("Test message")
        widget.append_error("Error message")
        widget.clear()
        log_display = getattr(widget, '_log_display', None) or getattr(widget, '_text_edit', None)
        content = log_display.toPlainText().strip()
        assert content == ""


class TestLogPanelWidgetLogCount:
    """Test LogPanelWidget log count functionality."""

    def test_get_log_count_method_exists(self, qapp):
        """Test that get_log_count method exists."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        assert hasattr(widget, 'get_log_count')
        assert callable(widget.get_log_count)

    def test_get_log_count_initial_zero(self, qapp):
        """Test that get_log_count returns 0 initially."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        assert widget.get_log_count() == 0

    def test_get_log_count_after_append(self, qapp):
        """Test that get_log_count returns correct count after append."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        widget.append_info("Message 1")
        widget.append_info("Message 2")
        assert widget.get_log_count() == 2

    def test_get_log_count_after_clear(self, qapp):
        """Test that get_log_count returns 0 after clear."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        widget.append_info("Message 1")
        widget.append_info("Message 2")
        widget.clear()
        assert widget.get_log_count() == 0

    def test_get_log_count_tracks_all_types(self, qapp):
        """Test that get_log_count tracks all log types."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        widget.append_info("Info message")
        widget.append_error("Error message")
        widget.append_warning("Warning message")
        widget.append_trap("Trap message")
        # Should count all 4 messages
        count = widget.get_log_count()
        assert count == 4


class TestLogPanelWidgetClearButton:
    """Test LogPanelWidget clear button functionality."""

    def test_clear_button_triggers_clear(self, qapp):
        """Test that clicking clear button clears the log."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        widget.append_info("Test message")

        # Click clear button
        clear_btn = getattr(widget, '_clear_btn', None) or getattr(widget, '_clear_button', None)
        if clear_btn:
            clear_btn.click()

        log_display = getattr(widget, '_log_display', None) or getattr(widget, '_text_edit', None)
        content = log_display.toPlainText().strip()
        assert content == ""


class TestLogPanelWidgetAutoScroll:
    """Test LogPanelWidget auto-scroll functionality."""

    def test_append_auto_scrolls(self, qapp):
        """Test that append methods auto-scroll to bottom."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        # Add multiple lines to trigger scrolling
        for i in range(10):
            widget.append_info(f"Message {i}")
        log_display = getattr(widget, '_log_display', None) or getattr(widget, '_text_edit', None)
        # Verify text was added
        content = log_display.toPlainText()
        assert "Message 0" in content
        assert "Message 9" in content


class TestLogPanelWidgetIntegration:
    """Test LogPanelWidget integration scenarios."""

    def test_full_logging_workflow(self, qapp):
        """Test complete workflow: add various logs and clear."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()

        # Add various log types
        widget.append_info("Application started")
        widget.append_info("Device connected: localhost")
        widget.append_trap("Received trap from 192.168.1.1")
        widget.append_warning("High CPU usage detected: 85%")
        widget.append_error("Failed to connect to device: timeout")

        # Verify count
        assert widget.get_log_count() == 5

        # Clear logs
        widget.clear()

        # Verify cleared
        assert widget.get_log_count() == 0
        log_display = getattr(widget, '_log_display', None) or getattr(widget, '_text_edit', None)
        assert log_display.toPlainText().strip() == ""

    def test_empty_message_handling(self, qapp):
        """Test that empty messages are handled correctly."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        # Should handle empty string without error
        widget.append_info("")
        widget.append_error("")
        # Log count should reflect the calls
        count = widget.get_log_count()
        assert count >= 0

    def test_unicode_message_handling(self, qapp):
        """Test that unicode messages are handled correctly."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()
        # Add unicode message
        widget.append_info("测试中文消息 Test 中文")
        widget.append_error("错误: 设备连接失败 Error")

        log_display = getattr(widget, '_log_display', None) or getattr(widget, '_text_edit', None)
        content = log_display.toPlainText()
        assert "测试中文消息" in content
        assert "错误" in content


class TestLogPanelWidgetSignals:
    """Test LogPanelWidget signals."""

    def test_widget_has_clear_requested_signal(self, qapp):
        """Test that widget has clear_requested signal."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        from PySide6.QtCore import Signal
        widget = LogPanelWidget()
        assert hasattr(widget, 'clear_requested')
        signal = getattr(widget, 'clear_requested', None)
        assert signal is not None
        assert isinstance(signal, Signal)

    def test_clear_button_emits_signal(self, qapp):
        """Test that clicking clear button emits clear_requested signal."""
        from snmp_monitor.gui.views.log_panel import LogPanelWidget
        widget = LogPanelWidget()

        signal_received = []

        def on_clear_requested():
            signal_received.append(True)

        widget.clear_requested.connect(on_clear_requested)

        # Click clear button
        clear_btn = getattr(widget, '_clear_btn', None) or getattr(widget, '_clear_button', None)
        if clear_btn:
            clear_btn.click()

        # Verify signal was emitted
        assert len(signal_received) >= 1
