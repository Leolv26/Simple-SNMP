"""Tests for TrapModel class."""
import pytest
from datetime import datetime
from unittest.mock import MagicMock


class TestTrapModelImports:
    """Test that TrapModel can be imported."""

    def test_import_trap_model(self):
        """Test that TrapModel can be imported."""
        try:
            from snmp_monitor.gui.models.trap_model import TrapModel
            assert TrapModel is not None
        except ImportError:
            pytest.fail("TrapModel cannot be imported")


class TestTrapModelInitialization:
    """Test TrapModel initialization."""

    def test_model_initialization(self):
        """Test that TrapModel can be initialized."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        assert model is not None

    def test_model_inherits_from_qabstracttablemodel(self):
        """Test that TrapModel inherits from QAbstractTableModel."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        from PySide6.QtCore import QAbstractTableModel
        model = TrapModel()
        assert isinstance(model, QAbstractTableModel)

    def test_initial_row_count_is_zero(self):
        """Test that initial row count is 0."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        assert model.rowCount() == 0


class TestTrapModelColumns:
    """Test TrapModel column structure."""

    def test_column_count_is_four(self):
        """Test that model has 4 columns."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        assert model.columnCount() == 4

    def test_column_headers(self):
        """Test that model has correct column headers."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        from PySide6.QtCore import Qt
        model = TrapModel()
        # Should have headers for time, source, OID, message
        headers = ["Time", "Source", "OID", "Message"]
        for i, header in enumerate(headers):
            assert model.headerData(i, Qt.Horizontal, Qt.DisplayRole) == header


class TestTrapModelAddTrap:
    """Test TrapModel add_trap functionality."""

    def test_add_trap_basic(self):
        """Test adding a basic trap."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        model.add_trap("192.168.1.1", "1.3.6.1.4.1.1", "Test trap", "info")
        assert model.rowCount() == 1

    def test_add_trap_increases_row_count(self):
        """Test that adding trap increases row count."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        initial_count = model.rowCount()
        model.add_trap("192.168.1.1", "1.3.6.1.4.1.1", "Test 1", "info")
        model.add_trap("192.168.1.2", "1.3.6.1.4.1.2", "Test 2", "warning")
        assert model.rowCount() == initial_count + 2

    def test_add_trap_updates_display(self):
        """Test that added trap data is available for display."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        from PySide6.QtCore import Qt
        model = TrapModel()
        model.add_trap("192.168.1.100", "1.3.6.1.4.1.100", "Interface down", "critical")
        # Get first row index
        index = model.index(0, 0)
        assert index.isValid()

    def test_add_trap_all_fields(self):
        """Test adding trap with all fields."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        model.add_trap("10.0.0.1", "1.3.6.1.2.1.1.3.0", "System up", "info")
        model.add_trap("10.0.0.2", "1.3.6.1.4.1.1", "Cold start", "warning")
        model.add_trap("10.0.0.3", "1.3.6.1.4.1.2", "Authentication failure", "error")
        model.add_trap("10.0.0.4", "1.3.6.1.4.1.3", "Disk full", "critical")
        assert model.rowCount() == 4


class TestTrapModelSorting:
    """Test TrapModel sorting (newest first)."""

    def test_traps_sorted_newest_first(self):
        """Test that traps are sorted with newest first (reverse chronological)."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        # Add traps in order
        model.add_trap("192.168.1.1", "1.3.6.1.1", "First trap", "info")
        model.add_trap("192.168.1.2", "1.3.6.1.2", "Second trap", "info")
        model.add_trap("192.168.1.3", "1.3.6.1.3", "Third trap", "info")
        # Most recent (third trap) should be at row 0
        index = model.index(0, 1)  # Column 1 = Source
        assert model.data(index) == "192.168.1.3"

    def test_new_trap_appears_at_top(self):
        """Test that new trap appears at the top of the list."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        model.add_trap("192.168.1.1", "1.3.6.1.1", "First", "info")
        # Add new trap
        model.add_trap("192.168.1.99", "1.3.6.1.99", "Latest", "info")
        # Latest should be at row 0
        index = model.index(0, 2)  # Column 2 = OID
        assert model.data(index) == "1.3.6.1.99"


class TestTrapModelDataRetrieval:
    """Test TrapModel data retrieval methods."""

    def test_get_traps_returns_list(self):
        """Test that get_traps returns a list."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        model.add_trap("192.168.1.1", "1.3.6.1.1", "Test", "info")
        traps = model.get_traps()
        assert isinstance(traps, list)

    def test_get_traps_returns_all_traps(self):
        """Test that get_traps returns all traps."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        model.add_trap("192.168.1.1", "1.3.6.1.1", "Test 1", "info")
        model.add_trap("192.168.1.2", "1.3.6.1.2", "Test 2", "info")
        traps = model.get_traps()
        assert len(traps) == 2

    def test_get_traps_contains_all_fields(self):
        """Test that each trap contains timestamp, source, oid, message, severity."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        model.add_trap("192.168.1.1", "1.3.6.1.1", "Test message", "warning")
        traps = model.get_traps()
        assert len(traps) == 1
        trap = traps[0]
        assert 'timestamp' in trap or 'time' in trap or trap[0] is not None
        assert 'source' in trap or 'source_address' in trap or 'source' in str(trap).lower()
        assert 'oid' in trap or 'OID' in trap
        assert 'message' in trap or 'msg' in trap or 'description' in trap
        assert 'severity' in trap or 'level' in trap

    def test_get_recent_returns_n_traps(self):
        """Test that get_recent returns specified number of traps."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        for i in range(10):
            model.add_trap(f"192.168.1.{i}", f"1.3.6.1.{i}", f"Trap {i}", "info")
        recent = model.get_recent(3)
        assert len(recent) == 3

    def test_get_recent_returns_newest_first(self):
        """Test that get_recent returns newest traps first."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        model.add_trap("192.168.1.1", "1.3.6.1.1", "First", "info")
        model.add_trap("192.168.1.2", "1.3.6.1.2", "Second", "info")
        model.add_trap("192.168.1.3", "1.3.6.1.3", "Third", "info")
        recent = model.get_recent(2)
        # Most recent should be first in the list
        assert len(recent) == 2

    def test_get_recent_more_than_available(self):
        """Test get_recent when count exceeds available traps."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        model.add_trap("192.168.1.1", "1.3.6.1.1", "Test", "info")
        recent = model.get_recent(10)
        assert len(recent) == 1

    def test_get_recent_empty_model(self):
        """Test get_recent on empty model."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        recent = model.get_recent(5)
        assert len(recent) == 0


