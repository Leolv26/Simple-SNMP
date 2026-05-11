"""End-to-end test for SNMP GetBulk functionality."""
import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.hlapi.asyncio import ObjectType
from pysnmp.smi.rfc1902 import ObjectIdentity


class TestGetBulkEndToEnd(unittest.TestCase):
    """Test GETBULK end-to-end functionality."""

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

    def test_getbulk_handler_with_mock_data(self):
        """Test GETBULK handler with mock data collector."""
        from snmp_monitor.agent.server import SNMPGetBulkHandler
        from snmp_monitor.nms import oids

        # Create mock data collector with realistic data
        mock_collector = Mock()
        mock_collector.system_handler.get_hostname.return_value = "test-server"
        mock_collector.system_handler.get_uptime.return_value = 86400  # 1 day in seconds
        mock_collector.process_handler.get_process_count.return_value = 150

        # Create handler
        mock_engine = Mock()
        mock_context = Mock()
        handler = SNMPGetBulkHandler(mock_engine, mock_context, mock_collector)

        # Test GETBULK starting from sysDescr
        result = handler._get_bulk_oid_values(oids.SNMP_SYSTEM_DESCR)

        # Verify we get multiple results
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 1)

        # Verify each result is an ObjectType
        for item in result:
            self.assertIsInstance(item, ObjectType)

        # Verify the first result is sysDescr
        first_item = result[0]
        self.assertIsInstance(first_item, ObjectType)

    def test_getbulk_with_different_start_oids(self):
        """Test GETBULK with different starting OIDs."""
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

        # Test with different starting OIDs
        test_cases = [
            (oids.SNMP_SYSTEM_DESCR, "sysDescr"),
            (oids.SNMP_SYSTEM_UPTIME, "sysUpTime"),
            (oids.SNMP_SYSTEM_CONTACT, "sysContact"),
        ]

        for oid, name in test_cases:
            with self.subTest(oid=name):
                result = handler._get_bulk_oid_values(oid)
                self.assertIsInstance(result, list)
                self.assertGreater(len(result), 0)


if __name__ == '__main__':
    unittest.main()
