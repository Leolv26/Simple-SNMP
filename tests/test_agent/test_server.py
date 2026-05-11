"""Unit tests for SNMP Agent server module."""
import unittest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity.rfc3413 import cmdrsp, context


class TestSNMPAgentServer(unittest.TestCase):
    """Test SNMPAgentServer class."""

    def setUp(self):
        """Set up test fixtures."""
        # Patch the server module import
        self.server_module_patcher = patch.dict('sys.modules', {
            'snmp_monitor.agent.handlers': Mock()
        })
        self.server_module_patcher.start()

    def tearDown(self):
        """Clean up test fixtures."""
        self.server_module_patcher.stop()

    def test_server_module_exists(self):
        """Test that server module can be imported."""
        from snmp_monitor.agent import server
        self.assertIsNotNone(server)

    def test_server_class_exists(self):
        """Test that SNMPAgentServer class can be imported."""
        from snmp_monitor.agent.server import SNMPAgentServer
        self.assertIsNotNone(SNMPAgentServer)

    def test_server_initialization(self):
        """Test that server initializes with correct configuration."""
        from snmp_monitor.agent.server import SNMPAgentServer

        # Mock the config for this test
        with patch('snmp_monitor.agent.server.get_config') as mock_config:
            mock_config.return_value = {
                'host': 'localhost',
                'port': 161,
                'community': 'public'
            }

            # Create server instance
            server = SNMPAgentServer()

            # Verify it was created
            self.assertIsNotNone(server)
            self.assertEqual(server.host, 'localhost')
            self.assertEqual(server.port, 161)
            self.assertEqual(server.community, 'public')

    def test_server_listens_on_port_161(self):
        """Test that server listens on UDP port 161."""
        from snmp_monitor.agent.server import SNMPAgentServer

        # Default port should be 161
        with patch('snmp_monitor.agent.server.get_config') as mock_config:
            mock_config.return_value = {
                'host': '0.0.0.0',
                'community': 'public'
            }

            server = SNMPAgentServer()
            self.assertEqual(server.port, 161)

    def test_get_request_handler(self):
        """Test that Get request handler is set up."""
        from snmp_monitor.agent.server import SNMPAgentServer

        with patch('snmp_monitor.agent.server.get_config') as mock_config:
            mock_config.return_value = {
                'host': 'localhost',
                'port': 161,
                'community': 'public'
            }

            server = SNMPAgentServer()

            # Verify handler exists
            self.assertIsNotNone(server.get_handler)

    def test_getnext_request_handler(self):
        """Test that GetNext request handler is set up."""
        from snmp_monitor.agent.server import SNMPAgentServer

        with patch('snmp_monitor.agent.server.get_config') as mock_config:
            mock_config.return_value = {
                'host': 'localhost',
                'port': 161,
                'community': 'public'
            }

            server = SNMPAgentServer()

            # Verify handler exists
            self.assertIsNotNone(server.getnext_handler)

    def test_walk_request_handler(self):
        """Test that Walk request handler is set up."""
        from snmp_monitor.agent.server import SNMPAgentServer

        with patch('snmp_monitor.agent.server.get_config') as mock_config:
            mock_config.return_value = {
                'host': 'localhost',
                'port': 161,
                'community': 'public'
            }

            server = SNMPAgentServer()

            # Verify handler exists (Walk uses GetNext)
            self.assertIsNotNone(server.getnext_handler)

    def test_set_request_handler_exists(self):
        """Test that Set request handler is registered on the server."""
        from snmp_monitor.agent.server import SNMPAgentServer

        with patch('snmp_monitor.agent.server.get_config') as mock_config:
            mock_config.return_value = {
                'host': 'localhost',
                'port': 161,
                'community': 'public'
            }

            server = SNMPAgentServer()

            # Verify Set handler exists
            self.assertTrue(hasattr(server, 'set_handler'))
            self.assertIsNotNone(server.set_handler)

    def test_set_writable_oid_syscontact(self):
        """Test that sysContact is a writable OID."""
        from snmp_monitor.agent.server import SNMPAgentServer

        with patch('snmp_monitor.agent.server.get_config') as mock_config:
            mock_config.return_value = {
                'host': 'localhost',
                'port': 161,
                'community': 'public'
            }

            server = SNMPAgentServer()

            # sysContact should be writable
            self.assertTrue(server.set_handler.is_writable(oids.SNMP_SYSTEM_CONTACT))

    def test_set_readonly_oid_rejected(self):
        """Test that read-only OIDs are rejected by Set handler."""
        from snmp_monitor.agent.server import SNMPAgentServer

        with patch('snmp_monitor.agent.server.get_config') as mock_config:
            mock_config.return_value = {
                'host': 'localhost',
                'port': 161,
                'community': 'public'
            }

            server = SNMPAgentServer()

            # sysDescr should be read-only
            self.assertFalse(server.set_handler.is_writable(oids.SNMP_SYSTEM_DESCR))

    def test_set_handler_updates_writable_value(self):
        """Test that Set handler can update a writable OID value."""
        from snmp_monitor.agent.server import SNMPAgentServer

        with patch('snmp_monitor.agent.server.get_config') as mock_config:
            mock_config.return_value = {
                'host': 'localhost',
                'port': 161,
                'community': 'public'
            }

            server = SNMPAgentServer()

            # Set sysLocation value
            result = server.set_handler.set_value(oids.SNMP_SYSTEM_LOCATION, "Building A")
            self.assertTrue(result)

            # Verify the value was stored
            value = server.set_handler.get_value(oids.SNMP_SYSTEM_LOCATION)
            self.assertEqual(value, "Building A")

    def test_set_handler_rejects_readonly_update(self):
        """Test that Set handler rejects updates to read-only OIDs."""
        from snmp_monitor.agent.server import SNMPAgentServer

        with patch('snmp_monitor.agent.server.get_config') as mock_config:
            mock_config.return_value = {
                'host': 'localhost',
                'port': 161,
                'community': 'public'
            }

            server = SNMPAgentServer()

            # Attempt to set sysDescr (read-only) should fail
            result = server.set_handler.set_value(oids.SNMP_SYSTEM_DESCR, "hacked")
            self.assertFalse(result)

    def test_data_collector_integration(self):
        """Test integration with SNMPDataCollector."""
        from snmp_monitor.agent.server import SNMPAgentServer
        from snmp_monitor.agent import handlers

        with patch('snmp_monitor.agent.server.get_config') as mock_config:
            mock_config.return_value = {
                'host': 'localhost',
                'port': 161,
                'community': 'public'
            }

            server = SNMPAgentServer()

            # Verify data collector is initialized
            self.assertIsNotNone(server.data_collector)
            # The actual data_collector is the real class, not a mock
            # Test that it has the expected attributes
            self.assertTrue(hasattr(server.data_collector, 'system_handler'))
            self.assertTrue(hasattr(server.data_collector, 'process_handler'))

    def test_invalid_oid_handling(self):
        """Test handling of invalid OIDs."""
        from snmp_monitor.agent.server import SNMPAgentServer

        with patch('snmp_monitor.agent.server.get_config') as mock_config:
            mock_config.return_value = {
                'host': 'localhost',
                'port': 161,
                'community': 'public'
            }

            server = SNMPAgentServer()

            # Verify the server has error handling capability
            self.assertIsNotNone(server.error_handler)

    def test_server_start(self):
        """Test server start functionality."""
        from snmp_monitor.agent.server import SNMPAgentServer

        with patch('snmp_monitor.agent.server.get_config') as mock_config:
            mock_config.return_value = {
                'host': 'localhost',
                'port': 161,
                'community': 'public'
            }

            server = SNMPAgentServer()

            # Mock the actual SNMP engine start and dispatcher
            with patch.object(server._threshold_monitor, 'start'):
                with patch.object(server.snmp_engine.transportDispatcher, 'runDispatcher', return_value=None) as mock_run:
                    with patch.object(server, '_start_snmp_engine'):
                        server.start()

                        # Verify the methods were called
                        server._start_snmp_engine.assert_called_once()
                        mock_run.assert_called_once()

    def test_server_stop(self):
        """Test server stop functionality."""
        from snmp_monitor.agent.server import SNMPAgentServer

        with patch('snmp_monitor.agent.server.get_config') as mock_config:
            mock_config.return_value = {
                'host': 'localhost',
                'port': 161,
                'community': 'public'
            }

            server = SNMPAgentServer()

            # Mock the actual SNMP engine stop and threshold monitor stop
            with patch.object(server._threshold_monitor, 'stop'):
                with patch.object(server.snmp_engine.transportDispatcher, 'closeDispatcher', return_value=None) as mock_close:
                    server.stop()

                    # Verify the stop method was called
                    mock_close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
