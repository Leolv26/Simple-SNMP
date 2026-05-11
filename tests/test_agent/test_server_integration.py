"""Integration test for server.py with ThresholdMonitor."""
import unittest
from unittest.mock import Mock, patch

from snmp_monitor.agent.server import SNMPAgentServer, get_config


class TestSNMPAgentServerWithThresholdMonitor(unittest.TestCase):

    def test_server_creates_threshold_monitor_on_init(self):
        with patch('snmp_monitor.agent.server.handlers.SNMPDataCollector') as mock_collector:
            with patch('snmp_monitor.agent.server.agent_trap.TrapSender') as mock_sender:
                mock_sender.return_value = Mock()
                mock_collector.return_value = Mock()
                with patch('snmp_monitor.agent.server.get_config') as mock_config:
                    mock_config.return_value = {
                        'host': '0.0.0.0', 'port': 161, 'community': 'public',
                        'thresholds': {'cpu': 80, 'memory': 85, 'disk': 90}
                    }
                    server = SNMPAgentServer()
                    self.assertIsNotNone(server._threshold_monitor)

    def test_server_starts_threshold_monitor(self):
        with patch('snmp_monitor.agent.server.handlers.SNMPDataCollector') as mock_collector:
            with patch('snmp_monitor.agent.server.agent_trap.TrapSender') as mock_sender:
                mock_sender.return_value = Mock()
                mock_collector.return_value = Mock()
                with patch('snmp_monitor.agent.server.get_config') as mock_config:
                    mock_config.return_value = {
                        'host': '0.0.0.0', 'port': 161, 'community': 'public',
                        'thresholds': {'cpu': 80, 'memory': 85, 'disk': 90}
                    }
                    server = SNMPAgentServer()
                    with patch.object(server._threshold_monitor, 'start') as mock_start:
                        with patch.object(server, '_start_snmp_engine'):
                            with patch.object(server.snmp_engine.transportDispatcher, 'runDispatcher'):
                                server.start()
                                mock_start.assert_called_once()
                    with patch.object(server._threshold_monitor, 'stop'):
                        with patch.object(server, '_stop_snmp_engine'):
                            server.stop()

    def test_server_stops_threshold_monitor(self):
        with patch('snmp_monitor.agent.server.handlers.SNMPDataCollector') as mock_collector:
            with patch('snmp_monitor.agent.server.agent_trap.TrapSender') as mock_sender:
                mock_sender.return_value = Mock()
                mock_collector.return_value = Mock()
                with patch('snmp_monitor.agent.server.get_config') as mock_config:
                    mock_config.return_value = {
                        'host': '0.0.0.0', 'port': 161, 'community': 'public',
                        'thresholds': {'cpu': 80, 'memory': 85, 'disk': 90}
                    }
                    server = SNMPAgentServer()
                    with patch.object(server._threshold_monitor, 'stop') as mock_stop:
                        with patch.object(server, '_stop_snmp_engine'):
                            server.stop()
                            mock_stop.assert_called_once()


if __name__ == '__main__':
    unittest.main()
