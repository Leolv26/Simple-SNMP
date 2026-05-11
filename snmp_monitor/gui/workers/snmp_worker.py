"""SNMP Worker thread for background SNMP polling operations."""
import logging
from typing import Optional, Tuple, Dict, Any
from PySide6.QtCore import QThread, Signal

from snmp_monitor.nms.client import SNMPClient
from snmp_monitor.nms import oids as nms_oids

logger = logging.getLogger(__name__)


class SNMPWorker(QThread):
    """
    SNMP Worker thread for background SNMP polling operations.

    This worker runs in a separate thread and periodically polls
    the SNMP agent for metrics. It emits signals to communicate
    data back to the main thread.

    Signals:
        data_ready: Emitted with dict of OID -> value when data is received
        error_occurred: Emitted with error message string when an error occurs
        oid_query_result: Emitted with (oid, value) tuple when single OID query completes

    Example:
        worker = SNMPWorker(host='127.0.0.1', poll_interval=2.0)
        worker.data_ready.connect(handle_data)
        worker.start()
        # When done:
        worker.stop()
        worker.wait(2000)
    """

    # Signals for data communication
    data_ready = Signal(object)        # Emitted when polling data is ready
    error_occurred = Signal(str)       # Emitted when an error occurs
    oid_query_result = Signal(str, object)  # Emitted when single OID query completes

    def __init__(
        self,
        host: str = '127.0.0.1',
        port: int = 1161,
        community: str = 'public',
        poll_interval: float = 2.0,
        timeout: int = 5,
        retries: int = 2,
        parent=None
    ):
        """
        Initialize SNMP Worker.

        Args:
            host: Target SNMP agent host IP or hostname
            port: Target SNMP port (default: 1161, must match agent port)
            community: SNMP community string
            poll_interval: Polling interval in seconds (default: 2.0)
            timeout: SNMP operation timeout in seconds
            retries: Number of retries for failed operations
            parent: Optional parent QObject
        """
        super().__init__(parent)
        self.host = host
        self.port = port
        self.community = community
        self._poll_interval = poll_interval
        self.timeout = timeout
        self.retries = retries

        # Control flag for thread loop
        self._running = False

        # Initialize SNMP client
        self.client = SNMPClient(
            host=host,
            port=port,
            community=community,
            version=nms_oids.SNMP_VERSION_2C,
            timeout=timeout,
            retries=retries
        )

        logger.info(f"SNMPWorker initialized for host {host}:{port}, poll_interval={poll_interval}s")

    def run(self):
        """
        Main polling loop executed in the background thread.

        This method runs the polling loop until stop() is called.
        It polls the SNMP agent at regular intervals and emits
        data_ready signals with the results.
        """
        logger.info("SNMPWorker polling loop started")
        self._running = True

        while self._running:
            try:
                # Execute polling operation
                data = self._poll()
                if data:
                    self.data_ready.emit(data)
            except Exception as e:
                logger.error(f"Error in SNMP polling loop: {e}")
                self.error_occurred.emit(str(e))

            # Sleep for poll interval (check _running flag periodically)
            self._sleep_interval()

        logger.info("SNMPWorker polling loop stopped")

    def _poll(self) -> Dict[Tuple[int, ...], Any]:
        """
        Execute a single polling operation.

        Returns:
            Dictionary mapping OID tuples to values
        """
        try:
            # Query the UCD-SNMP memory/load monitoring base OID
            logger.info(f"Starting GETBULK poll: oid=(1, 3, 6, 1, 4, 1, 2021, 4), host={self.host}")
            results = self.client.get_bulk(oid=(1, 3, 6, 1, 4, 1, 2021, 4))

            logger.info(f"GETBULK poll completed: {len(results)} results received")

            # Convert list of tuples to dict
            data = {oid: value for oid, value in results}

            logger.debug(f"Poll completed with {len(data)} metrics")
            return data

        except Exception as e:
            logger.error(f"Poll operation failed: {type(e).__name__}: {str(e)}", exc_info=True)
            raise

    def _sleep_interval(self):
        """
        Sleep for the poll interval, checking _running flag periodically.

        This allows for responsive shutdown without long blocking periods.
        """
        elapsed = 0.0
        sleep_step = 0.1  # Check every 100ms

        while elapsed < self._poll_interval and self._running:
            self.msleep(int(sleep_step * 1000))
            elapsed += sleep_step

    def query_oid(self, oid: str):
        """
        Query a single OID value.

        This method performs a single SNMP GET operation for the
        specified OID. The result is emitted via oid_query_result signal.

        Args:
            oid: OID string (e.g., '.1.3.6.1.2.1.1.1.0')
        """
        try:
            # Convert string OID to tuple if needed
            if isinstance(oid, str):
                # Handle OID format: .1.3.6.1... or 1.3.6.1...
                oid_clean = oid.strip()
                if oid_clean.startswith('.'):
                    oid_clean = oid_clean[1:]
                oid_tuple = tuple(int(x) for x in oid_clean.split('.'))
            else:
                oid_tuple = oid

            # Execute GET operation
            result = self.client.get(oid_tuple)

            # Emit result signal
            self.oid_query_result.emit(oid, result)
            logger.debug(f"OID query completed: {oid} -> {result}")

        except Exception as e:
            logger.error(f"OID query failed for {oid}: {e}")
            self.oid_query_result.emit(oid, None)
            self.error_occurred.emit(f"OID query failed: {str(e)}")

    def set_poll_interval(self, interval: float):
        """
        Set the polling interval.

        Args:
            interval: Polling interval in seconds (must be positive)
        """
        if interval <= 0:
            logger.error("Poll interval must be positive")
            return

        self._poll_interval = interval
        logger.info(f"Poll interval set to {interval} seconds")

    def stop(self):
        """
        Stop the polling loop safely.

        This method sets the _running flag to False, which causes
        the polling loop to exit on its next iteration.
        It then waits for the thread to finish.
        """
        logger.info("Stopping SNMPWorker")
        self._running = False
        self.wait(2000)  # Wait up to 2 seconds for thread to finish
