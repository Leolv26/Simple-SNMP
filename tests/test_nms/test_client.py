"""Unit tests for SNMP client module."""
import unittest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from snmp_monitor.nms import client, oids


class TestSNMPClient(unittest.TestCase):
    """Test SNMPClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = client.SNMPClient('192.168.1.1', 'public', version=oids.SNMP_VERSION_2C)

    def test_client_initialization(self):
        """Test client initialization with parameters."""
        self.assertEqual(self.client.host, '192.168.1.1')
        self.assertEqual(self.client.community, 'public')
        self.assertEqual(self.client.version, oids.SNMP_VERSION_2C)
        self.assertEqual(self.client.timeout, 5)
        self.assertEqual(self.client.retries, 2)

    def test_client_initialization_with_timeout_and_retries(self):
        """Test client initialization with custom timeout and retries."""
        client_obj = client.SNMPClient(
            '192.168.1.1',
            'public',
            version=oids.SNMP_VERSION_2C,
            timeout=10,
            retries=3
        )
        self.assertEqual(client_obj.timeout, 10)
        self.assertEqual(client_obj.retries, 3)

    def test_get_system_info(self):
        """Test getting system information."""
        with patch.object(self.client, 'get') as mock_get:
            # Mock multiple calls to get
            mock_get.side_effect = [
                (oids.SNMP_SYSTEM_NAME, 'test_host'),
                (oids.SNMP_SYSTEM_DESCR, 'Test Description'),
                (oids.SNMP_SYSTEM_UPTIME, '12345'),
                (oids.SNMP_SYSTEM_CONTACT, 'admin@test.com'),
                (oids.SNMP_SYSTEM_LOCATION, 'Data Center 1')
            ]
            result = self.client.get_system_info()

            self.assertIn('hostname', result)
            self.assertEqual(result['hostname'], 'test_host')
            self.assertEqual(result['description'], 'Test Description')
            self.assertEqual(result['uptime'], '12345')
            self.assertEqual(result['contact'], 'admin@test.com')
            self.assertEqual(result['location'], 'Data Center 1')

    def test_get_interface_list(self):
        """Test getting list of network interfaces."""
        with patch.object(self.client, 'get_next') as mock_get_next:
            mock_get_next.return_value = [
                (oids.SNMP_IF_DESCR + (1,), 'eth0'),
                (oids.SNMP_IF_DESCR + (2,), 'eth1')
            ]
            result = self.client.get_interface_list()

            self.assertEqual(len(result), 2)
            self.assertEqual(result[0][1], 'eth0')
            mock_get_next.assert_called_once()

    def test_get_interface_stats(self):
        """Test getting interface statistics."""
        with patch.object(self.client, 'get') as mock_get:
            # Mock multiple calls to get for different interface stats
            mock_get.side_effect = [
                (oids.SNMP_IF_TYPE + (1,), '6'),  # Ethernet
                (oids.SNMP_IF_SPEED + (1,), '1000000000'),  # 1 Gbps
                (oids.SNMP_IF_ADMIN_STATUS + (1,), '1'),  # Up
                (oids.SNMP_IF_OPER_STATUS + (1,), '1'),  # Up
                (oids.SNMP_IF_IN_OCTETS + (1,), '1000'),
                (oids.SNMP_IF_OUT_OCTETS + (1,), '2000')
            ]
            result = self.client.get_interface_stats(1)

            self.assertIn('type', result)
            self.assertEqual(result['type'], '6')
            self.assertEqual(result['speed'], '1000000000')
            self.assertEqual(result['admin_status'], '1')
            self.assertEqual(result['oper_status'], '1')
            self.assertEqual(result['in_octets'], '1000')
            self.assertEqual(result['out_octets'], '2000')

    def test_get_process_count(self):
        """Test getting process count."""
        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value = (oids.SNMP_PROC_COUNT, '50')
            result = self.client.get_process_count()

            self.assertEqual(result, 50)
            mock_get.assert_called_with(oids.SNMP_PROC_COUNT)

    def test_get_storage_info(self):
        """Test getting storage information."""
        with patch.object(self.client, 'get_next') as mock_get_next:
            # Mock multiple get_next calls
            mock_get_next.side_effect = [
                [(oids.SNMP_STORAGE_DESCR + (1,), '/'), (oids.SNMP_STORAGE_DESCR + (2,), '/home')],
                [(oids.SNMP_STORAGE_SIZE + (1,), '1000000'), (oids.SNMP_STORAGE_SIZE + (2,), '5000000')],
                [(oids.SNMP_STORAGE_USED + (1,), '500000'), (oids.SNMP_STORAGE_USED + (2,), '2500000')]
            ]
            result = self.client.get_storage_info()

            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['path'], '/')
            self.assertEqual(result[0]['size'], '1000000')
            self.assertEqual(result[0]['used'], '500000')
            self.assertEqual(result[1]['path'], '/home')
            self.assertEqual(result[1]['size'], '5000000')
            self.assertEqual(result[1]['used'], '2500000')

    def test_get_method_with_error(self):
        """Test SNMP GET operation with error."""
        with patch.object(self.client, '_get_async') as mock_async:
            mock_async.return_value = None
            result = self.client.get(oids.SNMP_SYSTEM_NAME)

            self.assertIsNone(result)

    def test_process_count_with_error(self):
        """Test process count when SNMP get fails."""
        with patch.object(self.client, 'get') as mock_get:
            mock_get.return_value = None
            result = self.client.get_process_count()

            self.assertEqual(result, 0)


class TestSNMPClientErrors(unittest.TestCase):
    """Test SNMPClient error handling."""

    def test_connection_error(self):
        """Test connection error handling."""
        client_obj = client.SNMPClient('invalid-host', 'public', version=oids.SNMP_VERSION_2C)

        with patch.object(client_obj, '_get_async') as mock_async:
            mock_async.side_effect = Exception("Connection error")

            with self.assertRaises(Exception) as context:
                client_obj.get(oids.SNMP_SYSTEM_NAME)

            self.assertIn('Connection error', str(context.exception))


if __name__ == '__main__':
    unittest.main()
