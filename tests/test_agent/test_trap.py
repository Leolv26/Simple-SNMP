"""Unit tests for trap module - SNMP Trap sender."""
import unittest
from unittest.mock import Mock, patch, MagicMock
from snmp_monitor.agent import trap


class TestTrapSender(unittest.TestCase):
    """Test TrapSender class."""

    def setUp(self):
        """Set up test fixtures."""
        self.sender = trap.TrapSender()

    def test_trap_sender_initialization(self):
        """Test TrapSender initialization."""
        self.assertIsNotNone(self.sender)
        self.assertEqual(self.sender.target_host, '127.0.0.1')
        self.assertIsInstance(self.sender.target_port, int)
        self.assertIsInstance(self.sender.community, str)

    def test_load_config(self):
        """Test configuration loading."""
        config = self.sender._load_config("config.yaml")
        self.assertIn('nms', config)
        self.assertIn('agent_host', config['nms'])
        self.assertIn('trap_port', config['nms'])

    def test_send_trap(self):
        """Test sending a trap."""
        with patch('snmp_monitor.agent.trap.asyncio.run') as mock_run:
            mock_run.return_value = (None, 0, 0, [])
            result = self.sender.send(".1.3.6.1.6.3.1.1.5.1", "Test trap")
            self.assertTrue(result)

    def test_send_threshold_alert(self):
        """Test sending threshold alert trap."""
        with patch.object(self.sender, 'send') as mock_send:
            mock_send.return_value = True
            result = self.sender.send_threshold_alert("cpu", 85.0, 80.0)
            self.assertTrue(result)
            mock_send.assert_called_once()

    def test_send_trap_failure(self):
        """Test trap send failure handling."""
        with patch('snmp_monitor.agent.trap.asyncio.run', side_effect=Exception("Test error")):
            result = self.sender.send(".1.3.6.1.6.3.1.1.5.1", "Test trap")
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