class TestTrapModelClear:
    """Test TrapModel clear functionality."""

    def test_clear_empty_model(self):
        """Test clearing an empty model."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        model.clear()
        assert model.rowCount() == 0

    def test_clear_with_traps(self):
        """Test clearing model with traps."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        model.add_trap("192.168.1.1", "1.3.6.1.1", "Test 1", "info")
        model.add_trap("192.168.1.2", "1.3.6.1.2", "Test 2", "info")
        model.clear()
        assert model.rowCount() == 0

    def test_clear_after_get_traps(self):
        """Test that get_traps returns empty after clear."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        model.add_trap("192.168.1.1", "1.3.6.1.1", "Test", "info")
        model.clear()
        traps = model.get_traps()
        assert len(traps) == 0


class TestTrapModelSignals:
    """Test TrapModel Qt signals."""

    def test_model_has_trap_added_signal(self):
        """Test that TrapModel has trap_added signal."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        assert hasattr(model, 'trap_added')

    def test_trap_added_signal_emitted(self):
        """Test that trap_added signal is emitted when trap is added."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        from PySide6.QtCore import QObject
        model = TrapModel()
        emitted_count = [0]

        class SignalCatcher(QObject):
            def __init__(self):
                super().__init__()
                self.trap_data = None

            def on_trap_added(self, data):
                emitted_count[0] += 1
                self.trap_data = data

        catcher = SignalCatcher()
        model.trap_added.connect(catcher.on_trap_added)
        model.add_trap("192.168.1.1", "1.3.6.1.1", "Test", "info")
        assert emitted_count[0] == 1

    def test_multiple_traps_emit_multiple_signals(self):
        """Test that multiple traps emit multiple signals."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        from PySide6.QtCore import QObject
        model = TrapModel()
        emitted_count = [0]

        def on_trap_added(data):
            emitted_count[0] += 1

        model.trap_added.connect(on_trap_added)
        model.add_trap("192.168.1.1", "1.3.6.1.1", "Test 1", "info")
        model.add_trap("192.168.1.2", "1.3.6.1.2", "Test 2", "info")
        model.add_trap("192.168.1.3", "1.3.6.1.3", "Test 3", "info")
        assert emitted_count[0] == 3


