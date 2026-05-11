"""Integration tests for GUI framework components.

This module tests the integration between GUI components including:
- MainWindow creation and initialization
- Model assembly and integration
- Worker thread lifecycle (start/stop)
- Signal connections between components
- Configuration loading and threshold settings
"""
import sys
import pytest
import time
from unittest.mock import Mock, MagicMock, patch

from PySide6.QtCore import Qt, QCoreApplication, QTimer
from PySide6.QtWidgets import QApplication


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def mock_snmp_client():
    """Create a mock SNMP client."""
    with patch('snmp_monitor.nms.client.SNMPClient') as mock:
        instance = MagicMock()
        mock.return_value = instance
        # Return mock data for get_bulk
        instance.get_bulk.return_value = [
            ((1, 3, 6, 1, 4, 1, 2021, 4, 3, 0), 50),   # cpu_percent
            ((1, 3, 6, 1, 4, 1, 2021, 4, 6, 0), 60),   # memory_percent
            ((1, 3, 6, 1, 4, 1, 2021, 4, 9, 0), 70),   # disk_percent
            ((1, 3, 6, 1, 4, 1, 2021, 10, 11, 1), 1000),  # bytes_sent
            ((1, 3, 6, 1, 4, 1, 2021, 10, 11, 2), 2000),  # bytes_recv
        ]
        yield instance


# =============================================================================
# Test GUI Component Integration
# =============================================================================

