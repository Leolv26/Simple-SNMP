"""Main Window for SNMP Monitor GUI Application.

This module provides the MainWindow class which:
- Inherits from QMainWindow for PySide6 main window
- Integrates all View components (DashboardWidget, DeviceTreeWidget, DataTableWidget, LogPanelWidget)
- Integrates AlertConfigDialog for threshold configuration
- Manages SNMPWorker and TrapWorker threads
- Connects worker signals to View components
- Provides UI layout with QGridLayout
- Handles worker lifecycle and cleanup on close
"""
import logging
from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGroupBox, QMenuBar, QMenu,
    QSplitter
)
from PySide6.QtGui import QAction

from snmp_monitor.gui.models import SNMPModel, MIBModel, TrapModel
from snmp_monitor.gui.workers import SNMPWorker, TrapWorker, AgentWorker
from snmp_monitor.gui.views import (
    DashboardWidget,
    DeviceTreeWidget,
    DataTableWidget,
    LogPanelWidget,
    AlertConfigDialog
)
from snmp_monitor.core.config import load_config

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main window for SNMP Monitor GUI application.

    This class orchestrates the GUI by:
    - Creating and managing data models (SNMPModel, MIBModel, TrapModel)
    - Creating and managing worker threads (SNMPWorker, TrapWorker)
    - Integrating all View components
    - Connecting signals between workers and View components
    - Providing UI layout with various panels using QGridLayout

    Signals:
        none (uses Qt signals from models and workers)

    Attributes:
        _snmp_model: SNMP data model instance
        _mib_model: MIB tree model instance
        _trap_model: Trap history model instance
        _snmp_worker: SNMP polling worker thread
        _trap_worker: Trap receiving worker thread
        _dashboard_widget: DashboardWidget for CPU/memory charts
        _device_tree_widget: DeviceTreeWidget for MIB tree display
        _data_table_widget: DataTableWidget for data display
        _log_panel_widget: LogPanelWidget for log messages
        _control_panel: Control panel widget with buttons
    """

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize the MainWindow.

        Args:
            config_path: Optional path to configuration file.
        """
        super().__init__()

        # Load configuration
        self._config = load_config(config_path)

        # Initialize models
        self._snmp_model = SNMPModel(config_path)
        self._mib_model = MIBModel()
        self._trap_model = TrapModel()

        # Initialize workers (not started yet)
        self._snmp_worker: Optional[SNMPWorker] = None
        self._trap_worker: Optional[TrapWorker] = None
        self._agent_worker: Optional[AgentWorker] = None

        # Setup UI
        self._setup_ui()

        # Create menu bar
        self._create_menu_bar()

        # Create status bar
        self.statusBar().showMessage("Ready")

        # Initial log message
        self._log_panel_widget.append_info("SNMP Monitor initialized")

    def _setup_ui(self) -> None:
        """Setup the user interface components with QGridLayout."""
        # Set window properties
        self.setWindowTitle("SNMP Monitor")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QGridLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Create all View components
        # 1. Device Tree Widget (top-left)
        self._device_tree_widget = DeviceTreeWidget(self._mib_model)
        main_layout.addWidget(self._device_tree_widget, 0, 0)

        # 2. Data Table Widget (top-middle)
        self._data_table_widget = DataTableWidget()
        main_layout.addWidget(self._data_table_widget, 0, 1)

        # 3. Control Panel (top-right)
        self._control_panel = self._create_control_panel()
        main_layout.addWidget(self._control_panel, 0, 2)

        # 4. Dashboard Widget (middle, spanning all columns)
        self._dashboard_widget = DashboardWidget()
        main_layout.addWidget(self._dashboard_widget, 1, 0, 1, 3)

        # 5. Log Panel Widget (bottom, spanning all columns)
        self._log_panel_widget = LogPanelWidget()
        main_layout.addWidget(self._log_panel_widget, 2, 0, 1, 3)

        # Set row stretches
        main_layout.setRowStretch(0, 2)  # Top section
        main_layout.setRowStretch(1, 1)  # Dashboard
        main_layout.setRowStretch(2, 1)  # Log panel

        # Connect View signals
        self._connect_view_signals()

    def _create_control_panel(self) -> QWidget:
        """Create the monitoring control panel widget.

        Returns:
            QWidget containing the control panel.
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title = QLabel("Monitoring Control")
        title.setStyleSheet("font-weight: bold; font-size: 14px; font-family: Arial, Helvetica, sans-serif;")
        layout.addWidget(title)

        # Agent Control Section
        agent_group = QGroupBox("Agent")
        agent_layout = QVBoxLayout(agent_group)

        self._agent_status_label = QLabel("Agent Status: Stopped")
        agent_layout.addWidget(self._agent_status_label)

        agent_btn_layout = QHBoxLayout()
        self._start_agent_btn = QPushButton("Start Agent")
        self._stop_agent_btn = QPushButton("Stop Agent")
        self._stop_agent_btn.setEnabled(False)
        self._start_agent_btn.clicked.connect(self._on_start_agent_clicked)
        self._stop_agent_btn.clicked.connect(self._on_stop_agent_clicked)
        agent_btn_layout.addWidget(self._start_agent_btn)
        agent_btn_layout.addWidget(self._stop_agent_btn)
        agent_layout.addLayout(agent_btn_layout)

        layout.addWidget(agent_group)

        # NMS Control Section
        nms_group = QGroupBox("NMS")
        nms_layout = QVBoxLayout(nms_group)

        self._status_label = QLabel("NMS Status: Stopped")
        nms_layout.addWidget(self._status_label)

        nms_btn_layout = QHBoxLayout()
        self._start_btn = QPushButton("Start NMS")
        self._stop_btn = QPushButton("Stop NMS")
        self._stop_btn.setEnabled(False)
        self._start_btn.clicked.connect(self.start_monitoring)
        self._stop_btn.clicked.connect(self.stop_monitoring)
        nms_btn_layout.addWidget(self._start_btn)
        nms_btn_layout.addWidget(self._stop_btn)
        nms_layout.addLayout(nms_btn_layout)

        layout.addWidget(nms_group)

        layout.addStretch()

        return panel

    def _connect_view_signals(self) -> None:
        """Connect signals between View components."""
        # Connect DeviceTreeWidget oid_selected to DataTableWidget search
        self._device_tree_widget.oid_selected.connect(self._on_oid_selected)

        # Connect DataTableWidget oid_query_requested to query_oid
        self._data_table_widget.oid_query_requested.connect(self._on_oid_query_requested)

        # Connect SNMP model signals
        self._snmp_model.data_updated.connect(self._on_snmp_data_updated)
        self._snmp_model.threshold_exceeded.connect(self._on_threshold_exceeded)

        # Connect LogPanelWidget clear
        self._log_panel_widget.clear_requested.connect(self._on_log_clear_requested)

    def _create_menu_bar(self) -> None:
        """Create the menu bar with File, Monitoring, and Help menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Monitoring menu
        monitoring_menu = menubar.addMenu("&Monitoring")

        start_action = QAction("&Start Monitoring", self)
        start_action.setShortcut("Ctrl+S")
        start_action.triggered.connect(self.start_monitoring)
        monitoring_menu.addAction(start_action)

        stop_action = QAction("&Stop Monitoring", self)
        stop_action.setShortcut("Ctrl+T")
        stop_action.triggered.connect(self.stop_monitoring)
        monitoring_menu.addAction(stop_action)

        monitoring_menu.addSeparator()

        threshold_action = QAction("&Threshold Configuration", self)
        threshold_action.triggered.connect(self._open_threshold_config)
        monitoring_menu.addAction(threshold_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _open_threshold_config(self) -> None:
        """Open the threshold configuration dialog."""
        dialog = AlertConfigDialog(self)
        dialog.set_thresholds(
            cpu=self._snmp_model.cpu_threshold,
            memory=self._snmp_model.memory_threshold,
            disk=self._snmp_model.disk_threshold
        )
        dialog.thresholds_changed.connect(self._on_thresholds_changed)
        dialog.exec()

    def _on_thresholds_changed(self, thresholds: dict) -> None:
        """Handle threshold configuration changes.

        Args:
            thresholds: Dictionary with 'cpu', 'memory', 'disk' threshold values.
        """
        if 'cpu' in thresholds:
            self._snmp_model.cpu_threshold = thresholds['cpu']
        if 'memory' in thresholds:
            self._snmp_model.memory_threshold = thresholds['memory']
        if 'disk' in thresholds:
            self._snmp_model.disk_threshold = thresholds['disk']

        self._log_panel_widget.append_info(
            f"Thresholds updated: CPU={thresholds.get('cpu', self._snmp_model.cpu_threshold)}%, "
            f"Memory={thresholds.get('memory', self._snmp_model.memory_threshold)}%, "
            f"Disk={thresholds.get('disk', self._snmp_model.disk_threshold)}%"
        )

    def _on_oid_selected(self, oid: str) -> None:
        """Handle OID selection from DeviceTreeWidget.

        Args:
            oid: Selected OID string.
        """
        self._log_panel_widget.append_info(f"OID selected: {oid}")
        self._data_table_widget.search_oid(oid)

    def _on_oid_query_requested(self, oid: str) -> None:
        """Handle OID query request from DataTableWidget.

        Args:
            oid: OID to query.
        """
        self._log_panel_widget.append_info(f"Querying OID: {oid}")

        if self._snmp_worker:
            self._snmp_worker.query_oid(oid)
        else:
            self._log_panel_widget.append_error("SNMP Worker not running, cannot query")

    def _on_oid_query_result(self, oid: str, value: object) -> None:
        """Handle OID query result.

        Args:
            oid: The queried OID.
            value: The result value.
        """
        self._data_table_widget.update_oid_value(oid, value)
        self._log_panel_widget.append_info(f"OID {oid} = {value}")

    def _on_snmp_data_updated(self, data: dict) -> None:
        """Handle SNMP model data update.

        Args:
            data: Dictionary of current metric values.
        """
        # Update dashboard
        cpu = data.get('cpu_percent')
        memory = data.get('memory_percent')
        if cpu is not None or memory is not None:
            self._dashboard_widget.update_data(cpu, memory)

        # Check thresholds and log alerts
        alerts = self._snmp_model.check_thresholds()
        for alert in alerts:
            self._log_panel_widget.append_warning(alert)

    def _on_threshold_exceeded(self, metric: str, value: float, threshold: float) -> None:
        """Handle threshold exceeded signal.

        Args:
            metric: Name of the metric (cpu, memory, disk)
            value: Current value
            threshold: Threshold value
        """
        message = f"ALERT: {metric.upper()} usage ({value:.1f}%) exceeds threshold ({threshold:.1f}%)"
        self._log_panel_widget.append_warning(message)

    def _on_log_clear_requested(self) -> None:
        """Handle log clear request."""
        logger.debug("Log panel cleared")

    def _on_start_agent_clicked(self) -> None:
        """Handle Start Agent button click."""
        self._start_agent()

    def _start_agent(self) -> None:
        """Start the Agent (called by button or start_workers)."""
        if self._agent_worker is None:
            self._agent_worker = AgentWorker(self)
            self._connect_agent_signals()

        # Start agent using the worker's start_agent method
        thresholds = {
            'cpu_threshold': self._snmp_model.cpu_threshold,
            'memory_threshold': self._snmp_model.memory_threshold,
            'disk_threshold': self._snmp_model.disk_threshold
        }
        self._agent_worker.start_agent(thresholds)

    def _stop_agent(self) -> None:
        """Stop the Agent."""
        if self._agent_worker:
            self._agent_worker.stop_agent()

    def _on_stop_agent_clicked(self) -> None:
        """Handle Stop Agent button click."""
        self._stop_agent()

    def _connect_agent_signals(self) -> None:
        """Connect AgentWorker signals."""
        if self._agent_worker:
            self._agent_worker.agent_started.connect(self._on_agent_started)
            self._agent_worker.agent_stopped.connect(self._on_agent_stopped)
            self._agent_worker.agent_error.connect(self._on_agent_error)

    def _on_agent_started(self) -> None:
        """Handle agent started signal."""
        self._agent_status_label.setText("Agent Status: Running")
        self._start_agent_btn.setEnabled(False)
        self._stop_agent_btn.setEnabled(True)
        self._log_panel_widget.append_info("Agent started")

        # Automatically start NMS workers after agent is ready
        self._start_nms_workers()

    def _on_agent_stopped(self) -> None:
        """Handle agent stopped signal."""
        self._agent_status_label.setText("Agent Status: Stopped")
        self._start_agent_btn.setEnabled(True)
        self._stop_agent_btn.setEnabled(False)
        self._log_panel_widget.append_info("Agent stopped")

    def _on_agent_error(self, error_message: str) -> None:
        """Handle agent error signal.

        Args:
            error_message: Error message from agent worker.
        """
        self._agent_status_label.setText("Agent Status: Error")
        self._log_panel_widget.append_error(f"Agent error: {error_message}")
        self._start_agent_btn.setEnabled(True)
        self._stop_agent_btn.setEnabled(False)
        logger.error(f"Agent error: {error_message}")

    def _start_nms_workers(self) -> None:
        """Start NMS worker threads (SNMP and Trap workers)."""
        if self._snmp_worker is None:
            # Get configuration for workers
            nms_config = self._config.get('nms', {})
            agent_host = nms_config.get('agent_host', '127.0.0.1')
            agent_port = nms_config.get('agent_port', 1161)  # Default to 1161
            trap_port = nms_config.get('trap_port', 11162)

            # Create workers
            self._snmp_worker = SNMPWorker(host=agent_host, port=agent_port)
            self._trap_worker = TrapWorker(port=trap_port)

            # Connect worker signals
            self._connect_worker_signals()

        # Start workers
        if not self._snmp_worker.isRunning():
            self._snmp_worker.start()
            logger.info("SNMP worker started")

        if not self._trap_worker.isRunning():
            self._trap_worker.start()
            logger.info("Trap worker started")

        self._log_panel_widget.append_info("NMS monitoring started")
        self._status_label.setText("NMS Status: Running")
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)

    def _stop_nms_workers(self) -> None:
        """Stop NMS worker threads (SNMP and Trap workers)."""
        if self._snmp_worker and self._snmp_worker.isRunning():
            self._snmp_worker.stop()
            logger.info("SNMP worker stopped")

        if self._trap_worker and self._trap_worker.isRunning():
            self._trap_worker.stop()
            logger.info("Trap worker stopped")

        self._log_panel_widget.append_info("NMS monitoring stopped")
        self._status_label.setText("NMS Status: Stopped")
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)

    def _show_about(self) -> None:
        """Show about dialog."""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "About SNMP Monitor",
            "SNMP Monitor v1.0\n\n"
            "A network monitoring application using SNMP protocol.\n\n"
            "Developed with PySide6."
        )

    def start_workers(self) -> None:
        """Start all worker threads (Agent first, then NMS).

        This is called when using menu or keyboard shortcuts.
        """
        self._start_agent()

    def stop_workers(self) -> None:
        """Stop all worker threads (NMS first, then Agent).

        This is called when using menu or keyboard shortcuts.
        """
        self._stop_nms_workers()
        self._stop_agent()

    def _connect_worker_signals(self) -> None:
        """Connect signals between workers and View components."""
        if self._snmp_worker:
            # Connect SNMP worker data signal
            self._snmp_worker.data_ready.connect(self._on_worker_data_ready)
            self._snmp_worker.error_occurred.connect(self._on_worker_error)
            # Connect query result
            self._snmp_worker.oid_query_result.connect(self._on_oid_query_result)

        if self._trap_worker:
            # Connect trap worker signal
            self._trap_worker.trap_received.connect(self._on_trap_received)
            self._trap_worker.error_occurred.connect(self._on_worker_error)

    # OID to metric name mapping for UCD-SNMP
    CPU_OID = (1, 3, 6, 1, 4, 1, 2021, 4, 3, 0)
    MEMORY_OID = (1, 3, 6, 1, 4, 1, 2021, 4, 6, 0)
    DISK_OID = (1, 3, 6, 1, 4, 1, 2021, 4, 7, 0)

    def _on_worker_data_ready(self, data: dict) -> None:
        """Handle SNMP worker data ready signal.

        Args:
            data: Dictionary of OID -> value from SNMP polling.
        """
        # Map OIDs to metric data
        metric_data = {}
        cpu_value = data.get(self.CPU_OID)
        memory_value = data.get(self.MEMORY_OID)

        if cpu_value is not None:
            metric_data['cpu_percent'] = float(cpu_value)
        if memory_value is not None:
            metric_data['memory_percent'] = float(memory_value)

        # Process and update SNMP model; the model's data_updated signal
        # drives dashboard updates through _on_snmp_data_updated.
        if metric_data:
            self._snmp_model.update_data(metric_data)

        # Update MIB model with new values if applicable
        for oid, value in data.items():
            oid_str = ".".join(map(str, oid))
            self._mib_model.update_value(oid_str, value)

    def _on_worker_error(self, error_message: str) -> None:
        """Handle worker error signal.

        Args:
            error_message: Error message from worker.
        """
        self._log_panel_widget.append_error(error_message)
        logger.error(error_message)

    def _on_trap_received(self, trap_data: dict) -> None:
        """Handle trap received signal.

        Args:
            trap_data: Dictionary containing trap information.
        """
        source = trap_data.get('source', 'Unknown')
        oid = trap_data.get('trap_oid', trap_data.get('oid', 'Unknown'))
        message = trap_data.get('message', f"Trap from {source}")
        severity = trap_data.get('severity', 'info')

        # Add to trap model
        self._trap_model.add_trap(source, oid, message, severity)

        # Log the trap
        self._log_panel_widget.append_trap(f"Trap received: {message} (from {source})")
        logger.info(f"Trap: {trap_data}")

    def start_monitoring(self) -> None:
        """Start monitoring (alias for start_workers)."""
        self.start_workers()

    def stop_monitoring(self) -> None:
        """Stop monitoring (alias for stop_workers)."""
        self.stop_workers()

    @property
    def snmp_model(self):
        """Get SNMP model instance."""
        return self._snmp_model

    @property
    def mib_model(self):
        """Get MIB model instance."""
        return self._mib_model

    @property
    def trap_model(self):
        """Get trap model instance."""
        return self._trap_model

    @property
    def dashboard_widget(self):
        """Get DashboardWidget instance."""
        return self._dashboard_widget

    @property
    def device_tree_widget(self):
        """Get DeviceTreeWidget instance."""
        return self._device_tree_widget

    @property
    def data_table_widget(self):
        """Get DataTableWidget instance."""
        return self._data_table_widget

    @property
    def log_panel_widget(self):
        """Get LogPanelWidget instance."""
        return self._log_panel_widget

    def closeEvent(self, event) -> None:
        """Handle window close event.

        This method ensures proper cleanup by stopping all workers
        and waiting for them to finish before closing.

        Args:
            event: Close event.
        """
        logger.info("MainWindow closing, cleaning up workers...")

        # Stop all workers
        self.stop_workers()

        # Wait for workers to finish (with timeout handled by stop())
        if self._snmp_worker:
            self._snmp_worker.wait(1000)
        if self._trap_worker:
            self._trap_worker.wait(1000)
        if self._agent_worker:
            self._agent_worker.wait(1000)

        self._log_panel_widget.append_info("Application closed")
        logger.info("MainWindow closed")

        # Accept the close event
        event.accept()
