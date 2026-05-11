"""Integration test for SNMP GetBulk functionality."""
import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.hlapi.asyncio import ObjectType


class TestGetBulkIntegration(unittest.TestCase):
    """Test GETBULK integration with agent server."""

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

    def test_getbulk_handler_processes_oids(self):
        """Test that GETBULK handler can process OIDs and return multiple values."""
        from snmp_monitor.agent.server import SNMPGetBulkHandler
        from snmp_monitor.nms import oids

        # Create mock data collector
        mock_collector = Mock()
        mock_collector.system_handler.get_hostname.return_value = "test-host"
        mock_collector.system_handler.get_uptime.return_value = 1000
        mock_collector.process_handler.get_process_count.return_value = 42

        # Create handler
        mock_engine = Mock()
        mock_context = Mock()
        handler = SNMPGetBulkHandler(mock_engine, mock_context, mock_collector)

        # Test _get_bulk_oid_values with a system OID
        result = handler._get_bulk_oid_values(oids.SNMP_SYSTEM_DESCR)

        # Should return multiple OID-value pairs
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

        # Each item should be an ObjectType
        for item in result:
            self.assertIsInstance(item, ObjectType)

    def test_getbulk_with_uptime_oid(self):
        """Test GETBULK starting from sysUpTime OID."""
        from snmp_monitor.agent.server import SNMPGetBulkHandler
        from snmp_monitor.nms import oids

        # Create mock data collector
        mock_collector = Mock()
        mock_collector.system_handler.get_hostname.return_value = "test-host"
        mock_collector.system_handler.get_uptime.return_value = 1000
        mock_collector.process_handler.get_process_count.return_value = 42

        # Create handler
        mock_engine = Mock()
        mock_context = Mock()
        handler = SNMPGetBulkHandler(mock_engine, mock_context, mock_collector)

        # Test with sysUpTime OID
        result = handler._get_bulk_oid_values(oids.SNMP_SYSTEM_UPTIME)

        # Should return multiple values starting from sysUpTime
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

        # First item should be an ObjectType
        self.assertIsInstance(result[0], ObjectType)

    def test_getbulk_prefix_matching(self):
        """Test that prefix matching works correctly."""
        from snmp_monitor.agent.server import SNMPGetBulkHandler

        mock_engine = Mock()
        mock_context = Mock()
        mock_collector = Mock()
        handler = SNMPGetBulkHandler(mock_engine, mock_context, mock_collector)

        # Test prefix matching
        self.assertTrue(handler._is_prefix((1, 3, 6), (1, 3, 6, 1, 2, 1)))
        self.assertTrue(handler._is_prefix((1, 3, 6, 1), (1, 3, 6, 1, 2, 1)))
        self.assertFalse(handler._is_prefix((1, 3, 6, 1, 2, 1, 2), (1, 3, 6, 1, 2, 1)))


if __name__ == '__main__':
    unittest.main()
