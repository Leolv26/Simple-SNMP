"""Tests for SNMPWorker class."""
import pytest
from unittest.mock import patch, MagicMock
import time


class TestSNMPWorkerInitialization:
    """Test SNMPWorker initialization."""

    def test_worker_initialization(self):
        """Test that SNMPWorker can be initialized."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker
        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1')
            assert worker is not None

    def test_worker_has_required_signals(self):
        """Test that SNMPWorker has required signals."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker
        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1')
            assert hasattr(worker, 'data_ready')
            assert hasattr(worker, 'error_occurred')
            assert hasattr(worker, 'oid_query_result')

    def test_worker_default_poll_interval(self):
        """Test that SNMPWorker has default poll interval."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker
        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1')
            assert worker._poll_interval == 2.0

    def test_worker_custom_poll_interval(self):
        """Test that SNMPWorker accepts custom poll interval."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker
        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1', poll_interval=5.0)
            assert worker._poll_interval == 5.0

    def test_worker_initial_running_state(self):
        """Test that SNMPWorker initial running state is False."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker
        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1')
            assert worker._running is False


class TestSNMPWorkerPolling:
    """Test SNMPWorker polling functionality."""

    def test_worker_has_client(self):
        """Test that SNMPWorker has an SNMP client."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker
        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            worker = SNMPWorker(host='127.0.0.1')
            assert worker.client is not None

    def test_worker_poll_interval_setter(self):
        """Test setting poll interval."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker
        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1', poll_interval=2.0)
            worker.set_poll_interval(5.0)
            assert worker._poll_interval == 5.0

    def test_worker_poll_interval_must_be_positive(self):
        """Test that poll interval must be positive."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker
        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1')
            worker.set_poll_interval(-1.0)
            # Should keep default or ignore invalid value
            assert worker._poll_interval > 0


class TestSNMPWorkerSignals:
    """Test SNMPWorker signal emission."""

    def test_data_ready_signal_exists(self):
        """Test that data_ready signal exists."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker
        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1')
            assert hasattr(worker, 'data_ready')

    def test_error_occurred_signal_exists(self):
        """Test that error_occurred signal exists."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker
        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1')
            assert hasattr(worker, 'error_occurred')

    def test_oid_query_result_signal_exists(self):
        """Test that oid_query_result signal exists."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker
        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1')
            assert hasattr(worker, 'oid_query_result')


class TestSNMPWorkerOIDQuery:
    """Test SNMPWorker OID query functionality."""

    def test_query_oid_method_exists(self):
        """Test that query_oid method exists."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker
        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1')
            assert hasattr(worker, 'query_oid')
            assert callable(worker.query_oid)

    def test_query_oid_accepts_oid_parameter(self):
        """Test that query_oid accepts an OID parameter."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker
        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1')
            # Should accept string OID
            worker.query_oid('.1.3.6.1.2.1.1.1.0')


class TestSNMPWorkerStop:
    """Test SNMPWorker stop functionality."""

    def test_stop_method_exists(self):
        """Test that stop method exists."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker
        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1')
            assert hasattr(worker, 'stop')
            assert callable(worker.stop)

    def test_stop_sets_running_to_false(self):
        """Test that stop sets _running to False."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker
        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1')
            worker._running = True  # Simulate running
            worker.stop()
            assert worker._running is False

    def test_stop_calls_wait(self):
        """Test that stop calls wait."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker
        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1')
            with patch.object(worker, 'wait') as mock_wait:
                worker.stop()
                mock_wait.assert_called()


class TestSNMPWorkerQThread:
    """Test SNMPWorker QThread inheritance."""

    def test_worker_inherits_from_qthread(self):
        """Test that SNMPWorker inherits from QThread."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker
        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1')
            from PySide6.QtCore import QThread
            assert isinstance(worker, QThread)


class TestSNMPWorkerHostConfiguration:
    """Test SNMPWorker host configuration."""

    def test_worker_uses_provided_host(self):
        """Test that SNMPWorker uses provided host."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker
        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            worker = SNMPWorker(host='192.168.1.100')
            # Client should be initialized with the host
            mock_client.assert_called_once()
            call_kwargs = mock_client.call_args
            assert call_kwargs[1]['host'] == '192.168.1.100'

    def test_worker_default_host(self):
        """Test that SNMPWorker has a default host."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker
        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            # Should not raise error with default host
            worker = SNMPWorker()
            mock_client.assert_called_once()
