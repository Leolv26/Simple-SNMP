"""Unit tests for ThresholdMonitor class in trap.py."""
import unittest
from unittest.mock import Mock, patch, MagicMock
import time

from snmp_monitor.agent.trap import ThresholdMonitor, TrapSender
from snmp_monitor.agent.handlers import SNMPDataCollector


class TestThresholdMonitor(unittest.TestCase):
    """Test ThresholdMonitor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_data_collector = Mock(spec=SNMPDataCollector)
        self.mock_trap_sender = Mock(spec=TrapSender)

    def test_initialization(self):
        """Test ThresholdMonitor initialization."""
        thresholds = {'cpu': 80, 'memory': 85, 'disk': 90}
        monitor = ThresholdMonitor(
            data_collector=self.mock_data_collector,
            trap_sender=self.mock_trap_sender,
            thresholds=thresholds,
            check_interval=1.0,
            cooldown_duration=300.0
        )
        self.assertIsNotNone(monitor)
        self.assertEqual(monitor._thresholds, thresholds)
        self.assertEqual(monitor._check_interval, 1.0)

    def test_check_once_cpu_exceeded(self):
        """Test CPU threshold exceeded detection."""
        self.mock_data_collector.collect_all_data.return_value = {
            'system': {
                'cpu_percent': 85,
                'memory': {'percent': 50},
                'disk': {'percent': 40}
            }
        }
        thresholds = {'cpu': 80, 'memory': 85, 'disk': 90}
        monitor = ThresholdMonitor(
            self.mock_data_collector, self.mock_trap_sender, thresholds, 1.0, 300.0
        )
        alerts = monitor._check_once()
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0][0], 'cpu')
        self.assertEqual(alerts[0][1], 85)

    def test_check_once_memory_exceeded(self):
        """Test memory threshold exceeded detection."""
        self.mock_data_collector.collect_all_data.return_value = {
            'system': {
                'cpu_percent': 50,
                'memory': {'percent': 90},
                'disk': {'percent': 40}
            }
        }
        thresholds = {'cpu': 80, 'memory': 85, 'disk': 90}
        monitor = ThresholdMonitor(
            self.mock_data_collector, self.mock_trap_sender, thresholds, 1.0, 300.0
        )
        alerts = monitor._check_once()
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0][0], 'memory')
        self.assertEqual(alerts[0][1], 90)

    def test_check_once_disk_exceeded(self):
        """Test disk threshold exceeded detection."""
        self.mock_data_collector.collect_all_data.return_value = {
            'system': {
                'cpu_percent': 50,
                'memory': {'percent': 50},
                'disk': {'percent': 95}
            }
        }
        thresholds = {'cpu': 80, 'memory': 85, 'disk': 90}
        monitor = ThresholdMonitor(
            self.mock_data_collector, self.mock_trap_sender, thresholds, 1.0, 300.0
        )
        alerts = monitor._check_once()
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0][0], 'disk')
        self.assertEqual(alerts[0][1], 95)

    def test_check_once_multiple_exceeded(self):
        """Test multiple thresholds exceeded."""
        self.mock_data_collector.collect_all_data.return_value = {
            'system': {
                'cpu_percent': 90,
                'memory': {'percent': 95},
                'disk': {'percent': 40}
            }
        }
        thresholds = {'cpu': 80, 'memory': 85, 'disk': 90}
        monitor = ThresholdMonitor(
            self.mock_data_collector, self.mock_trap_sender, thresholds, 1.0, 300.0
        )
        alerts = monitor._check_once()
        self.assertEqual(len(alerts), 2)
        alert_metrics = {a[0] for a in alerts}
        self.assertIn('cpu', alert_metrics)
        self.assertIn('memory', alert_metrics)

    def test_check_once_no_exceeded(self):
        """Test no threshold exceeded."""
        self.mock_data_collector.collect_all_data.return_value = {
            'system': {
                'cpu_percent': 50,
                'memory': {'percent': 50},
                'disk': {'percent': 40}
            }
        }
        thresholds = {'cpu': 80, 'memory': 85, 'disk': 90}
        monitor = ThresholdMonitor(
            self.mock_data_collector, self.mock_trap_sender, thresholds, 1.0, 300.0
        )
        alerts = monitor._check_once()
        self.assertEqual(len(alerts), 0)

    def test_check_once_value_equals_threshold_not_exceeded(self):
        """Test that value equal to threshold is not exceeded."""
        self.mock_data_collector.collect_all_data.return_value = {
            'system': {
                'cpu_percent': 80,
                'memory': {'percent': 50},
                'disk': {'percent': 40}
            }
        }
        thresholds = {'cpu': 80, 'memory': 85, 'disk': 90}
        monitor = ThresholdMonitor(
            self.mock_data_collector, self.mock_trap_sender, thresholds, 1.0, 300.0
        )
        alerts = monitor._check_once()
        self.assertEqual(len(alerts), 0)

    def test_cooldown_prevents_duplicate_traps(self):
        """Test cooldown mechanism prevents sending duplicate traps."""
        self.mock_data_collector.collect_all_data.return_value = {
            'system': {
                'cpu_percent': 85,
                'memory': {'percent': 50},
                'disk': {'percent': 40}
            }
        }
        thresholds = {'cpu': 80, 'memory': 85, 'disk': 90}
        monitor = ThresholdMonitor(
            self.mock_data_collector, self.mock_trap_sender, thresholds, 1.0, 300.0
        )

        # First check - should get alert
        alerts1 = monitor._check_once()
        self.assertEqual(len(alerts1), 1)

        # Immediate second check - should be in cooldown, no alert
        alerts2 = monitor._check_once()
        self.assertEqual(len(alerts2), 0)

    def test_cooldown_allows_after_duration(self):
        """Test that cooldown expires and allows new alerts."""
        self.mock_data_collector.collect_all_data.return_value = {
            'system': {
                'cpu_percent': 85,
                'memory': {'percent': 50},
                'disk': {'percent': 40}
            }
        }
        thresholds = {'cpu': 80, 'memory': 85, 'disk': 90}
        monitor = ThresholdMonitor(
            self.mock_data_collector, self.mock_trap_sender, thresholds, 1.0, 0.1
        )

        # First check
        alerts1 = monitor._check_once()
        self.assertEqual(len(alerts1), 1)

        # Wait for cooldown to expire
        time.sleep(0.15)

        # Second check - should get alert again
        alerts2 = monitor._check_once()
        self.assertEqual(len(alerts2), 1)

    def test_start_stop(self):
        """Test monitor can be started and stopped."""
        # Set mock return value so background thread doesn't crash
        self.mock_data_collector.collect_all_data.return_value = {
            'system': {'cpu_percent': 50, 'memory': {'percent': 50}, 'disk': {'percent': 50}}
        }
        thresholds = {'cpu': 80, 'memory': 85, 'disk': 90}
        monitor = ThresholdMonitor(
            self.mock_data_collector, self.mock_trap_sender, thresholds, 1.0, 300.0
        )
        monitor.start()
        self.assertTrue(monitor._running)
        self.assertIsNotNone(monitor._thread)
        monitor.stop()
        monitor._thread.join(timeout=2.0)
        self.assertFalse(monitor._running)


class TestThresholdMonitorWithRealDataCollector(unittest.TestCase):
    """Test ThresholdMonitor with real data collector (real psutil calls)."""

    def test_check_once_with_real_collector(self):
        """Test check_once with real data collector."""
        data_collector = SNMPDataCollector()
        mock_trap_sender = Mock(spec=TrapSender)
        thresholds = {'cpu': 0, 'memory': 0, 'disk': 0}
        monitor = ThresholdMonitor(
            data_collector, mock_trap_sender, thresholds, 1.0, 300.0
        )
        alerts = monitor._check_once()
        self.assertGreaterEqual(len(alerts), 1)


if __name__ == '__main__':
    unittest.main()
