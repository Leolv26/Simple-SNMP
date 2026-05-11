"""Unit tests for SNMP trap receiver module."""
import unittest
import threading
import time
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from snmp_monitor.nms import trap_receiver


class TestTrapReceiver(unittest.TestCase):
    """Test TrapReceiver class."""

    def setUp(self):
        """Set up test fixtures."""
        self.receiver = trap_receiver.TrapReceiver()

    def test_receiver_initialization(self):
        """Test trap receiver initialization."""
        self.assertFalse(self.receiver._running)
        self.assertEqual(self.receiver._port, 162)
        self.assertIsNone(self.receiver._socket)
        self.assertEqual(self.receiver._callbacks, [])

    def test_receiver_initialization_with_custom_port(self):
        """Test trap receiver initialization with custom port."""
        receiver = trap_receiver.TrapReceiver(port=1162)
        self.assertEqual(receiver._port, 1162)

    def test_register_callback(self):
        """Test registering a callback function."""
        callback_mock = Mock()
        self.receiver.register_callback(callback_mock)

        self.assertEqual(len(self.receiver._callbacks), 1)
        self.assertEqual(self.receiver._callbacks[0], callback_mock)

    def test_register_multiple_callbacks(self):
        """Test registering multiple callback functions."""
        callback1 = Mock()
        callback2 = Mock()
        callback3 = Mock()

        self.receiver.register_callback(callback1)
        self.receiver.register_callback(callback2)
        self.receiver.register_callback(callback3)

        self.assertEqual(len(self.receiver._callbacks), 3)
        self.assertIn(callback1, self.receiver._callbacks)
        self.assertIn(callback2, self.receiver._callbacks)
        self.assertIn(callback3, self.receiver._callbacks)

    def test_unregister_callback(self):
        """Test unregistering a callback function."""
        callback1 = Mock()
        callback2 = Mock()

        self.receiver.register_callback(callback1)
        self.receiver.register_callback(callback2)
        self.receiver.unregister_callback(callback1)

        self.assertEqual(len(self.receiver._callbacks), 1)
        self.assertEqual(self.receiver._callbacks[0], callback2)

    def test_unregister_nonexistent_callback(self):
        """Test unregistering a callback that doesn't exist."""
        callback1 = Mock()
        callback2 = Mock()

        self.receiver.register_callback(callback1)
        # Should not raise an error
        self.receiver.unregister_callback(callback2)

        self.assertEqual(len(self.receiver._callbacks), 1)

    def test_default_callback_not_in_list(self):
        """Test that default callback is not in callbacks list."""
        self.assertNotIn(self.receiver.default_callback, self.receiver._callbacks)

    def test_default_callback_exists(self):
        """Test that default_callback method exists and is callable."""
        self.assertTrue(hasattr(self.receiver, 'default_callback'))
        self.assertTrue(callable(self.receiver.default_callback))

    def test_default_callback_behavior(self):
        """Test default callback behavior with trap data."""
        trap_data = {'source': '192.168.1.1', 'oid': '1.3.6.1.4.1.99999'}
        # Should not raise an error
        self.receiver.default_callback(trap_data)


