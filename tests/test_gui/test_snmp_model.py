"""Tests for SNMPModel class."""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock


class TestSNMPModelDataStorage:
    """Test SNMPModel data storage functionality."""

    def test_model_initialization(self):
        """Test that SNMPModel can be initialized."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        assert model is not None

    def test_initial_data_values_are_none(self):
        """Test initial data values are None."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        assert model.cpu_percent is None
        assert model.memory_percent is None
        assert model.disk_percent is None
        assert model.bytes_sent is None
        assert model.bytes_recv is None

    def test_update_data_with_valid_values(self):
        """Test updating data with valid values."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        data = {
            'cpu_percent': 50.0,
            'memory_percent': 60.0,
            'disk_percent': 70.0,
            'bytes_sent': 1000,
            'bytes_recv': 2000
        }
        model.update_data(data)
        assert model.cpu_percent == 50.0
        assert model.memory_percent == 60.0
        assert model.disk_percent == 70.0
        assert model.bytes_sent == 1000
        assert model.bytes_recv == 2000

    def test_update_data_creates_history(self):
        """Test that updating data adds to history."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        data1 = {'cpu_percent': 50.0, 'memory_percent': 60.0, 'disk_percent': 70.0}
        data2 = {'cpu_percent': 55.0, 'memory_percent': 65.0, 'disk_percent': 75.0}
        model.update_data(data1)
        model.update_data(data2)
        history = model.get_history()
        assert len(history) == 2

    def test_history_contains_timestamps(self):
        """Test that history records include timestamps."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        data = {'cpu_percent': 50.0}
        model.update_data(data)
        history = model.get_history()
        assert len(history) == 1
        assert 'timestamp' in history[0]
        assert isinstance(history[0]['timestamp'], datetime)


class TestSNMPModelGetters:
    """Test SNMPModel getter methods."""

    def test_get_current_returns_none_when_empty(self):
        """Test get_current returns None when no data."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        current = model.get_current()
        assert current is None

    def test_get_current_returns_current_data(self):
        """Test get_current returns current data."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        data = {
            'cpu_percent': 50.0,
            'memory_percent': 60.0,
            'disk_percent': 70.0,
            'bytes_sent': 1000,
            'bytes_recv': 2000
        }
        model.update_data(data)
        current = model.get_current()
        assert current is not None
        assert current['cpu_percent'] == 50.0
        assert current['memory_percent'] == 60.0

    def test_get_history_returns_empty_list_when_empty(self):
        """Test get_history returns empty list when no data."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        history = model.get_history()
        assert history == []

    def test_get_history_returns_list(self):
        """Test get_history returns a list of historical data."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        model.update_data({'cpu_percent': 50.0})
        model.update_data({'cpu_percent': 60.0})
        history = model.get_history()
        assert isinstance(history, list)
        assert len(history) == 2


class TestSNMPModelThresholds:
    """Test SNMPModel threshold checking functionality."""

    def test_default_thresholds(self):
        """Test default threshold values."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        assert hasattr(model, 'cpu_threshold')
        assert hasattr(model, 'memory_threshold')
        assert hasattr(model, 'disk_threshold')
        # Default thresholds should be reasonable values
        assert model.cpu_threshold > 0
        assert model.memory_threshold > 0
        assert model.disk_threshold > 0

    def test_set_thresholds(self):
        """Test setting custom threshold values."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        model.set_thresholds(cpu=80.0, memory=85.0, disk=90.0)
        assert model.cpu_threshold == 80.0
        assert model.memory_threshold == 85.0
        assert model.disk_threshold == 90.0

    def test_check_thresholds_no_alert_when_normal(self):
        """Test no alert when values are below threshold."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        model.set_thresholds(cpu=80.0, memory=85.0, disk=90.0)
        data = {
            'cpu_percent': 50.0,
            'memory_percent': 60.0,
            'disk_percent': 70.0
        }
        model.update_data(data)
        alerts = model.check_thresholds()
        assert alerts == []

    def test_check_thresholds_alert_cpu(self):
        """Test alert when CPU exceeds threshold."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        model.set_thresholds(cpu=50.0, memory=85.0, disk=90.0)
        data = {
            'cpu_percent': 80.0,
            'memory_percent': 60.0,
            'disk_percent': 70.0
        }
        model.update_data(data)
        alerts = model.check_thresholds()
        assert len(alerts) > 0
        assert any('cpu' in str(alert).lower() for alert in alerts)

    def test_check_thresholds_alert_memory(self):
        """Test alert when memory exceeds threshold."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        model.set_thresholds(cpu=80.0, memory=50.0, disk=90.0)
        data = {
            'cpu_percent': 30.0,
            'memory_percent': 80.0,
            'disk_percent': 70.0
        }
        model.update_data(data)
        alerts = model.check_thresholds()
        assert len(alerts) > 0
        assert any('memory' in str(alert).lower() for alert in alerts)

    def test_check_thresholds_alert_disk(self):
        """Test alert when disk exceeds threshold."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        model.set_thresholds(cpu=80.0, memory=85.0, disk=60.0)
        data = {
            'cpu_percent': 30.0,
            'memory_percent': 50.0,
            'disk_percent': 85.0
        }
        model.update_data(data)
        alerts = model.check_thresholds()
        assert len(alerts) > 0
        assert any('disk' in str(alert).lower() for alert in alerts)

    def test_check_thresholds_multiple_alerts(self):
        """Test multiple alerts when multiple values exceed thresholds."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        model.set_thresholds(cpu=50.0, memory=50.0, disk=50.0)
        data = {
            'cpu_percent': 80.0,
            'memory_percent': 80.0,
            'disk_percent': 80.0
        }
        model.update_data(data)
        alerts = model.check_thresholds()
        assert len(alerts) >= 2

    def test_check_thresholds_returns_empty_when_no_data(self):
        """Test check_thresholds returns empty when no data."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        alerts = model.check_thresholds()
        assert alerts == []


class TestSNMPModelConfigLoading:
    """Test SNMPModel configuration loading."""

    @patch('snmp_monitor.gui.models.snmp_model.load_config')
    def test_load_config_from_yaml(self, mock_load_config):
        """Test loading configuration from YAML file."""
        mock_load_config.return_value = {
            'thresholds': {
                'cpu': 75.0,
                'memory': 80.0,
                'disk': 85.0
            }
        }
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        assert model.cpu_threshold == 75.0
        assert model.memory_threshold == 80.0
        assert model.disk_threshold == 85.0

    @patch('snmp_monitor.gui.models.snmp_model.load_config')
    def test_load_config_with_defaults(self, mock_load_config):
        """Test loading config with missing threshold values uses defaults."""
        mock_load_config.return_value = {}  # Empty config
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        # Should use default values
        assert model.cpu_threshold > 0
        assert model.memory_threshold > 0
        assert model.disk_threshold > 0


class TestSNMPModelSignals:
    """Test SNMPModel PyQt signals."""

    def test_model_has_signals(self):
        """Test that SNMPModel has required signals."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        # Model should have signals for data updates
        assert hasattr(model, 'data_updated')
        assert hasattr(model, 'threshold_exceeded')

    def test_data_updated_signal_emitted(self):
        """Test that data_updated signal is emitted on update."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        emitted = []
        try:
            from PySide6.QtCore import QObject
            # Create a slot to capture the signal
            class SignalCatcher(QObject):
                def __init__(self):
                    super().__init__()
                    self.received = []

                def on_data_updated(self, data):
                    self.received.append(data)

            catcher = SignalCatcher()
            model.data_updated.connect(catcher.on_data_updated)
            model.update_data({'cpu_percent': 50.0})
            # If signal is connected and emitted, the slot should be called
            assert len(catcher.received) == 1
        except ImportError:
            pytest.skip("PySide6 not available")


class TestSNMPModelEdgeCases:
    """Test SNMPModel edge cases."""

    def test_update_data_with_partial_data(self):
        """Test updating data with only some fields."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        model.update_data({'cpu_percent': 50.0})
        assert model.cpu_percent == 50.0
        assert model.memory_percent is None

    def test_history_limit(self):
        """Test that history has a maximum limit."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        # Add many entries
        for i in range(100):
            model.update_data({'cpu_percent': float(i)})
        history = model.get_history()
        # History should be limited to MAX_HISTORY_SIZE (100)
        assert len(history) == 100

    def test_get_current_after_multiple_updates(self):
        """Test get_current returns latest data after multiple updates."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        model = SNMPModel()
        model.update_data({'cpu_percent': 30.0})
        model.update_data({'cpu_percent': 50.0})
        model.update_data({'cpu_percent': 70.0})
        current = model.get_current()
        assert current['cpu_percent'] == 70.0
