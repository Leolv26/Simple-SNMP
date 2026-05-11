"""Handlers for SNMP data collection using psutil."""
import socket
import time
import psutil
from typing import Dict, List, Any


class SystemInfoHandler:
    """Handles system information collection using psutil."""

    def get_hostname(self) -> str:
        """Get system hostname."""
        return socket.gethostname()

    def get_uptime(self) -> int:
        """Get system uptime in seconds."""
        boot_time = psutil.boot_time()
        current_time = time.time()
        return int(current_time - boot_time)

    def get_cpu_count(self) -> int:
        """Get number of CPU cores."""
        return psutil.cpu_count()

    def get_cpu_percent(self, interval: float = 1.0) -> float:
        """Get CPU usage percentage."""
        return psutil.cpu_percent(interval=interval)

    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory usage information."""
        mem = psutil.virtual_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'percent': mem.percent,
            'used': mem.used,
            'free': mem.free
        }

    def get_disk_info(self, path: str = '/') -> Dict[str, Any]:
        """Get disk usage information for a given path."""
        disk = psutil.disk_usage(path)
        return {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent
        }

    def get_network_io(self) -> Dict[str, Any]:
        """Get network I/O statistics."""
        io = psutil.net_io_counters()
        return {
            'bytes_sent': io.bytes_sent,
            'bytes_recv': io.bytes_recv,
            'packets_sent': io.packets_sent,
            'packets_recv': io.packets_recv
        }

    def get_all_stats(self) -> Dict[str, Any]:
        """Get all system statistics."""
        return {
            'hostname': self.get_hostname(),
            'uptime': self.get_uptime(),
            'cpu_count': self.get_cpu_count(),
            'cpu_percent': self.get_cpu_percent(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_io()
        }


class ProcessInfoHandler:
    """Handles process information collection using psutil."""

    def get_process_count(self) -> int:
        """Get count of running processes."""
        return len(list(psutil.process_iter()))

    def get_top_processes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top N processes by CPU usage."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                proc_info = proc.info
                processes.append({
                    'pid': proc_info['pid'],
                    'name': proc_info['name'],
                    'cpu_percent': proc_info['cpu_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        # Sort by CPU percent in descending order
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        return processes[:limit]

    def get_process_list(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of all processes with basic information."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            try:
                proc_info = proc.info
                processes.append({
                    'pid': proc_info['pid'],
                    'name': proc_info['name'],
                    'status': proc_info['status']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes[:limit]


class SNMPDataCollector:
    """Main class for collecting all SNMP-related data."""

    def __init__(self):
        """Initialize the data collector with handlers."""
        self.system_handler = SystemInfoHandler()
        self.process_handler = ProcessInfoHandler()

    def collect_all_data(self) -> Dict[str, Any]:
        """Collect all system and process data."""
        return {
            'system': self.system_handler.get_all_stats(),
            'processes': {
                'count': self.process_handler.get_process_count(),
                'top': self.process_handler.get_top_processes(limit=10)
            }
        }
