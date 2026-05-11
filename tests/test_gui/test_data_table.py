"""Tests for DataTableWidget class."""
import pytest
from unittest.mock import MagicMock, patch
import sys


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for testing."""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestDataTableWidgetImports:
    """Test that DataTableWidget can be imported."""

    def test_import_data_table_widget(self):
        """Test that DataTableWidget can be imported."""
        try:
            from snmp_monitor.gui.views.data_table import DataTableWidget
            assert DataTableWidget is not None
        except ImportError:
            pytest.fail("DataTableWidget cannot be imported")


class TestDataTableWidgetInheritance:
    """Test DataTableWidget class inheritance."""

    def test_widget_inherits_from_qwidget(self, qapp):
        """Test that DataTableWidget inherits from QWidget."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        from PySide6.QtWidgets import QWidget
        widget = DataTableWidget()
        assert isinstance(widget, QWidget)


class TestDataTableWidgetInitialization:
    """Test DataTableWidget initialization."""

    def test_widget_can_be_instantiated(self, qapp):
        """Test that DataTableWidget can be instantiated."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()
        assert widget is not None

    def test_widget_has_table_widget(self, qapp):
        """Test that widget contains a QTableWidget."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()
        assert hasattr(widget, '_table_widget') or hasattr(widget, 'table_widget')

    def test_widget_has_oid_input(self, qapp):
        """Test that widget has an OID input field."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()
        assert hasattr(widget, '_oid_input') or hasattr(widget, 'oid_input')

    def test_widget_has_search_button(self, qapp):
        """Test that widget has a search button."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()
        assert hasattr(widget, '_search_btn') or hasattr(widget, 'search_button')


class TestDataTableWidgetTableWidget:
    """Test DataTableWidget QTableWidget configuration."""

    def test_table_widget_is_qtablewidget(self, qapp):
        """Test that table_widget is a QTableWidget."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        from PySide6.QtWidgets import QTableWidget
        widget = DataTableWidget()
        table = getattr(widget, '_table_widget', None)
        assert table is not None
        assert isinstance(table, QTableWidget)

    def test_table_has_four_columns(self, qapp):
        """Test that table has 4 columns (OID, Name, Current Value, Unit)."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()
        table = getattr(widget, '_table_widget', None)
        assert table is not None
        assert table.columnCount() == 4

    def test_table_column_headers(self, qapp):
        """Test that table has correct column headers."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()
        table = getattr(widget, '_table_widget', None)
        headers = [table.horizontalHeaderItem(i).text() for i in range(4)]
        # Check that headers contain expected labels
        assert any('OID' in h or 'oid' in h.lower() for h in headers)

    def test_table_row_selection_enabled(self, qapp):
        """Test that table has row selection enabled."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        from PySide6.QtWidgets import QAbstractItemView
        widget = DataTableWidget()
        table = getattr(widget, '_table_widget', None)
        # Selection behavior should be SelectRows
        assert table.selectionBehavior() == QAbstractItemView.SelectRows


