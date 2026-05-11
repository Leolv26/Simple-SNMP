"""Trap Record Model for displaying and managing SNMP trap history.

This module provides the TrapModel class which:
- Inherits from QAbstractTableModel for table view display
- Stores trap records with timestamp, source, OID, message, and severity
- Displays 4 columns: Time, Source, OID, Message
- Sorts traps in reverse chronological order (newest first)
- Emits signals when new traps are added
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, Signal


class TrapModel(QAbstractTableModel):
    """Model for displaying SNMP trap history in a table view.

    This model manages a list of trap records suitable for display
    in a Qt QTableView widget.

    Column layout:
        0 - Time: Timestamp when the trap was received
        1 - Source: Source IP address of the trap
        2 - OID: The OID that triggered the trap
        3 - Message: Human-readable trap message

    Internal storage also includes:
        4 - Severity: Trap severity level (debug, info, warning, error, critical)

    Signals:
        trap_added: Emitted when a new trap is added (data: dict)
    """

    # Column constants
    COLUMN_TIME = 0
    COLUMN_SOURCE = 1
    COLUMN_OID = 2
    COLUMN_MESSAGE = 3
    COLUMN_COUNT = 4

    # Column headers (only 4 columns for display)
    HEADERS = ["Time", "Source", "OID", "Message"]

    # Signal emitted when a new trap is added
    trap_added = Signal(dict)

    def __init__(self, parent=None) -> None:
        """Initialize the TrapModel.

        Args:
            parent: Parent QObject.
        """
        super().__init__(parent)
        # Store trap records as list of dictionaries
        # Each record: {timestamp, source, oid, message, severity}
        self._traps: List[Dict[str, Any]] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return the number of rows (trap records).

        Args:
            parent: Parent index (unused for table model).

        Returns:
            Number of trap records.
        """
        if parent.isValid():
            return 0
        return len(self._traps)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return the number of columns.

        Args:
            parent: Parent index (unused for table model).

        Returns:
            Number of columns (always 4 for display).
        """
        if parent.isValid():
            return 0
        return self.COLUMN_COUNT

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Return the data for the given index and role.

        Args:
            index: Model index.
            role: Data role.

        Returns:
            Data for the specified role, or None if no data.
        """
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        row = index.row()
        column = index.column()

        if row < 0 or row >= len(self._traps):
            return None

        trap = self._traps[row]

        if column == self.COLUMN_TIME:
            timestamp = trap.get('timestamp')
            if isinstance(timestamp, datetime):
                return timestamp.strftime("%Y-%m-%d %H:%M:%S")
            return str(timestamp) if timestamp else ""
        elif column == self.COLUMN_SOURCE:
            return trap.get('source', "")
        elif column == self.COLUMN_OID:
            return trap.get('oid', "")
        elif column == self.COLUMN_MESSAGE:
            return trap.get('message', "")

        return None

    def headerData(self, section: int, orientation: int, role: int = Qt.DisplayRole) -> Any:
        """Return the header data for the given section.

        Args:
            section: Section number.
            orientation: Horizontal or Vertical.
            role: Data role.

        Returns:
            Header data or None.
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if 0 <= section < len(self.HEADERS):
                return self.HEADERS[section]

        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Return the item flags for the given index.

        Args:
            index: Model index.

        Returns:
            Item flags.
        """
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def add_trap(self, source: str, oid: str, message: str, severity: str = "info") -> None:
        """Add a new trap record.

        The new trap will be inserted at the beginning of the list
        (newest first) to maintain reverse chronological order.

        Args:
            source: Source IP address or hostname.
            oid: The OID that triggered the trap.
            message: Human-readable trap message.
            severity: Severity level (debug, info, warning, error, critical).
        """
        trap_data = {
            'timestamp': datetime.now(),
            'source': source,
            'oid': oid,
            'message': message,
            'severity': severity
        }

        # Insert at the beginning (newest first)
        self.beginInsertRows(QModelIndex(), 0, 0)
        self._traps.insert(0, trap_data)
        self.endInsertRows()

        # Emit signal
        self.trap_added.emit(trap_data)

    def clear(self) -> None:
        """Remove all trap records."""
        if not self._traps:
            return

        count = len(self._traps)
        self.beginRemoveRows(QModelIndex(), 0, count - 1)
        self._traps.clear()
        self.endRemoveRows()

    def get_traps(self) -> List[Dict[str, Any]]:
        """Get all trap records.

        Returns:
            List of trap record dictionaries.
        """
        # Return a copy to prevent external modification
        return self._traps.copy()

    def get_recent(self, count: int) -> List[Dict[str, Any]]:
        """Get the most recent N trap records.

        Args:
            count: Number of records to return.

        Returns:
            List of the most recent trap records.
        """
        return self._traps[:count]
