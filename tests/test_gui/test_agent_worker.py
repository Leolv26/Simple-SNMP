"""Unit tests for AgentWorker class."""

import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication
import sys

from snmp_monitor.gui.workers.agent_worker import AgentWorker


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestAgentWorker:
    """Test cases for AgentWorker class."""

    def test_agent_worker_init(self, qapp):
        """Test AgentWorker initialization."""
        worker = AgentWorker()
        assert worker is not None
        assert not worker.is_running()

    def test_agent_worker_has_required_signals(self, qapp):
        """Test AgentWorker has required signals."""
        worker = AgentWorker()
        assert hasattr(worker, 'agent_started')
        assert hasattr(worker, 'agent_stopped')
        assert hasattr(worker, 'agent_error')

    def test_agent_worker_has_required_methods(self, qapp):
        """Test AgentWorker has required methods."""
        worker = AgentWorker()
        assert hasattr(worker, 'is_running')
        assert hasattr(worker, 'start_agent')
        assert hasattr(worker, 'stop_agent')
        assert hasattr(worker, 'run')
        assert callable(worker.is_running)
        assert callable(worker.start_agent)
        assert callable(worker.stop_agent)
        assert callable(worker.run)

    def test_start_agent_updates_state(self, qapp):
        """Test that start_agent updates internal state."""
        worker = AgentWorker()

        # Mock subprocess.Popen to avoid actual process creation
        with patch('snmp_monitor.gui.workers.agent_worker.subprocess.Popen') as mock_popen:
            # Mock the Popen instance
            mock_process = MagicMock()
            mock_popen.return_value = mock_process

            # Call start_agent
            result = worker.start_agent()

            # Verify the agent started
            assert result is True
            assert worker.is_running() is True
            mock_popen.assert_called_once()

    def test_stop_agent_updates_state(self, qapp):
        """Test that stop_agent updates internal state."""
        worker = AgentWorker()

        # Mock subprocess.Popen to avoid actual process creation
        with patch('snmp_monitor.gui.workers.agent_worker.subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_popen.return_value = mock_process

            # Start the agent first
            worker.start_agent()
            assert worker.is_running() is True

            # Stop the agent
            worker.stop_agent()

            # Verify state was updated
            assert worker.is_running() is False

    def test_stop_agent_when_not_running(self, qapp):
        """Test stopping an agent that is not running."""
        worker = AgentWorker()
        # Should not raise an error
        worker.stop_agent()
        assert not worker.is_running()

    def test_start_agent_with_thresholds(self, qapp):
        """Test start_agent with threshold configuration."""
        worker = AgentWorker()

        # Mock subprocess.Popen to avoid actual process creation
        with patch('snmp_monitor.gui.workers.agent_worker.subprocess.Popen') as mock_popen:
            # Mock the Popen instance
            mock_process = MagicMock()
            mock_popen.return_value = mock_process

            # Test starting with thresholds
            thresholds = {'cpu_threshold': 80, 'memory_threshold': 85}
            result = worker.start_agent(thresholds=thresholds)

            # Verify the call was made
            assert mock_popen.called
            assert result is True

    def test_stop_agent_graceful(self, qapp):
        """Test stopping an agent gracefully."""
        worker = AgentWorker()

        # Mock the subprocess and process
        with patch('snmp_monitor.gui.workers.agent_worker.subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_popen.return_value = mock_process

            # Start the agent first
            worker.start_agent()

            # Stop the agent
            worker.stop_agent()

            # Verify terminate was called
            mock_process.terminate.assert_called_once()

    def test_start_agent_uses_sys_executable(self, qapp):
        """Test that start_agent uses sys.executable instead of 'python'."""
        import sys
        worker = AgentWorker()

        with patch('snmp_monitor.gui.workers.agent_worker.subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_popen.return_value = mock_process

            worker.start_agent()

            # Verify sys.executable was used in the command
            call_args = mock_popen.call_args[0][0]
            assert sys.executable in call_args[0], \
                f"Expected sys.executable in command, got {call_args[0]}"
            assert 'python' not in call_args[0] or sys.executable in call_args[0]
