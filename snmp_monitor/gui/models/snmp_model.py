"""SNMP Data Model for storing and managing SNMP monitoring data.

This module provides the SNMPModel class which:
- Stores CPU, memory, disk, and network usage data
- Maintains timestamped history of data
- Checks values against configurable thresholds
- Emits signals for data updates and threshold violations
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from PySide6.QtCore import QObject, Signal

from snmp_monitor.core.config import load_config


class SNMPModel(QObject):
    """Model class for SNMP monitoring data.

    Attributes:
        cpu_percent: Current CPU usage percentage.
        memory_percent: Current memory usage percentage.
        disk_percent: Current disk usage percentage.
        bytes_sent: Total bytes sent (counter).
        bytes_recv: Total bytes received (counter).
        cpu_threshold: CPU usage threshold for alerts.
        memory_threshold: Memory usage threshold for alerts.
        disk_threshold: Disk usage threshold for alerts.

    Signals:
        data_updated: Emitted when new data is received.
        threshold_exceeded: Emitted when a metric exceeds its threshold.
    """

    # Signals for data updates
    data_updated = Signal(dict)
    threshold_exceeded = Signal(str, float, float)  # metric_name, current_value, threshold

    # Default thresholds
    DEFAULT_CPU_THRESHOLD = 80.0
    DEFAULT_MEMORY_THRESHOLD = 85.0
    DEFAULT_DISK_THRESHOLD = 90.0

    # Maximum history entries
    MAX_HISTORY_SIZE = 100

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize the SNMPModel.

        Args:
            config_path: Optional path to configuration file.
        """
        super().__init__()
        self._cpu_percent: Optional[float] = None
        self._memory_percent: Optional[float] = None
        self._disk_percent: Optional[float] = None
        self._bytes_sent: Optional[int] = None
        self._bytes_recv: Optional[int] = None
        self._history: List[Dict[str, Any]] = []
        self._timestamp: Optional[datetime] = None

        # Load thresholds from config
        self._cpu_threshold = self.DEFAULT_CPU_THRESHOLD
        self._memory_threshold = self.DEFAULT_MEMORY_THRESHOLD
        self._disk_threshold = self.DEFAULT_DISK_THRESHOLD
        self._load_thresholds(config_path)

    def _load_thresholds(self, config_path: Optional[str] = None) -> None:
        """Load threshold values from configuration.

        Args:
            config_path: Optional path to configuration file.
        """
        try:
            config = load_config(config_path)
            thresholds = config.get('thresholds', {})

            if 'cpu' in thresholds:
                self._cpu_threshold = float(thresholds['cpu'])
            if 'memory' in thresholds:
                self._memory_threshold = float(thresholds['memory'])
            if 'disk' in thresholds:
                self._disk_threshold = float(thresholds['disk'])
        except Exception:
            # Use default thresholds if config loading fails
            pass

    @property
    def cpu_percent(self) -> Optional[float]:
        """Get current CPU usage percentage."""
        return self._cpu_percent

    @cpu_percent.setter
    def cpu_percent(self, value: float) -> None:
        """Set CPU usage percentage."""
        self._cpu_percent = value

    @property
    def memory_percent(self) -> Optional[float]:
        """Get current memory usage percentage."""
        return self._memory_percent

    @memory_percent.setter
    def memory_percent(self, value: float) -> None:
        """Set memory usage percentage."""
        self._memory_percent = value

    @property
    def disk_percent(self) -> Optional[float]:
        """Get current disk usage percentage."""
        return self._disk_percent

    @disk_percent.setter
    def disk_percent(self, value: float) -> None:
        """Set disk usage percentage."""
        self._disk_percent = value

    @property
    def bytes_sent(self) -> Optional[int]:
        """Get total bytes sent."""
        return self._bytes_sent

    @bytes_sent.setter
    def bytes_sent(self, value: int) -> None:
        """Set total bytes sent."""
        self._bytes_sent = value

    @property
    def bytes_recv(self) -> Optional[int]:
        """Get total bytes received."""
        return self._bytes_recv

    @bytes_recv.setter
    def bytes_recv(self, value: int) -> None:
        """Set total bytes received."""
        self._bytes_recv = value

    @property
    def cpu_threshold(self) -> float:
        """Get CPU threshold value."""
        return self._cpu_threshold

    @cpu_threshold.setter
    def cpu_threshold(self, value: float) -> None:
        """Set CPU threshold value."""
        self._cpu_threshold = value

    @property
    def memory_threshold(self) -> float:
        """Get memory threshold value."""
        return self._memory_threshold

    @memory_threshold.setter
    def memory_threshold(self, value: float) -> None:
        """Set memory threshold value."""
        self._memory_threshold = value

    @property
    def disk_threshold(self) -> float:
        """Get disk threshold value."""
        return self._disk_threshold

    @disk_threshold.setter
    def disk_threshold(self, value: float) -> None:
        """Set disk threshold value."""
        self._disk_threshold = value

    def update_data(self, data: Dict[str, Any]) -> None:
        """Update model data with new values.

        Args:
            data: Dictionary containing metric data.
                  Supported keys: cpu_percent, memory_percent, disk_percent,
                                  bytes_sent, bytes_recv
        """
        timestamp = datetime.now()

        # Update individual fields
        if 'cpu_percent' in data:
            self._cpu_percent = float(data['cpu_percent'])
        if 'memory_percent' in data:
            self._memory_percent = float(data['memory_percent'])
        if 'disk_percent' in data:
            self._disk_percent = float(data['disk_percent'])
        if 'bytes_sent' in data:
            self._bytes_sent = int(data['bytes_sent'])
        if 'bytes_recv' in data:
            self._bytes_recv = int(data['bytes_recv'])

        self._timestamp = timestamp

        # Add to history
        self._add_to_history({
            'timestamp': timestamp,
            'cpu_percent': self._cpu_percent,
            'memory_percent': self._memory_percent,
            'disk_percent': self._disk_percent,
            'bytes_sent': self._bytes_sent,
            'bytes_recv': self._bytes_recv
        })

        # Emit signal
        self.data_updated.emit(self.get_current())

    def _add_to_history(self, entry: Dict[str, Any]) -> None:
        """Add an entry to history, maintaining size limit.

        Args:
            entry: History entry to add.
        """
        self._history.append(entry)

        # Trim history if it exceeds maximum size
        if len(self._history) > self.MAX_HISTORY_SIZE:
            self._history = self._history[-self.MAX_HISTORY_SIZE:]

    def get_current(self) -> Optional[Dict[str, Any]]:
        """Get current data values.

        Returns:
            Dictionary containing current data, or None if no data available.
        """
        if self._timestamp is None:
            return None

        return {
            'timestamp': self._timestamp,
            'cpu_percent': self._cpu_percent,
            'memory_percent': self._memory_percent,
            'disk_percent': self._disk_percent,
            'bytes_sent': self._bytes_sent,
            'bytes_recv': self._bytes_recv
        }

    def get_history(self) -> List[Dict[str, Any]]:
        """Get historical data.

        Returns:
            List of historical data entries.
        """
        return self._history.copy()

    def set_thresholds(self, cpu: Optional[float] = None,
                       memory: Optional[float] = None,
                       disk: Optional[float] = None) -> None:
        """Set threshold values.

        Args:
            cpu: CPU threshold percentage.
            memory: Memory threshold percentage.
            disk: Disk threshold percentage.
        """
        if cpu is not None:
            self._cpu_threshold = float(cpu)
        if memory is not None:
            self._memory_threshold = float(memory)
        if disk is not None:
            self._disk_threshold = float(disk)

    def check_thresholds(self) -> List[str]:
        """Check if current values exceed thresholds.

        Returns:
            List of alert messages for exceeded thresholds.
        """
        alerts = []

        # Check CPU threshold
        if self._cpu_percent is not None and self._cpu_percent > self._cpu_threshold:
            alert = f"CPU usage ({self._cpu_percent:.1f}%) exceeds threshold ({self._cpu_threshold:.1f}%)"
            alerts.append(alert)
            self.threshold_exceeded.emit('cpu', self._cpu_percent, self._cpu_threshold)

        # Check memory threshold
        if self._memory_percent is not None and self._memory_percent > self._memory_threshold:
            alert = f"Memory usage ({self._memory_percent:.1f}%) exceeds threshold ({self._memory_threshold:.1f}%)"
            alerts.append(alert)
            self.threshold_exceeded.emit('memory', self._memory_percent, self._memory_threshold)

        # Check disk threshold
        if self._disk_percent is not None and self._disk_percent > self._disk_threshold:
            alert = f"Disk usage ({self._disk_percent:.1f}%) exceeds threshold ({self._disk_threshold:.1f}%)"
            alerts.append(alert)
            self.threshold_exceeded.emit('disk', self._disk_percent, self._disk_threshold)

        return alerts