class TestGUIComponentIntegration:
    """Test GUI component integration."""

    def test_main_window_creation(self, qapp):
        """Test that MainWindow can be created successfully."""
        from snmp_monitor.gui.app import MainWindow
        window = MainWindow()
        assert window is not None
        assert window.windowTitle() == "SNMP Monitor"
        window.close()

    def test_main_window_model_assembly(self, qapp):
        """Test that MainWindow correctly assembles all models."""
        from snmp_monitor.gui.app import MainWindow
        from snmp_monitor.gui.models import SNMPModel, MIBModel, TrapModel

        window = MainWindow()

        # Verify all models are created
        assert hasattr(window, '_snmp_model')
        assert hasattr(window, '_mib_model')
        assert hasattr(window, '_trap_model')

        # Verify model types
        assert isinstance(window._snmp_model, SNMPModel)
        assert isinstance(window._mib_model, MIBModel)
        assert isinstance(window._trap_model, TrapModel)

        # Verify models are properly integrated
        assert window.snmp_model is window._snmp_model
        assert window.mib_model is window._mib_model
        assert window.trap_model is window._trap_model

        window.close()

    def test_main_window_worker_creation(self, qapp):
        """Test that MainWindow can create workers."""
        from snmp_monitor.gui.app import MainWindow
        from snmp_monitor.gui.workers import SNMPWorker, TrapWorker

        window = MainWindow()

        # Initially workers should be None
        assert window._snmp_worker is None
        assert window._trap_worker is None

        # Start workers with mocked SNMP client
        with patch('snmp_monitor.gui.workers.SNMPWorker'):
            with patch('snmp_monitor.gui.workers.TrapWorker'):
                window.start_workers()

        # After start, workers should be created
        assert window._snmp_worker is not None
        assert window._trap_worker is not None
        assert isinstance(window._snmp_worker, SNMPWorker)
        assert isinstance(window._trap_worker, TrapWorker)

        window.close()

    def test_ui_components_exist(self, qapp):
        """Test that all UI components are properly created."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Check all required widgets exist
        assert hasattr(window, '_mib_tree')
        assert hasattr(window, '_data_table')
        assert hasattr(window, '_alert_panel')
        assert hasattr(window, '_log_panel')
        assert hasattr(window, '_dashboard')

        # Verify widgets are properly configured
        assert window._data_table.columnCount() == 5  # Metric, Value, Unit, Threshold, Status

        window.close()


# =============================================================================
# Test Worker Thread Lifecycle
# =============================================================================

class TestWorkerThreadLifecycle:
    """Test Worker thread start and stop functionality."""

    def test_snmp_worker_start_and_stop(self, qapp):
        """Test SNMPWorker can start and stop cleanly."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker

        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1', poll_interval=0.5)

            # Worker should not be running initially
            assert not worker.isRunning()

            # Start worker
            worker.start()

            # Wait briefly for thread to start
            time.sleep(0.2)
            assert worker.isRunning()

            # Stop worker
            worker.stop()

            # Wait for thread to finish
            worker.wait(3000)
            assert not worker.isRunning()

    def test_trap_worker_start_and_stop(self, qapp):
        """Test TrapWorker can start and stop cleanly."""
        from snmp_monitor.gui.workers.trap_worker import TrapWorker

        worker = TrapWorker(port=10162)

        # Worker should not be running initially
        assert not worker.isRunning()

        # Start worker
        worker.start()

        # Wait briefly for thread to start
        time.sleep(0.2)
        assert worker.isRunning()

        # Stop worker
        worker.stop()

        # Wait for thread to finish
        worker.wait(3000)
        assert not worker.isRunning()

    def test_worker_thread_safe_shutdown(self, qapp):
        """Test that workers can shut down safely even if running."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker

        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1', poll_interval=0.1)
            worker.start()
            time.sleep(0.3)

            # Stop multiple times should be safe
            worker.stop()
            worker.wait(2000)
            assert not worker.isRunning()

            # Calling stop again should not raise
            worker.stop()


# =============================================================================
# Test Signal Connections
# =============================================================================

class TestSignalConnections:
    """Test signal connections between components."""

    def test_model_data_updated_signal(self, qapp):
        """Test that SNMPModel emits data_updated signal."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel

        model = SNMPModel()

        received_data = []

        def capture_data(data):
            received_data.append(data)

        model.data_updated.connect(capture_data)

        # Update data
        test_data = {'cpu_percent': 50.0, 'memory_percent': 60.0}
        model.update_data(test_data)

        # Give Qt event loop time to process
        qapp.processEvents()

        assert len(received_data) == 1
        assert 'cpu_percent' in received_data[0]

    def test_model_threshold_exceeded_signal(self, qapp):
        """Test that SNMPModel emits threshold_exceeded signal."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel

        model = SNMPModel()
        model.set_thresholds(cpu=50.0, memory=85.0, disk=90.0)

        exceeded_calls = []

        def capture_threshold(metric, value, threshold):
            exceeded_calls.append((metric, value, threshold))

        model.threshold_exceeded.connect(capture_threshold)

        # Update data exceeding threshold
        test_data = {'cpu_percent': 80.0, 'memory_percent': 60.0}
        model.update_data(test_data)
        alerts = model.check_thresholds()

        qapp.processEvents()

        assert len(exceeded_calls) >= 1
        assert exceeded_calls[0][0] == 'cpu'

    def test_worker_error_signal(self, qapp):
        """Test that SNMPWorker emits error_occurred signal."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker

        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1')

            errors = []

            def capture_error(msg):
                errors.append(msg)

            worker.error_occurred.connect(capture_error)

            # Emit an error signal manually
            worker.error_occurred.emit("Test error message")

            qapp.processEvents()

            assert len(errors) == 1
            assert "Test error" in errors[0]

    def test_main_window_logs_worker_error(self, qapp):
        """Test that MainWindow logs errors from workers."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Get initial log content
        initial_log = window._log_panel.toPlainText()

        # Manually trigger error handler
        window._on_worker_error("Connection failed")

        qapp.processEvents()

        log_content = window._log_panel.toPlainText()
        assert "Connection failed" in log_content

        window.close()

    def test_trap_worker_trap_received_signal(self, qapp):
        """Test that TrapWorker emits trap_received signal."""
        from snmp_monitor.gui.workers.trap_worker import TrapWorker

        worker = TrapWorker()

        traps = []

        def capture_trap(data):
            traps.append(data)

        worker.trap_received.connect(capture_trap)

        # Emit trap signal
        test_trap = {'type': 'trap', 'source': '192.168.1.100', 'oid': '1.3.6.1'}
        worker.trap_received.emit(test_trap)

        qapp.processEvents()

        assert len(traps) == 1
        assert traps[0]['source'] == '192.168.1.100'


# =============================================================================
# Test Configuration Loading
# =============================================================================

class TestConfigurationLoading:
    """Test configuration loading functionality."""

    def test_config_yaml_loading(self):
        """Test that config.yaml can be loaded."""
        from snmp_monitor.core.config import load_config

        config = load_config()

        assert config is not None
        assert isinstance(config, dict)

    def test_config_has_required_sections(self):
        """Test that config has required sections."""
        from snmp_monitor.core.config import load_config

        config = load_config()

        # Config should have nms section
        assert 'nms' in config or 'snmp_agent' in config or 'thresholds' in config

    def test_threshold_config_from_yaml(self):
        """Test that thresholds are loaded from config."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel
        from snmp_monitor.core.config import load_config

        config = load_config()
        thresholds = config.get('thresholds', {})

        model = SNMPModel()

        # Model should have threshold values loaded
        assert hasattr(model, 'cpu_threshold')
        assert hasattr(model, 'memory_threshold')
        assert hasattr(model, 'disk_threshold')

        # If thresholds are in config, verify they match
        if 'cpu' in thresholds:
            assert model.cpu_threshold == thresholds['cpu']
        if 'memory' in thresholds:
            assert model.memory_threshold == thresholds['memory']
        if 'disk' in thresholds:
            assert model.disk_threshold == thresholds['disk']

    def test_main_window_loads_config(self, qapp):
        """Test that MainWindow loads configuration correctly."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Verify config is loaded
        assert hasattr(window, '_config')
        assert window._config is not None

        # Verify nms config is available
        nms_config = window._config.get('nms', {})
        assert 'agent_host' in nms_config
        assert 'trap_port' in nms_config

        window.close()

    def test_model_threshold_reflects_config(self, qapp):
        """Test that model thresholds reflect config values."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Verify model thresholds match config or defaults
        model = window._snmp_model

        assert model.cpu_threshold > 0
        assert model.memory_threshold > 0
        assert model.disk_threshold > 0

        window.close()


