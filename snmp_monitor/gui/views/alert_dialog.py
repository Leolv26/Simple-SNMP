"""Alert configuration dialog for setting SNMP trap thresholds.

This module provides the AlertConfigDialog class which:
- Inherits from QDialog for modal dialog behavior
- Provides spinboxes for configuring CPU, memory, and disk thresholds
- Emits thresholds_changed signal when OK button is clicked
- Supports retrieving current threshold values
"""
import logging
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QPushButton,
    QWidget,
)

logger = logging.getLogger(__name__)


class AlertConfigDialog(QDialog):
    """Dialog for configuring SNMP trap alert thresholds.

    This dialog allows users to set thresholds for CPU, memory, and disk
    usage. When the OK button is clicked, it emits the thresholds_changed
    signal with a dictionary containing the new threshold values.

    Signals:
        thresholds_changed(dict): Emitted when OK is clicked, contains
            {'cpu': int, 'memory': int, 'disk': int}

    Attributes:
        _cpu_spinbox: SpinBox for CPU threshold (0-100%).
        _memory_spinbox: SpinBox for memory threshold (0-100%).
        _disk_spinbox: SpinBox for disk threshold (0-100%).
        _ok_btn: OK button to confirm changes.
        _cancel_btn: Cancel button to discard changes.

    Example:
        >>> dialog = AlertConfigDialog()
        >>> dialog.thresholds_changed.connect(lambda t: print(t))
        >>> if dialog.exec() == QDialog.Accepted:
        ...     thresholds = dialog.get_thresholds()
    """

    # Signal emitted when thresholds are changed
    thresholds_changed = Signal(dict)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the AlertConfigDialog.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)

        # Set dialog properties
        self.setWindowTitle("配置告警阈值")
        self.setModal(True)

        # Setup UI components
        self._setup_ui()

        logger.debug("AlertConfigDialog initialized")

    def _setup_ui(self) -> None:
        """Setup the dialog UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)

        # CPU threshold row
        cpu_layout = QHBoxLayout()
        cpu_label = QLabel("CPU 阈值 (%):")
        self._cpu_spinbox = QSpinBox()
        self._cpu_spinbox.setRange(0, 100)
        self._cpu_spinbox.setSuffix(" %")
        cpu_layout.addWidget(cpu_label)
        cpu_layout.addWidget(self._cpu_spinbox)
        main_layout.addLayout(cpu_layout)

        # Memory threshold row
        memory_layout = QHBoxLayout()
        memory_label = QLabel("内存阈值 (%):")
        self._memory_spinbox = QSpinBox()
        self._memory_spinbox.setRange(0, 100)
        self._memory_spinbox.setSuffix(" %")
        memory_layout.addWidget(memory_label)
        memory_layout.addWidget(self._memory_spinbox)
        main_layout.addLayout(memory_layout)

        # Disk threshold row
        disk_layout = QHBoxLayout()
        disk_label = QLabel("磁盘阈值 (%):")
        self._disk_spinbox = QSpinBox()
        self._disk_spinbox.setRange(0, 100)
        self._disk_spinbox.setSuffix(" %")
        disk_layout.addWidget(disk_label)
        disk_layout.addWidget(self._disk_spinbox)
        main_layout.addLayout(disk_layout)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self._ok_btn = QPushButton("确定")
        self._cancel_btn = QPushButton("取消")
        self._ok_btn.clicked.connect(self._on_ok_clicked)
        self._cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self._ok_btn)
        button_layout.addWidget(self._cancel_btn)
        main_layout.addLayout(button_layout)

    def _on_ok_clicked(self) -> None:
        """Handle OK button click."""
        thresholds = self.get_thresholds()
        self.thresholds_changed.emit(thresholds)
        self.accept()

    def get_thresholds(self) -> dict:
        """Get the current threshold values.

        Returns:
            Dictionary containing 'cpu', 'memory', and 'disk' threshold values.

        Example:
            >>> dialog = AlertConfigDialog()
            >>> thresholds = dialog.get_thresholds()
            >>> print(thresholds)
            {'cpu': 80, 'memory': 85, 'disk': 90}
        """
        return {
            'cpu': self._cpu_spinbox.value(),
            'memory': self._memory_spinbox.value(),
            'disk': self._disk_spinbox.value(),
        }

    def set_thresholds(self, cpu: Optional[int] = None,
                       memory: Optional[int] = None,
                       disk: Optional[int] = None) -> None:
        """Set the threshold values.

        Args:
            cpu: CPU threshold value (0-100).
            memory: Memory threshold value (0-100).
            disk: Disk threshold value (0-100).

        Example:
            >>> dialog = AlertConfigDialog()
            >>> dialog.set_thresholds(cpu=80, memory=85, disk=90)
        """
        if cpu is not None:
            self._cpu_spinbox.setValue(cpu)
        if memory is not None:
            self._memory_spinbox.setValue(memory)
        if disk is not None:
            self._disk_spinbox.setValue(disk)
