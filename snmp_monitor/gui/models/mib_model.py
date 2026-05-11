"""MIB Tree Model for displaying SNMP OID hierarchy.

This module provides the MIBModel class which:
- Inherits from QAbstractItemModel for QTreeView display
- Manages OID tree structure with parent-child relationships
- Supports adding, removing, and updating OID nodes
- Provides data for display in Qt views
"""
from typing import Optional, List, Any, Tuple
from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt


class MIBNode:
    """Represents a node in the MIB tree.

    Attributes:
        oid: The OID string (e.g., "1.3.6.1.2.1.1.1.0")
        name: Human-readable name (e.g., "sysDescr")
        value: Current value of the OID
        oid_type: SNMP data type (e.g., "String", "Integer", "Gauge")
        parent: Parent MIBNode or None for root nodes
        children: List of child MIBNode objects
    """

    def __init__(
        self,
        oid: str,
        name: str = "",
        value: Any = None,
        oid_type: str = "String",
        parent: Optional["MIBNode"] = None
    ) -> None:
        """Initialize a MIB node.

        Args:
            oid: The OID string.
            name: Human-readable name.
            value: Current value.
            oid_type: SNMP data type.
            parent: Parent node (None for root).
        """
        self.oid = oid
        self.name = name
        self.value = value
        self.oid_type = oid_type
        self.parent = parent
        self.children: List["MIBNode"] = []

        if parent is not None:
            parent.children.append(self)

    def row(self) -> int:
        """Get the row index of this node in parent's children list.

        Returns:
            Index of this node in parent's children list.
        """
        if self.parent:
            return self.parent.children.index(self)
        return 0

    def columnCount(self) -> int:
        """Get the number of columns for this node.

        Returns:
            Always returns 4 (OID, Name, Value, Type).
        """
        return 4

    def data(self, column: int) -> Any:
        """Get data for a specific column.

        Args:
            column: Column index (0=OID, 1=Name, 2=Value, 3=Type).

        Returns:
            Data value for the column.
        """
        if column == 0:
            return self.oid
        elif column == 1:
            return self.name
        elif column == 2:
            return self.value if self.value is not None else ""
        elif column == 3:
            return self.oid_type
        return None

    def setData(self, column: int, value: Any) -> None:
        """Set data for a specific column.

        Args:
            column: Column index.
            value: New value to set.
        """
        if column == 0:
            self.oid = value
        elif column == 1:
            self.name = value
        elif column == 2:
            self.value = value
        elif column == 3:
            self.oid_type = value