class TestTrapReceiverAsync(unittest.TestCase):
    """Test TrapReceiver asynchronous operations."""

    def test_is_running_property(self):
        """Test is_running property."""
        receiver = trap_receiver.TrapReceiver()
        self.assertFalse(receiver.is_running)

    def test_start_sets_running_flag(self):
        """Test that start() sets _running flag to True."""
        receiver = trap_receiver.TrapReceiver()
        with patch.object(receiver, '_create_socket'):
            receiver.start()
            self.assertTrue(receiver._running)

    def test_stop_clears_running_flag(self):
        """Test that stop() clears _running flag."""
        receiver = trap_receiver.TrapReceiver()
        receiver._running = True
        with patch.object(receiver, '_close_socket'):
            receiver.stop()
            self.assertFalse(receiver._running)

    def test_socket_timeout_on_stop(self):
        """Test that socket timeout is set during stop."""
        receiver = trap_receiver.TrapReceiver()
        mock_socket = Mock()
        receiver._socket = mock_socket
        receiver._running = True

        with patch.object(receiver, '_close_socket'):
            receiver.stop()
            mock_socket.settimeout.assert_called_once()

    @patch('socket.socket')
    def test_create_socket_binds_to_port(self, mock_socket_class):
        """Test that socket binds to specified port."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket

        receiver = trap_receiver.TrapReceiver()
        receiver._create_socket()

        mock_socket_class.assert_called_once()
        mock_socket.bind.assert_called_once()
        mock_socket.settimeout.assert_called_once()

    def test_create_socket_handles_error(self):
        """Test error handling during socket creation."""
        receiver = trap_receiver.TrapReceiver()

        with patch('socket.socket') as mock_socket_class:
            mock_socket_class.side_effect = Exception("Socket error")

            with self.assertRaises(Exception) as context:
                receiver._create_socket()

            self.assertIn('Socket error', str(context.exception))

    @patch('socket.socket')
    def test_close_socket_closes_connection(self, mock_socket_class):
        """Test that close_socket properly closes the socket."""
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket

        receiver = trap_receiver.TrapReceiver()
        receiver._socket = mock_socket
        receiver._close_socket()

        mock_socket.close.assert_called_once()
        self.assertIsNone(receiver._socket)


class TestTrapReceiverWithThread(unittest.TestCase):
    """Test TrapReceiver with threading to simulate async behavior."""

    def test_start_starts_thread(self):
        """Test that start() creates and starts a thread."""
        receiver = trap_receiver.TrapReceiver()

        with patch.object(receiver, '_create_socket'), \
             patch.object(receiver, '_receive_loop') as mock_receive_loop:

            receiver.start()
            time.sleep(0.1)  # Give thread time to start

            self.assertTrue(receiver._running)
            # Thread should be running
            self.assertIsNotNone(receiver._thread)
            self.assertTrue(receiver._thread.is_alive())

            # Stop the receiver to clean up
            receiver.stop()
            receiver._thread.join(timeout=1.0)

    def test_receive_loop_stops_when_not_running(self):
        """Test that receive_loop stops when _running is False."""
        receiver = trap_receiver.TrapReceiver()
        receiver._running = False

        with patch.object(receiver, '_socket') as mock_socket:
            # Should not block because _running is False
            receiver._thread_loop()
            mock_socket.recvfrom.assert_not_called()

    def test_receive_loop_calls_callbacks(self):
        """Test that receive_loop calls registered callbacks."""
        receiver = trap_receiver.TrapReceiver()
        callback_mock = Mock()
        receiver.register_callback(callback_mock)
        receiver._running = True

        mock_socket = Mock()
        mock_socket.recvfrom.return_value = (b'test_data', ('192.168.1.1', 162))
        receiver._socket = mock_socket

        with patch.object(receiver, '_parse_trap') as mock_parse:
            mock_parse.return_value = {'test': 'data'}

            # Run one iteration of receive_loop
            receiver._receive_loop()
            callback_mock.assert_called_once()

    def test_parse_trap_returns_dict(self):
        """Test that _parse_trap returns a dictionary."""
        receiver = trap_receiver.TrapReceiver()

        # Create mock trap data
        trap_data = b'test_trap_data'

        # This should return a dictionary
        result = receiver._parse_trap(trap_data)
        self.assertIsInstance(result, dict)

    def test_start_stop_sequence(self):
        """Test complete start-stop sequence."""
        receiver = trap_receiver.TrapReceiver()

        with patch.object(receiver, '_create_socket'), \
             patch.object(receiver, '_thread_loop') as mock_loop:

            # Start
            receiver.start()
            time.sleep(0.05)
            self.assertTrue(receiver._running)

            # Stop
            receiver.stop()
            time.sleep(0.05)
            self.assertFalse(receiver._running)

    def test_parse_trap_with_valid_data(self):
        """Test parsing of valid trap data."""
        receiver = trap_receiver.TrapReceiver()

        # Test with minimal trap data simulation
        trap_data = b'\x30\x1a...'  # Minimal ASN.1 structure

        result = receiver._parse_trap(trap_data)

        self.assertIsInstance(result, dict)
        # Check that the result has expected trap structure
        self.assertIn('type', result)
        self.assertIn('length', result)
        self.assertIn('raw_data', result)


if __name__ == '__main__':
    unittest.main()
