"""Device Tree Widget for displaying MIB OID hierarchy.

This module provides the DeviceTreeWidget class which:
- Inherits from QWidget for PySide6 integration
- Displays MIB tree structure using QTreeView
- Integrates with MIBModel for data display
- Supports expand/collapse nodes
- Emits oid_selected signal on node selection
"""
import logging
from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTreeView, QPushButton, QLabel, QHeaderView
)

from snmp_monitor.gui.models.mib_model import MIBModel

logger = logging.getLogger(__name__)


class DeviceTreeWidget(QWidget):
    """Widget for browsing MIB OID tree.

    This widget provides a tree view for displaying the hierarchical
    structure of MIB OIDs with the following features:
    - Displays OID, Name, Value, and Type columns
    - Supports expand/collapse of nodes
    - Emits oid_selected signal when a node is selected
    - Provides refresh button to reload MIB data

    Signals:
        oid_selected: Emitted when an OID is selected (oid: str)

    Example:
        >>> widget = DeviceTreeWidget()
        >>> widget.oid_selected.connect(lambda oid: print(f"Selected: {oid}"))
    """

    # Signal emitted when an OID is selected
    oid_selected = Signal(str)

    def __init__(self, model: Optional[MIBModel] = None, parent: Optional[QWidget] = None) -> None:
        """Initialize the DeviceTreeWidget.

        Args:
            model: Optional MIBModel to use. If not provided, creates a new one.
            parent: Optional parent widget.
        """
        super().__init__(parent)

        # Use provided model or create new one
        self._model = model if model is not None else MIBModel()

        # Setup UI components
        self._setup_ui()

        # Connect signals
        self._connect_signals()

        logger.debug("DeviceTreeWidget initialized")

    def _setup_ui(self) -> None:
        """Setup the user interface components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Title label
        title_layout = QHBoxLayout()
        self._title_label = QLabel("MIB 浏览器")
        self._title_label.setStyleSheet("font-weight: bold; font-size: 14px; font-family: Arial, Helvetica, sans-serif;")
        title_layout.addWidget(self._title_label)
        title_layout.addStretch()

        # Refresh button
        self._refresh_btn = QPushButton("刷新")
        self._refresh_btn.setToolTip("刷新 MIB 数据")
        title_layout.addWidget(self._refresh_btn)

        # Add title layout
        main_layout.addLayout(title_layout)

        # Tree view
        self._tree_view = QTreeView()
        self._tree_view.setModel(self._model)

        # Configure tree view
        self._tree_view.setAlternatingRowColors(True)
        self._tree_view.setSelectionBehavior(QTreeView.SelectRows)
        self._tree_view.setSelectionMode(QTreeView.SingleSelection)
        self._tree_view.setSortingEnabled(True)

        # Configure column widths
        header = self._tree_view.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # OID
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Name
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Value
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Type

        # Set column minimum widths
        self._tree_view.setColumnWidth(0, 200)
        self._tree_view.setColumnWidth(1, 150)
        self._tree_view.setColumnWidth(2, 150)
        self._tree_view.setColumnWidth(3, 80)

        # Add tree view to layout
        main_layout.addWidget(self._tree_view)

    def _connect_signals(self) -> None:
        """Connect widget signals and slots."""
        # Connect refresh button
        self._refresh_btn.clicked.connect(self.refresh)

        # Connect tree view selection to oid_selected signal
        self._tree_view.doubleClicked.connect(self._on_double_click)

    def _on_double_click(self, index) -> None:
        """Handle double-click on tree view item.

        Args:
            index: The model index of the clicked item.
        """
        if not index.isValid():
            return

        node = index.internalPointer()
        if node and node.oid:
            logger.debug(f"Node double-clicked: {node.oid}")
            self.oid_selected.emit(node.oid)

    @Slot()
    def refresh(self) -> None:
        """Refresh the MIB tree data.

        This method is called when the refresh button is clicked.
        It clears the model and reloads the MIB data.
        """
        logger.debug("Refreshing MIB tree")
        self._model.clear()
        self._model.beginResetModel()
        self._model.endResetModel()

        # Load default MIB data (MIB-II system group as example)
        self._load_default_mib_data()

    def _load_default_mib_data(self) -> None:
        """Load default MIB data for demonstration."""
        # Add system group root
        system_idx = self._model.add_oid("1.3.6.1.2.1.1", "system", "System Group")

        # Add system group children
        self._model.add_oid("1.3.6.1.2.1.1.1.0", "sysDescr", "SNMP Agent",
                            parent=system_idx)
        self._model.add_oid("1.3.6.1.2.1.1.3.0", "sysUpTime", "0",
                            parent=system_idx)
        self._model.add_oid("1.3.6.1.2.1.1.4.0", "sysContact", "admin@example.com",
                            parent=system_idx)
        self._model.add_oid("1.3.6.1.2.1.1.5.0", "sysName", "localhost",
                            parent=system_idx)
        self._model.add_oid("1.3.6.1.2.1.1.6.0", "sysLocation", "Unknown",
                            parent=system_idx)

        # Add interfaces group root
        if_idx = self._model.add_oid("1.3.6.1.2.1.2", "interfaces", "Interfaces Group")

        # Add some interface entries
        self._model.add_oid("1.3.6.1.2.1.2.1.0", "ifNumber", "2",
                            parent=if_idx)

        # Expand system node by default
        system_model_idx = self._model.index(0, 0)
        if system_model_idx.isValid():
            self._tree_view.expand(system_model_idx)

    def load_mib_data(self, oids: list) -> None:
        """Load MIB data from a list of OIDs.

        Args:
            oids: List of tuples (oid, name, value, type) to load.
        """
        self._model.clear()
        for oid, name, value, oid_type in oids:
            self._model.add_oid(oid, name, value, oid_type)
        logger.debug(f"Loaded {len(oids)} OIDs into tree")

    @property
    def tree_view(self) -> QTreeView:
        """Get the tree view widget.

        Returns:
            The QTreeView widget.
        """
        return self._tree_view

    @property
    def model(self) -> MIBModel:
        """Get the MIB model.

        Returns:
            The MIBModel instance.
        """
        return self._model

    @property
    def refresh_button(self) -> QPushButton:
        """Get the refresh button.

        Returns:
            The refresh QPushButton widget.
        """
        return self._refresh_btn