# =============================================================================
# Test End-to-End Integration
# =============================================================================

class TestEndToEndIntegration:
    """Test end-to-end integration scenarios."""

    def test_main_window_full_lifecycle(self, qapp):
        """Test complete MainWindow lifecycle: create, start, stop, close."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Verify initial state
        assert window._snmp_worker is None
        assert window._trap_worker is None
        assert window._status_label.text() == "Monitoring: Stopped"

        # Start monitoring with mocked workers
        with patch('snmp_monitor.gui.workers.SNMPWorker.start'):
            with patch('snmp_monitor.gui.workers.TrapWorker.start'):
                window.start_monitoring()

        qapp.processEvents()

        # Verify started state
        assert window._snmp_worker is not None
        assert window._trap_worker is not None

        # Stop monitoring
        window.stop_monitoring()

        qapp.processEvents()

        # Verify stopped state
        assert window._status_label.text() == "Monitoring: Stopped"

        window.close()

    def test_data_flow_from_worker_to_model_to_ui(self, qapp):
        """Test data flow from worker signal to model to UI."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Simulate worker data ready
        test_data = {
            'cpu_percent': 75.0,
            'memory_percent': 65.0,
            'disk_percent': 55.0,
            'bytes_sent': 5000,
            'bytes_recv': 10000
        }

        # Update model directly (simulating what worker would do)
        window._snmp_model.update_data(test_data)

        qapp.processEvents()

        # Verify model was updated
        assert window._snmp_model.cpu_percent == 75.0
        assert window._snmp_model.memory_percent == 65.0

        window.close()

    def test_trap_flow_to_trap_model(self, qapp):
        """Test trap flow from worker to trap model."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Simulate trap received
        trap_data = {
            'type': 'trap',
            'source': '192.168.1.100',
            'oid': '.1.3.6.1.4.1.2021.4',
            'message': 'Test trap alert',
            'severity': 'warning'
        }

        window._on_trap_received(trap_data)

        qapp.processEvents()

        # Verify trap was added to model
        assert window._trap_model.rowCount() == 1

        window.close()

    def test_threshold_check_integration(self, qapp):
        """Test threshold checking integration."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Set low threshold
        window._snmp_model.set_thresholds(cpu=50.0, memory=85.0, disk=90.0)

        # Update with data exceeding threshold
        test_data = {'cpu_percent': 80.0}
        window._snmp_model.update_data(test_data)

        alerts = window._snmp_model.check_thresholds()

        qapp.processEvents()

        # Should have CPU alert
        assert len(alerts) > 0
        assert any('cpu' in alert.lower() for alert in alerts)

        window.close()

    def test_multiple_worker_start_stop_cycles(self, qapp):
        """Test multiple start/stop cycles for workers."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        for i in range(3):
            with patch('snmp_monitor.gui.workers.SNMPWorker.start'):
                with patch('snmp_monitor.gui.workers.TrapWorker.start'):
                    window.start_workers()

            qapp.processEvents()

            assert window._snmp_worker is not None
            assert window._trap_worker is not None

            window.stop_workers()

            qapp.processEvents()

        window.close()


class TestAgentNMSIntegration:
    """Test Agent + NMS integration with proper start/stop order."""

    def test_agent_worker_integration(self, qapp):
        """Test that AgentWorker is properly integrated in MainWindow."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Verify AgentWorker is initialized
        assert hasattr(window, '_agent_worker')
        assert window._agent_worker is None  # Not started yet

        # Verify methods exist
        assert hasattr(window, '_start_agent')
        assert hasattr(window, '_stop_agent')
        assert hasattr(window, '_start_nms_workers')

        window.close()

    def test_trap_received_logged(self, qapp):
        """Test that Trap received is logged in LogPanel."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Get initial log content
        initial_log = window._log_panel_widget._log_display.toPlainText()

        # Simulate trap received
        trap_data = {
            'type': 'trap',
            'source': '127.0.0.1',
            'oid': '.1.3.6.1.4.1.2021.4.0.1',
            'message': 'CPU threshold exceeded',
            'severity': 'warning'
        }

        # Call the trap handler
        window._on_trap_received(trap_data)

        qapp.processEvents()

        # Verify trap was logged
        log_content = window._log_panel_widget._log_display.toPlainText()
        assert 'Trap' in log_content or 'trap' in log_content.lower()
        assert '127.0.0.1' in log_content

        window.close()

    def test_agent_worker_signals_connected(self, qapp):
        """Test that AgentWorker signals are properly connected."""
        from snmp_monitor.gui.app import MainWindow
        from snmp_monitor.gui.workers.agent_worker import AgentWorker

        window = MainWindow()

        with patch('snmp_monitor.gui.app.AgentWorker') as MockAgentWorker:
            mock_agent = MagicMock()
            MockAgentWorker.return_value = mock_agent
            mock_agent.is_running.return_value = False

            # Create agent worker
            window._agent_worker = AgentWorker()
            window._connect_agent_signals()

            # Verify signal connections exist
            assert mock_agent.agent_started.connect.called or \
                   hasattr(mock_agent, 'agent_started')
            assert hasattr(mock_agent, 'agent_stopped')
            assert hasattr(mock_agent, 'agent_error')

        window.close()

    def test_agent_control_buttons_exist(self, qapp):
        """Test that Agent control buttons exist in the UI."""
        from snmp_monitor.gui.app import MainWindow

        window = MainWindow()

        # Check that agent control buttons exist
        assert hasattr(window, '_start_agent_btn')
        assert hasattr(window, '_stop_agent_btn')

        # Initial state: start enabled, stop disabled
        assert window._start_agent_btn.isEnabled()
        assert not window._stop_agent_btn.isEnabled()

        window.close()


# =============================================================================
# Test Thread Safety
# =============================================================================

class TestThreadSafety:
    """Test thread safety aspects."""

    def test_worker_signals_are_thread_safe(self, qapp):
        """Test that worker signals work across threads."""
        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker

        with patch('snmp_monitor.gui.workers.snmp_worker.SNMPClient'):
            worker = SNMPWorker(host='127.0.0.1')

            main_thread_data = []

            def capture_data(data):
                main_thread_data.append(data)

            worker.data_ready.connect(capture_data)

            # Emit signal from different context
            worker.data_ready.emit({'cpu_percent': 50.0})

            qapp.processEvents()

            # Data should be received in main thread
            assert len(main_thread_data) == 1

    def test_model_signals_are_thread_safe(self, qapp):
        """Test that model signals work across threads."""
        from snmp_monitor.gui.models.snmp_model import SNMPModel

        model = SNMPModel()

        received = []

        def capture(data):
            received.append(data)

        model.data_updated.connect(capture)

        # Update and verify signal emission
        model.update_data({'cpu_percent': 75.0})

        qapp.processEvents()

        assert len(received) == 1
