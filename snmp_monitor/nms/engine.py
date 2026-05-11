"""NMS polling engine for SNMP monitoring."""
import threading
import time
import logging
from typing import Dict, Tuple, Any
from PySide6.QtCore import QObject, Signal

from snmp_monitor.nms.client import SNMPClient
from snmp_monitor.nms.oids import SNMP_VERSION_2C

logger = logging.getLogger(__name__)


class NMSEngine(QObject):
    """NMS polling engine for SNMP monitoring."""

    data_ready = Signal(object)
    trap_received = Signal(object)
    error_occurred = Signal(str)

    def __init__(self, config_file: str = "config.yaml"):
        """
        Initialize NMS engine.

        Args:
            config_file: Path to configuration file
        """
        super().__init__()
        self._running = False
        self._thread: threading.Thread = None
        self._poll_interval = 2.0  # Default polling interval in seconds

        # Initialize SNMP client with defaults
        self.client = SNMPClient(
            host='127.0.0.1',
            community='public',
            version=SNMP_VERSION_2C,
            timeout=5,
            retries=2
        )

        logger.info(f"NMSEngine initialized with config file: {config_file}")

    def start(self):
        """Start the polling engine."""
        logger.info("Starting NMSEngine")
        self._running = True

        # Start polling thread
        self._thread = threading.Thread(target=self._polling_loop, daemon=True)
        self._thread.start()

        logger.info("NMSEngine started")

    def stop(self):
        """Stop the polling engine."""
        logger.info("Stopping NMSEngine")
        self._running = False

        logger.info("NMSEngine stopped")

    def wait(self, timeout: float = None) -> bool:
        """
        Wait for the polling thread to finish.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if thread finished within timeout, False otherwise
        """
        if self._thread:
            self._thread.join(timeout=timeout)
            return not self._thread.is_alive()
        return True

    def poll_once(self) -> Dict[Tuple[int, ...], Any]:
        """
        Execute a single poll of metrics from the SNMP agent.

        Returns:
            Dictionary mapping OID tuples to values
        """
        logger.debug("Executing single poll")

        try:
            # Get all metrics via GETBULK operation
            # Query the UCD-SNMP memory/load monitoring base OID
            results = self.client.get_bulk(oid=(1, 3, 6, 1, 4, 1, 2021, 4))

            # Convert list of tuples to dict
            data = {oid: value for oid, value in results}

            # Emit signal with the data
            self.data_ready.emit(data)

            logger.debug(f"Poll completed with {len(data)} metrics")
            return data

        except Exception as e:
            logger.error(f"Error during poll: {e}")
            self.error_occurred.emit(str(e))
            return {}

    def _polling_loop(self):
        """Main polling loop running in background thread."""
        logger.info("Starting polling thread loop")
        while self._running:
            try:
                self.poll_once()
                time.sleep(self._poll_interval)
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                if not self._running:
                    break
                time.sleep(0.1)  # Brief pause on error

    def _on_trap_received(self, trap_data: Dict[str, Any]):
        """
        Trap received callback.

        Args:
            trap_data: Dictionary containing trap information
        """
        logger.debug(f"Trap received: {trap_data}")
        self.trap_received.emit(trap_data)

    def set_poll_interval(self, interval: float):
        """
        Set the polling interval.

        Args:
            interval: Polling interval in seconds
        """
        if interval <= 0:
            logger.error("Poll interval must be positive")
            return
        self._poll_interval = interval
        logger.info(f"Poll interval set to {interval} seconds")