class TestDataTableWidgetSearchComponents:
    """Test DataTableWidget search components."""

    def test_oid_input_is_qlineedit(self, qapp):
        """Test that OID input is a QLineEdit."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        from PySide6.QtWidgets import QLineEdit
        widget = DataTableWidget()
        oid_input = getattr(widget, '_oid_input', None)
        assert oid_input is not None
        assert isinstance(oid_input, QLineEdit)

    def test_search_button_is_qpushbutton(self, qapp):
        """Test that search button is a QPushButton."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        from PySide6.QtWidgets import QPushButton
        widget = DataTableWidget()
        search_btn = getattr(widget, '_search_btn', None) or getattr(widget, 'search_button', None)
        assert search_btn is not None
        assert isinstance(search_btn, QPushButton)

    def test_search_button_has_text(self, qapp):
        """Test that search button has text or tooltip."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()
        search_btn = getattr(widget, '_search_btn', None) or getattr(widget, 'search_button', None)
        assert search_btn is not None
        # Button should have some text or tooltip
        assert len(search_btn.text()) > 0 or len(search_btn.toolTip()) > 0


class TestDataTableWidgetSignals:
    """Test DataTableWidget signals."""

    def test_widget_has_oid_query_requested_signal(self, qapp):
        """Test that widget has oid_query_requested signal."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        from PySide6.QtCore import Signal
        widget = DataTableWidget()
        assert hasattr(widget, 'oid_query_requested')
        signal = getattr(widget, 'oid_query_requested', None)
        assert signal is not None
        assert isinstance(signal, Signal)

    def test_widget_has_oid_value_updated_signal(self, qapp):
        """Test that widget has oid_value_updated signal."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        from PySide6.QtCore import Signal
        widget = DataTableWidget()
        assert hasattr(widget, 'oid_value_updated')
        signal = getattr(widget, 'oid_value_updated', None)
        assert signal is not None
        assert isinstance(signal, Signal)

    def test_search_button_triggers_signal(self, qapp):
        """Test that clicking search button emits oid_query_requested."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()

        signal_received = []

        def on_query_requested(oid):
            signal_received.append(oid)

        widget.oid_query_requested.connect(on_query_requested)

        # Set text in OID input
        oid_input = getattr(widget, '_oid_input', None)
        if oid_input:
            oid_input.setText("1.3.6.1.2.1.1.1.0")

        # Click search button
        search_btn = getattr(widget, '_search_btn', None) or getattr(widget, 'search_button', None)
        if search_btn:
            search_btn.click()

        # Verify signal was emitted
        assert len(signal_received) == 1
        assert signal_received[0] == "1.3.6.1.2.1.1.1.0"


class TestDataTableWidgetMethods:
    """Test DataTableWidget public methods."""

    def test_widget_has_update_table_method(self, qapp):
        """Test that widget has an update_table or add_row method."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()
        # Should have either update_table or add_row
        assert hasattr(widget, 'update_table') or hasattr(widget, 'add_row')

    def test_widget_has_clear_table_method(self, qapp):
        """Test that widget has a clear_table or clear method."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()
        # Should have either clear_table or clear
        assert hasattr(widget, 'clear_table') or hasattr(widget, 'clear')

    def test_widget_has_search_oid_method(self, qapp):
        """Test that widget has a search_oid method."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()
        assert hasattr(widget, 'search_oid')


class TestDataTableWidgetTableOperations:
    """Test DataTableWidget table operations."""

    def test_add_row_method_works(self, qapp):
        """Test that add_row adds data to table."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()

        # Check if add_row method exists
        if hasattr(widget, 'add_row'):
            widget.add_row("1.3.6.1.2.1.1.1.0", "sysDescr", "Test System", "String")
            table = getattr(widget, '_table_widget', None)
            assert table.rowCount() == 1
        else:
            # Fallback to update_table
            if hasattr(widget, 'update_table'):
                widget.update_table([("1.3.6.1.2.1.1.1.0", "sysDescr", "Test System", "String")])
                table = getattr(widget, '_table_widget', None)
                assert table.rowCount() == 1

    def test_clear_table_method_works(self, qapp):
        """Test that clear_table clears the table."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()

        # Add some data first
        if hasattr(widget, 'add_row'):
            widget.add_row("1.3.6.1.2.1.1.1.0", "sysDescr", "Test System", "String")

        table = getattr(widget, '_table_widget', None)

        # Clear the table
        if hasattr(widget, 'clear_table'):
            widget.clear_table()
        elif hasattr(widget, 'clear'):
            widget.clear()

        assert table.rowCount() == 0

    def test_update_table_with_multiple_rows(self, qapp):
        """Test that update_table can handle multiple rows."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()

        if hasattr(widget, 'update_table'):
            data = [
                ("1.3.6.1.2.1.1.1.0", "sysDescr", "Test System 1", "String"),
                ("1.3.6.1.2.1.1.3.0", "sysUpTime", "100", "TimeTicks"),
                ("1.3.6.1.2.1.1.5.0", "sysName", "Test Host", "String"),
            ]
            widget.update_table(data)

            table = getattr(widget, '_table_widget', None)
            assert table.rowCount() == 3


