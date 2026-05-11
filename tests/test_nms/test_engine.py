"""Unit tests for NMS Engine module."""
import unittest
from unittest.mock import Mock, patch, MagicMock
from snmp_monitor.nms.engine import NMSEngine


class TestNMSEngine(unittest.TestCase):
    """Test NMSEngine class."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = NMSEngine()

    def test_engine_creation(self):
        """Test engine creation."""
        self.assertIsNotNone(self.engine)
        self.assertIsNotNone(self.engine.client)
        # trap_receiver has been removed from NMSEngine as per design evolution
        # Trap handling is now done directly in GUI layer

    def test_engine_poll(self):
        """Test poll_once functionality."""
        with patch.object(self.engine.client, 'get_bulk') as mock_get:
            mock_get.return_value = [
                ((1, 3, 6, 1, 4, 1, 2021, 4, 5, 0), '45'),
            ]
            result = self.engine.poll_once()

            self.assertIsNotNone(result)
            self.assertIn((1, 3, 6, 1, 4, 1, 2021, 4, 5, 0), result)
            mock_get.assert_called_once()

    def test_engine_poll_execution(self):
        """Test that poll_once executes and returns data."""
        with patch.object(self.engine.client, 'get_bulk') as mock_get:
            mock_get.return_value = []

            result = self.engine.poll_once()

            self.assertIsNotNone(result)
            self.assertIsInstance(result, dict)

    def test_engine_signals_emit(self):
        """Test that data_ready signal fires after poll."""
        signals_received = []

        def on_data_ready(data):
            signals_received.append(data)

        self.engine.data_ready.connect(on_data_ready)

        with patch.object(self.engine.client, 'get_bulk') as mock_get:
            mock_get.return_value = [
                ((1, 3, 6, 1, 4, 1, 2021, 4, 5, 0), '45'),
            ]
            self.engine.poll_once()

        self.assertGreater(len(signals_received), 0)
        self.assertIn((1, 3, 6, 1, 4, 1, 2021, 4, 5, 0), signals_received[0])

    def test_engine_start_and_stop(self):
        """Test starting and stopping the engine."""
        self.engine.start()

        # Give the thread time to start
        import time
        time.sleep(0.1)

        self.assertTrue(self.engine._running)

        self.engine.stop()
        self.engine.wait(timeout=1)

        self.assertFalse(self.engine._running)

    def test_engine_poll_once_when_not_running(self):
        """Test poll_once can be called even when not running."""
        with patch.object(self.engine.client, 'get_bulk') as mock_get:
            mock_get.return_value = []

            result = self.engine.poll_once()

            self.assertIsNotNone(result)

    def test_engine_trap_received_signal(self):
        """Test trap_received signal is emitted when trap arrives."""
        signals_received = []

        def on_trap_received(data):
            signals_received.append(data)

        self.engine.trap_received.connect(on_trap_received)

        # Simulate trap receiving via callback
        trap_data = {'type': 'trap', 'source': '127.0.0.1'}
        self.engine._on_trap_received(trap_data)

        self.assertEqual(len(signals_received), 1)
        self.assertEqual(signals_received[0], trap_data)

    def test_engine_error_signal(self):
        """Test error_occurred signal is emitted on errors."""
        signals_received = []

        def on_error_occurred(error_message):
            signals_received.append(error_message)

        self.engine.error_occurred.connect(on_error_occurred)

        # Manually emit error through the signal system
        self.engine.error_occurred.emit("Test error")

        self.assertEqual(len(signals_received), 1)
        self.assertEqual(signals_received[0], "Test error")

    def test_engine_poll_multiple_metrics(self):
        """Test polling multiple metrics at once."""
        with patch.object(self.engine.client, 'get_bulk') as mock_get:
            mock_get.return_value = [
                ((1, 3, 6, 1, 4, 1, 2021, 4, 5, 0), '45'),  # cpu
                ((1, 3, 6, 1, 4, 1, 2021, 4, 6, 0), '70'),  # memory
            ]
            result = self.engine.poll_once()

            self.assertEqual(len(result), 2)
            self.assertIn((1, 3, 6, 1, 4, 1, 2021, 4, 5, 0), result)
            self.assertIn((1, 3, 6, 1, 4, 1, 2021, 4, 6, 0), result)


if __name__ == '__main__':
    unittest.main()