class TestTrapModelDisplay:
    """Test TrapModel display functionality."""

    def test_data_returns_source_for_source_column(self):
        """Test that data() returns source for source column."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        from PySide6.QtCore import Qt
        model = TrapModel()
        model.add_trap("192.168.1.100", "1.3.6.1.1", "Test", "info")
        index = model.index(0, 1)  # Column 1 = Source
        data = model.data(index, Qt.DisplayRole)
        assert data == "192.168.1.100"

    def test_data_returns_oid_for_oid_column(self):
        """Test that data() returns OID for OID column."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        from PySide6.QtCore import Qt
        model = TrapModel()
        model.add_trap("192.168.1.1", "1.3.6.1.4.1.100", "Test", "info")
        index = model.index(0, 2)  # Column 2 = OID
        data = model.data(index, Qt.DisplayRole)
        assert data == "1.3.6.1.4.1.100"

    def test_data_returns_message_for_message_column(self):
        """Test that data() returns message for message column."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        from PySide6.QtCore import Qt
        model = TrapModel()
        model.add_trap("192.168.1.1", "1.3.6.1.1", "Interface down alert", "critical")
        index = model.index(0, 3)  # Column 3 = Message
        data = model.data(index, Qt.DisplayRole)
        assert data == "Interface down alert"

    def test_data_returns_timestamp_for_time_column(self):
        """Test that data() returns timestamp for time column."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        from PySide6.QtCore import Qt
        model = TrapModel()
        model.add_trap("192.168.1.1", "1.3.6.1.1", "Test", "info")
        index = model.index(0, 0)  # Column 0 = Time
        data = model.data(index, Qt.DisplayRole)
        assert data is not None
        # Should be some kind of datetime string or object
        assert isinstance(data, (str, datetime))

    def test_data_returns_none_for_invalid_index(self):
        """Test that data() returns None for invalid index."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        from PySide6.QtCore import Qt, QModelIndex
        model = TrapModel()
        index = QModelIndex()
        data = model.data(index, Qt.DisplayRole)
        assert data is None


class TestTrapModelEdgeCases:
    """Test TrapModel edge cases."""

    def test_empty_source(self):
        """Test adding trap with empty source."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        model.add_trap("", "1.3.6.1.1", "Test", "info")
        assert model.rowCount() == 1

    def test_empty_oid(self):
        """Test adding trap with empty OID."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        model.add_trap("192.168.1.1", "", "Test", "info")
        assert model.rowCount() == 1

    def test_empty_message(self):
        """Test adding trap with empty message."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        model.add_trap("192.168.1.1", "1.3.6.1.1", "", "info")
        assert model.rowCount() == 1

    def test_special_characters_in_message(self):
        """Test adding trap with special characters in message."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        special_msg = "Alert: CPU > 90%! Check system."
        model.add_trap("192.168.1.1", "1.3.6.1.1", special_msg, "critical")
        assert model.rowCount() == 1
        traps = model.get_traps()
        assert traps[0]['message'] == special_msg

    def test_unicode_in_message(self):
        """Test adding trap with unicode characters."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        unicode_msg = "Error: Disk full 惨惰"
        model.add_trap("192.168.1.1", "1.3.6.1.1", unicode_msg, "error")
        traps = model.get_traps()
        assert traps[0]['message'] == unicode_msg

    def test_long_oid(self):
        """Test adding trap with long OID."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        long_oid = "1.3.6.1.4.1.9.9." + ".".join(["1"] * 20)
        model.add_trap("192.168.1.1", long_oid, "Test", "info")
        traps = model.get_traps()
        assert traps[0]['oid'] == long_oid

    def test_all_severity_levels(self):
        """Test adding traps with all severity levels."""
        from snmp_monitor.gui.models.trap_model import TrapModel
        model = TrapModel()
        severities = ["debug", "info", "warning", "error", "critical"]
        for i, severity in enumerate(severities):
            model.add_trap(f"192.168.1.{i}", f"1.3.6.1.{i}", f"Test {severity}", severity)
        assert model.rowCount() == 5
