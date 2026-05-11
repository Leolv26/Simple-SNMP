"""AgentWorker class for Agent lifecycle management."""

import logging
import os
import subprocess
import sys
import time
from PySide6.QtCore import QThread, Signal

from snmp_monitor.core.config import find_config_file, load_config
from snmp_monitor.nms.client import SNMPClient

logger = logging.getLogger(__name__)


class AgentWorker(QThread):
    """
    Worker thread for Agent lifecycle management.

    Signals:
        agent_started: Emitted when the agent starts
        agent_stopped: Emitted when the agent stops
        agent_error: Emitted when an error occurs
    """

    STARTUP_TIMEOUT_SECONDS = 5.0
    STARTUP_POLL_INTERVAL_SECONDS = 0.2
    GUI_BULK_BASE_OID = (1, 3, 6, 1, 4, 1, 2021, 4)

    # Define signals for agent lifecycle events
    agent_started = Signal()
    agent_stopped = Signal()
    agent_error = Signal(str)

    def __init__(self, parent=None):
        """Initialize the AgentWorker."""
        super().__init__(parent)
        self._is_running = False
        self._process = None
        self._log_file = None

    def is_running(self):
        """Check if the agent is currently running.

        Returns:
            bool: True if running, False otherwise
        """
        return self._is_running

    def start_agent(self, thresholds=None):
        """Start the agent server.

        Args:
            thresholds: Dictionary of threshold configurations (e.g., {'cpu_threshold': 80})

        Returns:
            bool: True if successfully started, False otherwise
        """
        try:
            logger.info("Starting Agent subprocess: python -m snmp_monitor.agent")

            # Prepare environment with thresholds
            env = os.environ.copy()
            if thresholds:
                for key, value in thresholds.items():
                    env[f'AGENT_{key.upper()}'] = str(value)
                    logger.info(f"  Setting threshold: {key}={value}")

            config_file = find_config_file()
            agent_cwd = str(config_file.parent) if config_file else None
            log_path = config_file.parent / 'agent_subprocess.log' if config_file else None

            logger.info(f"Agent config file: {config_file if config_file else '<not found>'}")
            logger.info(f"Agent subprocess cwd: {agent_cwd if agent_cwd else os.getcwd()}")
            if log_path:
                logger.info(f"Agent subprocess log: {log_path}")
                self._log_file = open(log_path, 'a', encoding='utf-8')
                stdout_target = self._log_file
                stderr_target = subprocess.STDOUT
            else:
                stdout_target = subprocess.DEVNULL
                stderr_target = subprocess.DEVNULL

            # Start the agent server as a subprocess
            # Use sys.executable to ensure correct Python path in all environments
            self._process = subprocess.Popen(
                [sys.executable, '-m', 'snmp_monitor.agent'],
                cwd=agent_cwd,
                env=env,
                stdout=stdout_target,
                stderr=stderr_target
            )

            logger.info(f"Agent subprocess started with PID: {self._process.pid}")

            if hasattr(self._process, 'wait'):
                try:
                    return_code = self._process.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    return_code = None

                if return_code is not None:
                    error_message = f"Agent process exited during startup with code {return_code}"
                    logger.error(error_message)
                    self._close_log_file()
                    self._is_running = False
                    self.agent_error.emit(error_message)
                    return False

                if not self._wait_until_snmp_ready():
                    error_message = "Agent process started but SNMP GETBULK did not become ready"
                    logger.error(error_message)
                    self._terminate_process()
                    self._is_running = False
                    self.agent_error.emit(error_message)
                    return False

            # Update state and emit signal only after SNMP polling is ready.
            self._is_running = True
            self.agent_started.emit()
            return True
        except Exception as e:
            logger.error(f"Failed to start agent: {type(e).__name__}: {str(e)}", exc_info=True)
            self.agent_error.emit(f"Failed to start agent: {str(e)}")
            return False

    def _get_snmp_connection(self):
        config = load_config()
        snmp_agent = config.get('snmp_agent', {})
        nms = config.get('nms', {})

        host = nms.get('agent_host', '127.0.0.1')
        port = nms.get('agent_port', snmp_agent.get('port', 1161))
        community = snmp_agent.get('community', 'public')
        return host, port, community

    def _wait_until_snmp_ready(self) -> bool:
        host, port, community = self._get_snmp_connection()
        deadline = time.monotonic() + self.STARTUP_TIMEOUT_SECONDS
        last_error = None

        logger.info(f"Waiting for Agent SNMP GETBULK readiness at {host}:{port}")

        while time.monotonic() < deadline:
            if self._process and hasattr(self._process, 'poll') and self._process.poll() is not None:
                logger.error(f"Agent process exited before SNMP became ready, code={self._process.poll()}")
                return False

            try:
                client = SNMPClient(host, port=port, community=community, timeout=0.5, retries=0)
                results = client.get_bulk(self.GUI_BULK_BASE_OID, max_repetitions=10)
                data = {oid: value for oid, value in results}
                if (1, 3, 6, 1, 4, 1, 2021, 4, 3, 0) in data and (1, 3, 6, 1, 4, 1, 2021, 4, 6, 0) in data:
                    logger.info(f"Agent SNMP GETBULK ready at {host}:{port}")
                    return True
            except Exception as exc:
                last_error = exc
                logger.debug(f"Agent SNMP readiness check failed: {type(exc).__name__}: {exc}")

            time.sleep(self.STARTUP_POLL_INTERVAL_SECONDS)

        logger.error(
            f"Agent SNMP GETBULK readiness timed out at {host}:{port}; "
            f"last_error={type(last_error).__name__ if last_error else None}: {last_error}"
        )
        return False

    def _terminate_process(self):
        try:
            if not self._process or self._process.poll() is not None:
                return

            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()
        finally:
            self._close_log_file()

    def _close_log_file(self):
        if self._log_file:
            self._log_file.close()
            self._log_file = None

    def stop_agent(self):
        """Stop the agent gracefully.

        First attempts graceful termination, then force kills if needed.
        """
        if not self._is_running:
            return

        try:
            self._terminate_process()
            self._is_running = False
            self.agent_stopped.emit()
        except Exception as e:
            self.agent_error.emit(f"Failed to stop agent: {str(e)}")

    def run(self):
        """Main worker thread execution loop.

        Note: This thread manages the Agent subprocess lifecycle.
        The actual Agent startup is handled by start_agent() method.
        """
        try:
            # Main loop - wait for agent to be stopped
            while self._is_running:
                self.msleep(100)
        except Exception as e:
            self.agent_error.emit(str(e))
        finally:
            self._is_running = False
            self.agent_stopped.emit()
