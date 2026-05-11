"""Data Table Widget for displaying SNMP OID values.

This module provides the DataTableWidget class which:
- Inherits from QWidget for PySide6 integration
- Uses QTableWidget to display device data (OID, Name, Current Value, Unit)
- Provides OID search functionality with QLineEdit and QPushButton
- Emits signals for OID queries and value updates
"""
import logging
from typing import List, Optional, Tuple

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QPushButton, QLabel
)

logger = logging.getLogger(__name__)


class DataTableWidget(QWidget):
    """Widget for displaying and querying SNMP OID data.

    This widget provides a table view for displaying OID information
    with the following features:
    - Displays OID, Name, Current Value, and Unit columns
    - Provides OID search input and button
    - Emits signals for OID queries and value updates
    - Supports row selection

    Signals:
        oid_query_requested: Emitted when user requests OID query (oid: str)
        oid_value_updated: Emitted when OID value is updated (oid: str, value: object)

    Example:
        >>> widget = DataTableWidget()
        >>> widget.oid_query_requested.connect(lambda oid: print(f"Query: {oid}"))
        >>> widget.update_table([("1.3.6.1.2.1.1.1.0", "sysDescr", "Test", "String")])
    """

    # Signal emitted when user requests OID query
    oid_query_requested = Signal(str)

    # Signal emitted when OID value is updated
    oid_value_updated = Signal(str, object)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the DataTableWidget.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)

        # Setup UI components
        self._setup_ui()

        # Connect signals
        self._connect_signals()

        logger.debug("DataTableWidget initialized")

    def _setup_ui(self) -> None:
        """Setup the user interface components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Search layout
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        # OID label
        self._oid_label = QLabel("OID:")
        self._oid_label.setStyleSheet("font-weight: bold; font-family: Arial, Helvetica, sans-serif;")
        search_layout.addWidget(self._oid_label)

        # OID input field
        self._oid_input = QLineEdit()
        self._oid_input.setPlaceholderText("Enter OID (e.g., 1.3.6.1.2.1.1.1.0)")
        self._oid_input.setMinimumWidth(300)
        search_layout.addWidget(self._oid_input)

        # Search button
        self._search_btn = QPushButton("查询")
        self._search_btn.setToolTip("Search for OID value")
        search_layout.addWidget(self._search_btn)

        # Add stretch to push search components to the left
        search_layout.addStretch()

        # Add search layout to main layout
        main_layout.addLayout(search_layout)

        # Table widget
        self._table_widget = QTableWidget()
        self._setup_table()

        # Add table to main layout
        main_layout.addWidget(self._table_widget)

    def _setup_table(self) -> None:
        """Configure the table widget."""
        # Set column count
        self._table_widget.setColumnCount(4)

        # Set column headers
        headers = ["OID", "名称", "当前值", "单位"]
        self._table_widget.setHorizontalHeaderLabels(headers)

        # Configure table properties
        self._table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self._table_widget.setSelectionMode(QTableWidget.SingleSelection)
        self._table_widget.setAlternatingRowColors(True)
        self._table_widget.setSortingEnabled(True)

        # Configure column resize modes
        header = self._table_widget.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Interactive)  # OID
        header.setSectionResizeMode(1, QHeaderView.Stretch)      # Name
        header.setSectionResizeMode(2, QHeaderView.Stretch)      # Current Value
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Unit

        # Set minimum column widths
        self._table_widget.setColumnWidth(0, 200)
        self._table_widget.setColumnWidth(1, 150)
        self._table_widget.setColumnWidth(2, 150)
        self._table_widget.setColumnWidth(3, 80)

    def _connect_signals(self) -> None:
        """Connect widget signals and slots."""
        # Connect search button click
        self._search_btn.clicked.connect(self._on_search_clicked)

        # Connect input return pressed
        self._oid_input.returnPressed.connect(self._on_search_clicked)

    @Slot()
    def _on_search_clicked(self) -> None:
        """Handle search button click or return key press."""
        oid = self._oid_input.text().strip()
        if oid:
            logger.debug(f"Search clicked for OID: {oid}")
            self.oid_query_requested.emit(oid)

    def search_oid(self, oid: str) -> None:
        """Search for a specific OID.

        Args:
            oid: The OID to search for.
        """
        if oid:
            self._oid_input.setText(oid)
            self.oid_query_requested.emit(oid)

    def update_table(self, data: List[Tuple[str, str, str, str]]) -> None:
        """Update the table with new data.

        This method clears the table and populates it with the provided data.

        Args:
            data: List of tuples (oid, name, value, unit) to display.
        """
        # Clear existing data
        self._table_widget.setRowCount(0)

        # Add new rows
        for oid, name, value, unit in data:
            self._add_row_to_table(oid, name, value, unit)

        logger.debug(f"Table updated with {len(data)} rows")

    def add_row(self, oid: str, name: str, value: str, unit: str) -> None:
        """Add a single row to the table.

        Args:
            oid: The OID value.
            name: The OID name.
            value: The current value.
            unit: The unit of measurement.
        """
        self._add_row_to_table(oid, name, value, unit)

    def _add_row_to_table(self, oid: str, name: str, value: str, unit: str) -> None:
        """Add a row to the table widget.

        Args:
            oid: The OID value.
            name: The OID name.
            value: The current value.
            unit: The unit of measurement.
        """
        row_position = self._table_widget.rowCount()
        self._table_widget.insertRow(row_position)

        # Create table items
        oid_item = QTableWidgetItem(oid)
        oid_item.setFlags(oid_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self._table_widget.setItem(row_position, 0, oid_item)

        name_item = QTableWidgetItem(name)
        name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self._table_widget.setItem(row_position, 1, name_item)

        value_item = QTableWidgetItem(value)
        value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self._table_widget.setItem(row_position, 2, value_item)

        unit_item = QTableWidgetItem(unit)
        unit_item.setFlags(unit_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self._table_widget.setItem(row_position, 3, unit_item)

    def clear_table(self) -> None:
        """Clear all data from the table."""
        self._table_widget.setRowCount(0)
        logger.debug("Table cleared")

    def clear(self) -> None:
        """Clear the table and input field."""
        self.clear_table()
        self._oid_input.clear()

    def update_oid_value(self, oid: str, value: object) -> None:
        """Update the value of a specific OID in the table.

        Args:
            oid: The OID to update.
            value: The new value.
        """
        display_value = self._format_oid_value(value)

        # Find the row with matching OID
        for row in range(self._table_widget.rowCount()):
            item = self._table_widget.item(row, 0)
            if item and item.text() == oid:
                # Update the value column
                value_item = QTableWidgetItem(display_value)
                value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self._table_widget.setItem(row, 2, value_item)

                # Emit signal
                self.oid_value_updated.emit(oid, value)
                logger.debug(f"Updated OID {oid} with value {display_value}")
                return

        self._add_row_to_table(oid, "OID Query Result", display_value, "")
        self.oid_value_updated.emit(oid, value)
        logger.debug(f"Added query result row for OID {oid} with value {display_value}")

    def _format_oid_value(self, value: object) -> str:
        """Format raw SNMP query result for table display.

        Args:
            value: Raw value or SNMPClient.get() result tuple.

        Returns:
            Display string for the value column.
        """
        if (
            isinstance(value, tuple)
            and len(value) == 2
            and isinstance(value[0], tuple)
        ):
            return str(value[1])

        if value is None:
            return "No result"

        return str(value)

    def set_value(self, oid: str, value: object) -> None:
        """Set the value for a specific OID (alias for update_oid_value).

        Args:
            oid: The OID to update.
            value: The new value.
        """
        self.update_oid_value(oid, value)

    def get_selected_oid(self) -> Optional[str]:
        """Get the OID of the currently selected row.

        Returns:
            The selected OID or None if no row is selected.
        """
        selected_rows = self._table_widget.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            item = self._table_widget.item(row, 0)
            if item:
                return item.text()
        return None

    @property
    def table_widget(self) -> QTableWidget:
        """Get the table widget.

        Returns:
            The QTableWidget instance.
        """
        return self._table_widget

    @property
    def oid_input(self) -> QLineEdit:
        """Get the OID input field.

        Returns:
            The QLineEdit instance.
        """
        return self._oid_input

    @property
    def search_button(self) -> QPushButton:
        """Get the search button.

        Returns:
            The QPushButton instance.
        """
        return self._search_btn
