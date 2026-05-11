"""Unit tests for handlers module - data collection using psutil."""
import unittest
from unittest.mock import Mock, patch, MagicMock
from snmp_monitor.agent import handlers


class TestSystemInfoHandler(unittest.TestCase):
    """Test SystemInfoHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = handlers.SystemInfoHandler()

    def test_get_hostname(self):
        """Test getting hostname from system."""
        with patch('socket.gethostname', return_value='test-host'):
            result = self.handler.get_hostname()
            self.assertEqual(result, 'test-host')

    def test_get_uptime(self):
        """Test getting system uptime."""
        with patch('psutil.boot_time', return_value=1000000):
            # Boot time is 1000000, current time will be mocked
            with patch('time.time', return_value=1600000):
                result = self.handler.get_uptime()
                self.assertEqual(result, 600000)  # 600000 seconds

    def test_get_cpu_count(self):
        """Test getting CPU count."""
        with patch('psutil.cpu_count', return_value=8):
            result = self.handler.get_cpu_count()
            self.assertEqual(result, 8)

    def test_get_cpu_percent(self):
        """Test getting CPU usage percentage."""
        with patch('psutil.cpu_percent', return_value=25.5):
            result = self.handler.get_cpu_percent()
            self.assertEqual(result, 25.5)

    def test_get_memory_info(self):
        """Test getting memory information."""
        mock_mem = Mock()
        mock_mem.total = 16384 * 1024 * 1024  # 16GB
        mock_mem.available = 8192 * 1024 * 1024  # 8GB
        mock_mem.percent = 50.0

        with patch('psutil.virtual_memory', return_value=mock_mem):
            result = self.handler.get_memory_info()
            self.assertEqual(result['total'], 16384 * 1024 * 1024)
            self.assertEqual(result['available'], 8192 * 1024 * 1024)
            self.assertEqual(result['percent'], 50.0)

    def test_get_disk_info(self):
        """Test getting disk information."""
        mock_disk = Mock()
        mock_disk.total = 500 * 1024 * 1024 * 1024  # 500GB
        mock_disk.used = 250 * 1024 * 1024 * 1024  # 250GB
        mock_disk.free = 250 * 1024 * 1024 * 1024  # 250GB
        mock_disk.percent = 50.0

        with patch('psutil.disk_usage', return_value=mock_disk, args=('/')):
            result = self.handler.get_disk_info('/')
            self.assertEqual(result['total'], 500 * 1024 * 1024 * 1024)
            self.assertEqual(result['used'], 250 * 1024 * 1024 * 1024)
            self.assertEqual(result['free'], 250 * 1024 * 1024 * 1024)
            self.assertEqual(result['percent'], 50.0)

    def test_get_network_io(self):
        """Test getting network I/O statistics."""
        mock_io = Mock()
        mock_io.bytes_sent = 1024 * 1024  # 1MB
        mock_io.bytes_recv = 2 * 1024 * 1024  # 2MB
        mock_io.packets_sent = 1000
        mock_io.packets_recv = 2000

        with patch('psutil.net_io_counters', return_value=mock_io):
            result = self.handler.get_network_io()
            self.assertEqual(result['bytes_sent'], 1024 * 1024)
            self.assertEqual(result['bytes_recv'], 2 * 1024 * 1024)
            self.assertEqual(result['packets_sent'], 1000)
            self.assertEqual(result['packets_recv'], 2000)

    def test_get_all_stats(self):
        """Test getting all system statistics."""
        # Mock all dependencies
        with patch('socket.gethostname', return_value='test-host'):
            with patch('psutil.boot_time', return_value=1000000):
                with patch('time.time', return_value=1600000):
                    with patch('psutil.cpu_count', return_value=8):
                        with patch('psutil.cpu_percent', return_value=25.5):
                            mock_mem = Mock()
                            mock_mem.total = 16384 * 1024 * 1024
                            mock_mem.available = 8192 * 1024 * 1024
                            mock_mem.percent = 50.0
                            with patch('psutil.virtual_memory', return_value=mock_mem):
                                result = self.handler.get_all_stats()

                                self.assertEqual(result['hostname'], 'test-host')
                                self.assertEqual(result['uptime'], 600000)
                                self.assertEqual(result['cpu_count'], 8)
                                self.assertEqual(result['cpu_percent'], 25.5)
                                self.assertIn('memory', result)
                                self.assertIn('disk', result)
                                self.assertIn('network', result)


class TestProcessInfoHandler(unittest.TestCase):
    """Test ProcessInfoHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = handlers.ProcessInfoHandler()

    def test_get_process_count(self):
        """Test getting process count."""
        mock_process = Mock()
        with patch('psutil.process_iter', return_value=[mock_process] * 5):
            result = self.handler.get_process_count()
            self.assertEqual(result, 5)

    def test_get_top_processes(self):
        """Test getting top CPU processes."""
        mock_process1 = Mock()
        mock_process1.info = {'name': 'process1', 'pid': 100, 'cpu_percent': 50.0}
        mock_process1.cpu_percent.return_value = 50.0

        mock_process2 = Mock()
        mock_process2.info = {'name': 'process2', 'pid': 200, 'cpu_percent': 30.0}
        mock_process2.cpu_percent.return_value = 30.0

        with patch('psutil.process_iter', return_value=[mock_process1, mock_process2]):
            result = self.handler.get_top_processes(limit=5)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['name'], 'process1')
            self.assertEqual(result[0]['cpu_percent'], 50.0)

    def test_get_process_list(self):
        """Test getting list of all processes."""
        mock_process = Mock()
        mock_process.info = {'name': 'test_process', 'pid': 999, 'status': 'running'}

        with patch('psutil.process_iter', return_value=[mock_process]):
            result = self.handler.get_process_list()
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['name'], 'test_process')


class TestSNMPDataCollector(unittest.TestCase):
    """Test SNMPDataCollector class."""

    def setUp(self):
        """Set up test fixtures."""
        self.collector = handlers.SNMPDataCollector()

    def test_collect_all_data(self):
        """Test collecting all SNMP data."""
        with patch.object(self.collector.system_handler, 'get_all_stats') as mock_system:
            with patch.object(self.collector.process_handler, 'get_process_count') as mock_process_count:
                with patch.object(self.collector.process_handler, 'get_top_processes') as mock_top_processes:
                    mock_system.return_value = {'hostname': 'test-host', 'uptime': 1000}
                    mock_process_count.return_value = 50
                    mock_top_processes.return_value = []

                    result = self.collector.collect_all_data()

                    self.assertIn('system', result)
                    self.assertIn('processes', result)
                    self.assertEqual(result['system']['hostname'], 'test-host')
                    self.assertEqual(result['processes']['count'], 50)


if __name__ == '__main__':
    unittest.main()
