"""Dashboard widget for displaying real-time CPU and memory charts.

This module provides the DashboardWidget class which:
- Inherits from QWidget for PySide6 integration
- Embeds matplotlib figures using FigureCanvasQTAgg
- Displays CPU and memory usage as line charts
- Supports scrolling window for recent data points
- Provides update_data() method for real-time updates
"""
import logging
from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy, QWidget, QVBoxLayout

import matplotlib
# Configure matplotlib to use available fonts instead of DejaVu Sans
# Must be set before importing pyplot or Figure
# Use fonts that support Chinese characters
# Priority: WenQuanYi > SimSun > Microsoft YaHei > Arial > Helvetica
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei', 'SimSun', 'Microsoft YaHei', 'Arial', 'Helvetica', 'sans-serif']

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties

logger = logging.getLogger(__name__)

# Create font properties for Chinese characters
# Use a specific Chinese font that's available
CHINESE_FONT = FontProperties(family='WenQuanYi Micro Hei')


class DashboardWidget(QWidget):
    """Dashboard widget for displaying real-time CPU and memory charts.

    This widget displays CPU and memory usage as line charts using matplotlib,
    embedded in a PySide6 widget. It maintains a rolling window of data points
    and automatically updates the charts when new data is received.

    Attributes:
        _max_points: Maximum number of data points to display in the window.
        _cpu_data: List of CPU usage values.
        _memory_data: List of memory usage values.
        _fig: Matplotlib Figure object.
        _canvas: FigureCanvasQTAgg for rendering the figure.
        _ax_cpu: Matplotlib Axes for CPU chart.
        _ax_memory: Matplotlib Axes for memory chart.

    Example:
        >>> widget = DashboardWidget()
        >>> widget.update_data(50.0, 60.0)  # CPU=50%, Memory=60%
    """

    MINIMUM_CHART_HEIGHT = 360

    def __init__(self, max_points: int = 50, parent: Optional[QWidget] = None) -> None:
        """Initialize the DashboardWidget.

        Args:
            max_points: Maximum number of data points to display in the
                scrolling window. Defaults to 50.
            parent: Optional parent widget.
        """
        super().__init__(parent)

        # Configuration
        self._max_points = max_points
        self.setMinimumHeight(self.MINIMUM_CHART_HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

        # Data storage
        self._cpu_data: List[float] = []
        self._memory_data: List[float] = []

        # Setup matplotlib
        self._setup_matplotlib()

        # Setup layout
        self._setup_layout()

        logger.debug(f"DashboardWidget initialized with max_points={max_points}")

    def _setup_matplotlib(self) -> None:
        """Setup matplotlib figure and axes."""
        # Create figure with 2 subplots (stacked vertically)
        self._fig = Figure(figsize=(8, 6), dpi=100)
        self._fig.patch.set_facecolor('#f0f0f0')

        # Create canvas for rendering
        self._canvas = FigureCanvasQTAgg(self._fig)
        self._canvas.setMinimumHeight(self.MINIMUM_CHART_HEIGHT)
        self._canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

        # Create subplots
        self._ax_cpu = self._fig.add_subplot(2, 1, 1)
        self._ax_memory = self._fig.add_subplot(2, 1, 2)

        # Configure CPU chart
        self._ax_cpu.set_title('CPU 使用率 (%)', fontproperties=CHINESE_FONT)
        self._ax_cpu.set_xlabel('采样点', fontproperties=CHINESE_FONT)
        self._ax_cpu.set_ylabel('使用率 (%)', fontproperties=CHINESE_FONT)
        self._ax_cpu.set_ylim(0, 100)
        self._ax_cpu.grid(True, linestyle='--', alpha=0.7)
        self._ax_cpu.set_facecolor('#ffffff')

        # Configure Memory chart
        self._ax_memory.set_title('内存使用率 (%)', fontproperties=CHINESE_FONT)
        self._ax_memory.set_xlabel('采样点', fontproperties=CHINESE_FONT)
        self._ax_memory.set_ylabel('使用率 (%)', fontproperties=CHINESE_FONT)
        self._ax_memory.set_ylim(0, 100)
        self._ax_memory.grid(True, linestyle='--', alpha=0.7)
        self._ax_memory.set_facecolor('#ffffff')

        # Adjust layout
        self._fig.tight_layout()

    def _setup_layout(self) -> None:
        """Setup the widget layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._canvas)

    def update_data(self, cpu: Optional[float], memory: Optional[float]) -> None:
        """Update the charts with new CPU and memory data.

        This method adds new data points to the scrolling window,
        removes old data points when the window is full, and
        redraws both charts.

        Args:
            cpu: Current CPU usage percentage (0-100).
            memory: Current memory usage percentage (0-100).

        Example:
            >>> widget.update_data(50.0, 60.0)
        """
        # Handle None values
        if cpu is not None:
            self._cpu_data.append(cpu)
        if memory is not None:
            self._memory_data.append(memory)

        # Trim data to max_points (FIFO)
        if len(self._cpu_data) > self._max_points:
            self._cpu_data = self._cpu_data[-self._max_points:]
        if len(self._memory_data) > self._max_points:
            self._memory_data = self._memory_data[-self._max_points:]

        # Update charts
        self._update_charts()

        # Redraw canvas
        self._canvas.draw()

    def _update_charts(self) -> None:
        """Update both CPU and memory charts with current data."""
        # Clear previous plots
        self._ax_cpu.clear()
        self._ax_memory.clear()

        # Generate x-axis values
        x_cpu = list(range(len(self._cpu_data)))
        x_memory = list(range(len(self._memory_data)))

        # Plot CPU data
        if self._cpu_data:
            self._ax_cpu.plot(x_cpu, self._cpu_data, 'b-', linewidth=2,
                              label='CPU (%)', marker='o', markersize=3)
            self._ax_cpu.legend(loc='upper right')
            self._ax_cpu.set_ylim(0, 100)

        # Configure CPU chart with explicit font settings
        self._ax_cpu.set_title('CPU 使用率 (%)', fontproperties=CHINESE_FONT)
        self._ax_cpu.set_xlabel('采样点', fontproperties=CHINESE_FONT)
        self._ax_cpu.set_ylabel('使用率 (%)', fontproperties=CHINESE_FONT)
        self._ax_cpu.grid(True, linestyle='--', alpha=0.7)
        self._ax_cpu.set_facecolor('#ffffff')

        # Plot memory data
        if self._memory_data:
            self._ax_memory.plot(x_memory, self._memory_data, 'g-', linewidth=2,
                                label='Memory (%)', marker='s', markersize=3)
            self._ax_memory.legend(loc='upper right')
            self._ax_memory.set_ylim(0, 100)

        # Configure memory chart with explicit font settings
        self._ax_memory.set_title('内存使用率 (%)', fontproperties=CHINESE_FONT)
        self._ax_memory.set_xlabel('采样点', fontproperties=CHINESE_FONT)
        self._ax_memory.set_ylabel('使用率 (%)', fontproperties=CHINESE_FONT)
        self._ax_memory.grid(True, linestyle='--', alpha=0.7)
        self._ax_memory.set_facecolor('#ffffff')

        # Update layout
        self._fig.tight_layout()

    def reset(self) -> None:
        """Reset the dashboard by clearing all data.

        This method clears both CPU and memory data lists and
        redraws the empty charts.

        Example:
            >>> widget.reset()
        """
        self._cpu_data.clear()
        self._memory_data.clear()
        self._update_charts()
        self._canvas.draw()
        logger.debug("DashboardWidget data reset")

    @property
    def cpu_data(self) -> List[float]:
        """Get the list of CPU data points.

        Returns:
            List of CPU usage percentages.
        """
        return self._cpu_data.copy()

    @property
    def memory_data(self) -> List[float]:
        """Get the list of memory data points.

        Returns:
            List of memory usage percentages.
        """
        return self._memory_data.copy()

    @property
    def max_points(self) -> int:
        """Get the maximum number of data points.

        Returns:
            Maximum number of data points in the window.
        """
        return self._max_points
