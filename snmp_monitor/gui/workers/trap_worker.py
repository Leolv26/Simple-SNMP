"""SNMP Trap Worker thread for background Trap receiving operations."""
import logging
import socket
from typing import Optional, Dict, Any
from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)


class TrapWorker(QThread):
    """
    SNMP Trap Worker thread for background Trap receiving operations.

    This worker runs in a separate thread and listens for SNMP traps
    on UDP port 162. It emits signals to communicate trap data back
    to the main thread.

    Signals:
        trap_received: Emitted with dict of trap data when a trap is received
        error_occurred: Emitted with error message string when an error occurs

    Example:
        worker = TrapWorker(port=162)
        worker.trap_received.connect(handle_trap)
        worker.start()
        # When done:
        worker.stop()
        worker.wait(2000)
    """

    # Signals for data communication
    trap_received = Signal(dict)  # Emitted when a trap is received
    error_occurred = Signal(str)  # Emitted when an error occurs

    def __init__(
        self,
        port: int = 11162,
        parent=None
    ):
        """
        Initialize Trap Worker.

        Args:
            port: UDP port to listen on for traps (default: 11162)
            parent: Optional parent QObject
        """
        super().__init__(parent)
        self._port = port

        # Control flag for thread loop
        self._running = False

        # Socket for receiving traps
        self._socket: Optional[socket.socket] = None

        logger.info(f"TrapWorker initialized on port {port}")

    def run(self):
        """
        Main receive loop executed in the background thread.

        This method creates a UDP socket, binds to the specified port,
        and listens for incoming SNMP traps until stop() is called.
        """
        logger.info("TrapWorker run loop started")

        # Create UDP socket for receiving traps
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.bind(('0.0.0.0', self._port))
            self._socket.settimeout(1.0)  # 1 second timeout for graceful shutdown
            logger.info(f"TrapWorker listening on port {self._port}")
        except Exception as e:
            logger.error(f"Failed to create trap socket: {e}")
            self.error_occurred.emit(f"Failed to bind to port {self._port}: {str(e)}")
            return

        self._running = True

        while self._running:
            try:
                # Receive trap data
                data, addr = self._socket.recvfrom(1024)
                logger.debug(f"Received {len(data)} bytes from {addr}")

                # Parse trap data
                trap_data = self._parse_trap(data)
                trap_data['source'] = addr[0]
                trap_data['port'] = addr[1]

                # Emit trap received signal
                self.trap_received.emit(trap_data)

            except socket.timeout:
                # Timeout is expected - continue to check _running flag
                continue
            except Exception as e:
                logger.error(f"Error receiving trap: {e}")
                self.error_occurred.emit(f"Trap receive error: {str(e)}")

        logger.info("TrapWorker run loop stopped")

    def _parse_trap(self, data: bytes) -> Dict[str, Any]:
        """
        Parse raw SNMP trap data into a dictionary.

        Args:
            data: Raw trap packet bytes

        Returns:
            Dictionary containing trap information
        """
        try:
            # For now, return basic trap structure with raw data
            # Real implementation would parse ASN.1 BER encoding
            # Using pysnmp-lextudio which has different API than standard pysnmp
            return {
                'type': 'trap',
                'trap_oid': '1.3.6.1.6.3.1.1.5.1',  # Generic trap OID
                'message': 'SNMP Trap received',
                'severity': 'info',
                'raw_data': data.hex() if data else ''
            }
        except Exception as e:
            logger.error(f"Failed to parse trap: {e}")
            # Return safe fallback with raw data
            return {
                'type': 'trap',
                'trap_oid': 'unknown',
                'message': f'Parse error: {str(e)}',
                'severity': 'error',
                'raw_data': data.hex() if data else '',
                'parse_error': str(e)
            }

    def stop(self):
        """
        Stop the trap receiver loop safely.

        This method sets the _running flag to False, which causes
        the receive loop to exit on its next iteration.
        It then waits for the thread to finish.
        """
        logger.info("Stopping TrapWorker")
        self._running = False

        # Close socket if it exists
        if self._socket:
            try:
                self._socket.close()
            except Exception as e:
                logger.error(f"Error closing socket: {e}")
            finally:
                self._socket = None

        # Wait up to 2 seconds for thread to finish
        self.wait(2000)