class TestDataTableWidgetLayout:
    """Test DataTableWidget layout structure."""

    def test_widget_has_layout(self, qapp):
        """Test that widget has a layout."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        from PySide6.QtWidgets import QLayout
        widget = DataTableWidget()
        assert widget.layout() is not None
        assert isinstance(widget.layout(), QLayout)

    def test_table_is_child_of_widget(self, qapp):
        """Test that table is a child of the widget."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()
        table = getattr(widget, '_table_widget', None)
        assert table is not None
        assert table.parent() is widget


class TestDataTableWidgetSearchFunctionality:
    """Test DataTableWidget search functionality."""

    def test_oid_input_accepts_text(self, qapp):
        """Test that OID input accepts text input."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()
        oid_input = getattr(widget, '_oid_input', None)
        if oid_input:
            oid_input.setText("1.3.6.1.2.1.1.1.0")
            assert oid_input.text() == "1.3.6.1.2.1.1.1.0"

    def test_search_oid_method_emits_signal(self, qapp):
        """Test that search_oid method emits oid_query_requested signal."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()

        signal_received = []

        def on_query_requested(oid):
            signal_received.append(oid)

        widget.oid_query_requested.connect(on_query_requested)

        if hasattr(widget, 'search_oid'):
            widget.search_oid("1.3.6.1.2.1.1.1.0")

        assert len(signal_received) == 1
        assert signal_received[0] == "1.3.6.1.2.1.1.1.0"


class TestDataTableWidgetValueUpdate:
    """Test DataTableWidget value update functionality."""

    def test_update_oid_value_method_exists(self, qapp):
        """Test that widget has method to update OID values."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()
        # Should have a method to update values
        assert hasattr(widget, 'update_oid_value') or hasattr(widget, 'set_value')

    def test_update_oid_value_emits_signal(self, qapp):
        """Test that updating OID value emits oid_value_updated signal."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()

        signal_received = []

        def on_value_updated(oid, value):
            signal_received.append((oid, value))

        widget.oid_value_updated.connect(on_value_updated)

        # Add a row first
        if hasattr(widget, 'add_row'):
            widget.add_row("1.3.6.1.2.1.1.1.0", "sysDescr", "Old Value", "String")

        # Update the value
        if hasattr(widget, 'update_oid_value'):
            widget.update_oid_value("1.3.6.1.2.1.1.1.0", "New Value")
        elif hasattr(widget, 'set_value'):
            widget.set_value("1.3.6.1.2.1.1.1.0", "New Value")

        # Verify signal was emitted
        assert len(signal_received) == 1
        assert signal_received[0][0] == "1.3.6.1.2.1.1.1.0"
        assert signal_received[0][1] == "New Value"


class TestDataTableWidgetIntegration:
    """Test DataTableWidget integration scenarios."""

    def test_full_search_flow(self, qapp):
        """Test complete flow: input OID -> click search -> display result."""
        from snmp_monitor.gui.views.data_table import DataTableWidget
        widget = DataTableWidget()

        query_oids = []

        def on_query_requested(oid):
            query_oids.append(oid)

        widget.oid_query_requested.connect(on_query_requested)

        # Input OID and search
        oid_input = getattr(widget, '_oid_input', None)
        if oid_input:
            oid_input.setText("1.3.6.1.2.1.1.1.0")

        search_btn = getattr(widget, '_search_btn', None) or getattr(widget, 'search_button', None)
        if search_btn:
            search_btn.click()

        # Verify query was triggered
        assert len(query_oids) == 1
        assert query_oids[0] == "1.3.6.1.2.1.1.1.0"

        # Simulate receiving data and updating table
        if hasattr(widget, 'update_table'):
            widget.update_table([
                ("1.3.6.1.2.1.1.1.0", "sysDescr", "SNMP Agent v1.0", "String")
            ])

            table = getattr(widget, '_table_widget', None)
            assert table.rowCount() == 1
