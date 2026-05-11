"""Log panel widget for displaying application logs.

This module provides the LogPanelWidget class which:
- Inherits from QWidget for PySide6 integration
- Displays logs using QPlainTextEdit with color-coded log levels
- Supports timestamps for each log entry
- Provides methods for different log levels (info, error, warning, trap)
- Includes a clear button to clear all logs
"""
import logging
from datetime import datetime
from typing import Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor, QTextCharFormat, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPlainTextEdit, QPushButton, QLabel
)

logger = logging.getLogger(__name__)


class LogPanelWidget(QWidget):
    """Log panel widget for displaying application logs.

    This widget provides a scrollable log display with color-coded
    log levels and timestamps. It supports four log levels:
    - INFO (black) - General information
    - ERROR (red) - Error messages
    - WARNING (orange) - Warning messages
    - TRAP (purple/blue) - Trap messages

    Signals:
        clear_requested: Emitted when the clear button is clicked.

    Attributes:
        _log_display: QPlainTextEdit for displaying logs.
        _clear_btn: QPushButton for clearing logs.
        _log_count: Integer counter for total log entries.
        _info_color: QColor for INFO level text.
        _error_color: QColor for ERROR level text.
        _warning_color: QColor for WARNING level text.
        _trap_color: QColor for TRAP level text.

    Example:
        >>> widget = LogPanelWidget()
        >>> widget.append_info("Application started")
        >>> widget.append_error("Connection failed")
        >>> widget.append_trap("Trap received from 192.168.1.1")
        >>> widget.append_warning("High CPU usage detected")
        >>> count = widget.get_log_count()
        >>> widget.clear()
    """

    # Signals
    clear_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the LogPanelWidget.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)

        # Log count
        self._log_count: int = 0

        # Color definitions for different log levels
        self._info_color = QColor(0, 0, 0)      # Black
        self._error_color = QColor(200, 0, 0)    # Red
        self._warning_color = QColor(255, 140, 0)  # Orange/Dark Orange
        self._trap_color = QColor(128, 0, 128)   # Purple

        # Setup UI
        self._setup_ui()

        logger.debug("LogPanelWidget initialized")

    def _setup_ui(self) -> None:
        """Setup the widget UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Header layout with title and clear button
        header_layout = QHBoxLayout()
        header_layout.setSpacing(5)

        # Title label
        title_label = QLabel("日志面板")
        title_font = QFont()
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        # Spacer
        header_layout.addStretch()

        # Clear button
        self._clear_btn = QPushButton("清空")
        self._clear_btn.setMaximumWidth(60)
        self._clear_btn.clicked.connect(self._on_clear_clicked)
        header_layout.addWidget(self._clear_btn)

        main_layout.addLayout(header_layout)

        # Log display (QPlainTextEdit)
        self._log_display = QPlainTextEdit()
        self._log_display.setReadOnly(True)
        self._log_display.setMaximumBlockCount(1000)  # Limit to last 1000 lines
        self._log_display.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        main_layout.addWidget(self._log_display)

    def _on_clear_clicked(self) -> None:
        """Handle clear button click."""
        self.clear_requested.emit()
        self.clear()

    def _format_timestamp(self) -> str:
        """Get current timestamp in format [HH:MM:SS].

        Returns:
            Formatted timestamp string.
        """
        return datetime.now().strftime("%H:%M:%S")

    def _append_log(self, level: str, message: str, color: QColor) -> None:
        """Append a log message with given level and color.

        Args:
            level: Log level string (INFO, ERROR, etc.).
            message: Log message content.
            color: QColor for the text.
        """
        timestamp = self._format_timestamp()
        formatted_message = f"[{timestamp}] [{level}] {message}"

        # Create text format with color
        char_format = QTextCharFormat()
        char_format.setForeground(color)

        # Get cursor and append with formatting
        cursor = self._log_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(formatted_message + "\n", char_format)

        # Increment log count
        self._log_count += 1

        # Auto-scroll to bottom
        self._log_display.verticalScrollBar().setValue(
            self._log_display.verticalScrollBar().maximum()
        )

    def append_info(self, message: str) -> None:
        """Append an INFO level log message.

        Args:
            message: The log message to append.

        Example:
            >>> widget.append_info("Application started successfully")
        """
        self._append_log("INFO", message, self._info_color)
        logger.info(message)

    def append_error(self, message: str) -> None:
        """Append an ERROR level log message.

        Args:
            message: The log message to append.

        Example:
            >>> widget.append_error("Failed to connect to device")
        """
        self._append_log("ERROR", message, self._error_color)
        logger.error(message)

    def append_trap(self, message: str) -> None:
        """Append a TRAP level log message.

        Args:
            message: The log message to append.

        Example:
            >>> widget.append_trap("Received trap from 192.168.1.1")
        """
        self._append_log("TRAP", message, self._trap_color)
        logger.debug(f"Trap: {message}")

    def append_warning(self, message: str) -> None:
        """Append a WARNING level log message.

        Args:
            message: The log message to append.

        Example:
            >>> widget.append_warning("High CPU usage detected: 85%")
        """
        self._append_log("WARN", message, self._warning_color)
        logger.warning(message)

    def clear(self) -> None:
        """Clear all log entries from the display.

        This method clears the QPlainTextEdit content and resets
        the log counter to zero.

        Example:
            >>> widget.clear()
        """
        self._log_display.clear()
        self._log_count = 0
        logger.debug("Log panel cleared")

    def get_log_count(self) -> int:
        """Get the current number of log entries.

        Returns:
            The number of log entries that have been added.

        Example:
            >>> widget.append_info("Message 1")
            >>> widget.append_info("Message 2")
            >>> widget.get_log_count()
            2
        """
        return self._log_count

    @property
    def log_display(self) -> QPlainTextEdit:
        """Get the QPlainTextEdit widget for log display.

        Returns:
            The QPlainTextEdit widget.
        """
        return self._log_display

    @property
    def clear_button(self) -> QPushButton:
        """Get the clear button widget.

        Returns:
            The QPushButton for clearing logs.
        """
        return self._clear_btn