class MIBModel(QAbstractItemModel):
    """Model for displaying MIB OID tree in QTreeView.

    This model manages a hierarchical tree of MIB OIDs suitable for
    display in a Qt QTreeView widget.

    Column layout:
        0 - OID: The OID string (e.g., "1.3.6.1.2.1.1.1.0")
        1 - Name: Human-readable name (e.g., "sysDescr")
        2 - Value: Current value
        3 - Type: SNMP data type (e.g., "String", "Integer")

    Signals:
        oid_added: Emitted when an OID is added (oid: str)
        oid_removed: Emitted when an OID is removed (oid: str)
        value_updated: Emitted when a value is updated (oid: str, value: Any)
    """

    # Column constants
    COLUMN_OID = 0
    COLUMN_NAME = 1
    COLUMN_VALUE = 2
    COLUMN_TYPE = 3
    COLUMN_COUNT = 4

    # Column headers
    HEADERS = ["OID", "Name", "Value", "Type"]

    def __init__(self, parent=None) -> None:
        """Initialize the MIBModel.

        Args:
            parent: Parent QObject.
        """
        super().__init__(parent)
        self._root = MIBNode("", "Root", None, "")
        self._oid_index_map: dict[str, MIBNode] = {}  # OID string -> MIBNode

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        """Return the index of the item in the model given row, column, and parent.

        Args:
            row: Row number.
            column: Column number.
            parent: Parent index.

        Returns:
            QModelIndex for the item.
        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        # Get parent node
        if not parent.isValid():
            parent_node = self._root
        else:
            parent_node = parent.internalPointer()

        # Get child node
        if row < len(parent_node.children):
            child_node = parent_node.children[row]
            return self.createIndex(row, column, child_node)

        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        """Return the parent of the model item with the given index.

        Args:
            index: Child index.

        Returns:
            Parent QModelIndex.
        """
        if not index.isValid():
            return QModelIndex()

        child_node = index.internalPointer()
        parent_node = child_node.parent

        if parent_node is None or parent_node == self._root:
            return QModelIndex()

        return self.createIndex(parent_node.row(), 0, parent_node)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return the number of rows under the given parent.

        Args:
            parent: Parent index.

        Returns:
            Number of rows.
        """
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_node = self._root
        else:
            parent_node = parent.internalPointer()

        return len(parent_node.children)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return the number of columns under the given parent.

        Args:
            parent: Parent index.

        Returns:
            Number of columns (always 4).
        """
        return self.COLUMN_COUNT

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Return the data stored under the given role for the item referred to by index.

        Args:
            index: Model index.
            role: Data role.

        Returns:
            Data for the role, or None if no data.
        """
        if not index.isValid():
            return None

        node = index.internalPointer()
        column = index.column()

        if role == Qt.DisplayRole:
            return node.data(column)
        elif role == Qt.EditRole:
            return node.data(column)
        elif role == Qt.ToolTipRole:
            # Provide tooltip with full OID and value
            if column == 0:
                return node.oid
            elif column == 2:
                return f"{node.name}: {node.value}"
            return None
        elif role == Qt.StatusTipRole:
            return f"{node.name} ({node.oid})"

        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        """Set the data for the item at index.

        Args:
            index: Model index.
            value: New value.
            role: Data role.

        Returns:
            True if data was set successfully.
        """
        if not index.isValid():
            return False

        if role == Qt.EditRole:
            node = index.internalPointer()
            node.setData(index.column(), value)
            self.dataChanged.emit(index, index, [role])
            return True

        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Return the item flags for the given index.

        Args:
            index: Model index.

        Returns:
            Item flags.
        """
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

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
            if section < len(self.HEADERS):
                return self.HEADERS[section]

        return None

    def add_oid(
        self,
        oid: str,
        name: str = "",
        value: Any = None,
        oid_type: str = "String",
        parent: QModelIndex = QModelIndex()
    ) -> QModelIndex:
        """Add an OID node to the tree.

        Args:
            oid: OID string (e.g., "1.3.6.1.2.1.1.1.0")
            name: Human-readable name.
            value: Current value.
            oid_type: SNMP data type.
            parent: Parent QModelIndex for nested OIDs.

        Returns:
            QModelIndex of the newly created node.
        """
        # Determine parent node
        if parent.isValid():
            parent_node = parent.internalPointer()
        else:
            parent_node = self._root

        # Create new node
        node = MIBNode(oid, name, value, oid_type, parent_node)

        # Map OID to node for quick lookup
        self._oid_index_map[oid] = node

        # Calculate row position
        row = len(parent_node.children) - 1

        # Notify views
        parent_index = QModelIndex() if parent_node == self._root else parent
        self.beginInsertRows(parent_index, row, row)
        self.endInsertRows()

        return self.createIndex(row, 0, node)

    def remove_oid(self, index: QModelIndex) -> bool:
        """Remove an OID node from the tree.

        Args:
            index: QModelIndex of the node to remove.

        Returns:
            True if node was removed, False otherwise.
        """
        if not index.isValid():
            return False

        node = index.internalPointer()
        if node is None or node == self._root:
            return False

        parent_node = node.parent
        if parent_node is None:
            return False

        # Get row before removal
        row = node.row()

        # Remove from OID map
        if node.oid in self._oid_index_map:
            del self._oid_index_map[node.oid]

        # Notify views before modification
        parent_index = QModelIndex() if parent_node == self._root else self.createIndex(parent_node.row(), 0, parent_node)
        self.beginRemoveRows(parent_index, row, row)

        # Remove from parent's children list
        if node in parent_node.children:
            parent_node.children.remove(node)

        self.endRemoveRows()

        return True

    def update_value(self, oid: str, value: Any) -> bool:
        """Update the value of an OID node.

        Args:
            oid: OID string of the node to update.
            value: New value.

        Returns:
            True if value was updated, False if OID not found.
        """
        if oid not in self._oid_index_map:
            return False

        node = self._oid_index_map[oid]
        old_value = node.value
        node.value = value

        # Emit dataChanged for the value column
        index = self.createIndex(node.row(), self.COLUMN_VALUE, node)
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])

        return True

    def clear(self) -> None:
        """Remove all OID nodes from the tree."""
        self.beginResetModel()

        # Clear all children from root
        self._root.children.clear()
        self._oid_index_map.clear()

        self.endResetModel()

    def get_node(self, oid: str) -> Optional[MIBNode]:
        """Get a MIBNode by its OID.

        Args:
            oid: OID string.

        Returns:
            MIBNode if found, None otherwise.
        """
        return self._oid_index_map.get(oid)

    def get_oid_index(self, oid: str) -> QModelIndex:
        """Get the model index for an OID.

        Args:
            oid: OID string.

        Returns:
            QModelIndex of the node, or invalid index if not found.
        """
        node = self._oid_index_map.get(oid)
        if node:
            return self.createIndex(node.row(), 0, node)
        return QModelIndex()

    def find_oid(self, oid: str) -> Optional[MIBNode]:
        """Find a node by OID string (partial match support).

        Args:
            oid: OID string or prefix to search.

        Returns:
            MIBNode if found, None otherwise.
        """
        return self._oid_index_map.get(oid)

    def get_all_oids(self) -> List[Tuple[str, str, Any, str]]:
        """Get all OIDs as a list.

        Returns:
            List of tuples (oid, name, value, type).
        """
        return [
            (node.oid, node.name, node.value, node.oid_type)
            for node in self._oid_index_map.values()
        ]
