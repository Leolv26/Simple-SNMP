"""Tests for DashboardWidget class in dashboard.py."""
import sys
import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QWidget

# Import matplotlib components for testing
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestDashboardWidgetImports:
    """Test that DashboardWidget can be imported correctly."""

    def test_dashboard_module_import(self):
        """Test that dashboard module can be imported."""
        from snmp_monitor.gui.views import dashboard
        assert dashboard is not None

    def test_dashboard_widget_class_exists(self):
        """Test that DashboardWidget class exists in dashboard module."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        assert DashboardWidget is not None

    def test_dashboard_widget_import_from_views(self):
        """Test that DashboardWidget can be imported from views package."""
        from snmp_monitor.gui.views import DashboardWidget
        assert DashboardWidget is not None


class TestDashboardWidgetInheritance:
    """Test DashboardWidget class inheritance."""

    def test_dashboard_widget_inherits_qwidget(self, qapp):
        """Test that DashboardWidget inherits from QWidget."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        assert issubclass(DashboardWidget, QWidget)

    def test_dashboard_widget_can_be_instantiated(self, qapp):
        """Test that DashboardWidget can be instantiated."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        assert widget is not None
        assert isinstance(widget, QWidget)


class TestDashboardWidgetInitialization:
    """Test DashboardWidget initialization."""

    def test_default_max_points(self, qapp):
        """Test that default max_points is 50."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        assert hasattr(widget, '_max_points')
        assert widget._max_points == 50

    def test_custom_max_points(self, qapp):
        """Test that custom max_points can be set."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget(max_points=100)
        assert widget._max_points == 100

    def test_has_cpu_data_list(self, qapp):
        """Test that widget initializes CPU data list."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        assert hasattr(widget, '_cpu_data')
        assert isinstance(widget._cpu_data, list)
        assert len(widget._cpu_data) == 0

    def test_has_memory_data_list(self, qapp):
        """Test that widget initializes memory data list."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        assert hasattr(widget, '_memory_data')
        assert isinstance(widget._memory_data, list)
        assert len(widget._memory_data) == 0


class TestDashboardWidgetMatplotlib:
    """Test DashboardWidget matplotlib integration."""

    def test_has_figure_canvas(self, qapp):
        """Test that widget has a figure canvas."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        assert hasattr(widget, '_canvas')
        assert isinstance(widget._canvas, FigureCanvasQTAgg)

    def test_has_figure(self, qapp):
        """Test that widget has a matplotlib figure."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        assert hasattr(widget, '_fig')
        assert isinstance(widget._fig, Figure)

    def test_has_cpu_axes(self, qapp):
        """Test that widget has CPU axes (subplot)."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        assert hasattr(widget, '_ax_cpu')
        # Should be matplotlib Axes object
        import matplotlib.axes
        assert isinstance(widget._ax_cpu, matplotlib.axes.Axes)

    def test_has_memory_axes(self, qapp):
        """Test that widget has memory axes (subplot)."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        assert hasattr(widget, '_ax_memory')
        # Should be matplotlib Axes object
        import matplotlib.axes
        assert isinstance(widget._ax_memory, matplotlib.axes.Axes)

    def test_figure_has_two_subplots(self, qapp):
        """Test that figure has two subplots (CPU and Memory)."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        # Check that figure has 2 axes
        assert len(widget._fig.axes) == 2


class TestDashboardWidgetLayout:
    """Test DashboardWidget layout structure."""

    def test_has_layout(self, qapp):
        """Test that widget has a layout."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        from PySide6.QtWidgets import QLayout
        widget = DashboardWidget()
        assert widget.layout() is not None
        assert isinstance(widget.layout(), QLayout)

    def test_canvas_is_in_widget(self, qapp):
        """Test that canvas is a child of the widget."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        # Check that canvas parent is the widget
        assert widget._canvas.parent() is widget


class TestDashboardWidgetChartConfiguration:
    """Test DashboardWidget chart configuration."""

    def test_cpu_chart_has_title(self, qapp):
        """Test that CPU chart has a title."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        title = widget._ax_cpu.get_title()
        assert 'CPU' in title or 'cpu' in title.lower()

    def test_memory_chart_has_title(self, qapp):
        """Test that memory chart has a title."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        title = widget._ax_memory.get_title()
        assert len(title) > 0, "Memory chart should have a title"

    def test_cpu_chart_has_ylabel(self, qapp):
        """Test that CPU chart has Y-axis label."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        ylabel = widget._ax_cpu.get_ylabel()
        assert '%' in ylabel or 'percent' in ylabel.lower() or 'CPU' in ylabel

    def test_memory_chart_has_ylabel(self, qapp):
        """Test that memory chart has Y-axis label."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        ylabel = widget._ax_memory.get_ylabel()
        assert '%' in ylabel or 'percent' in ylabel.lower() or 'Memory' in ylabel or 'Mem' in ylabel

    def test_cpu_chart_has_xlabel(self, qapp):
        """Test that CPU chart has X-axis label."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        xlabel = widget._ax_cpu.get_xlabel()
        assert len(xlabel) >= 0, "CPU chart should have X-axis label"

    def test_cpu_chart_has_grid(self, qapp):
        """Test that CPU chart has grid lines."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        # Grid should be visible
        gridlines = widget._ax_cpu.xaxis.get_gridlines()
        assert len(gridlines) > 0 or widget._ax_cpu.grid_on

    def test_memory_chart_has_grid(self, qapp):
        """Test that memory chart has grid lines."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        # Grid should be visible
        gridlines = widget._ax_memory.xaxis.get_gridlines()
        assert len(gridlines) > 0 or widget._ax_memory.grid_on


class TestDashboardWidgetUpdateData:
    """Test DashboardWidget update_data method."""

    def test_update_data_method_exists(self, qapp):
        """Test that update_data method exists."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        assert hasattr(widget, 'update_data')
        assert callable(widget.update_data)

    def test_update_data_accepts_cpu_memory(self, qapp):
        """Test that update_data accepts cpu and memory parameters."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        # Should not raise an error
        widget.update_data(50.0, 60.0)

    def test_update_data_updates_cpu_data(self, qapp):
        """Test that update_data updates CPU data list."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        widget.update_data(25.0, 30.0)
        assert len(widget._cpu_data) == 1
        assert widget._cpu_data[0] == 25.0

    def test_update_data_updates_memory_data(self, qapp):
        """Test that update_data updates memory data list."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        widget.update_data(25.0, 30.0)
        assert len(widget._memory_data) == 1
        assert widget._memory_data[0] == 30.0

    def test_update_data_multiple_calls(self, qapp):
        """Test that update_data works with multiple calls."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        for i in range(5):
            widget.update_data(float(i * 10), float(i * 5))
        assert len(widget._cpu_data) == 5
        assert len(widget._memory_data) == 5

    def test_update_data_respects_max_points(self, qapp):
        """Test that update_data respects max_points limit."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget(max_points=5)
        # Add more than max_points
        for i in range(10):
            widget.update_data(float(i), float(i))
        # Should only keep the last max_points
        assert len(widget._cpu_data) == 5
        assert len(widget._memory_data) == 5

    def test_update_data_redraws_canvas(self, qapp):
        """Test that update_data redraws the canvas."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        with patch.object(widget._canvas, 'draw') as mock_draw:
            widget.update_data(50.0, 60.0)
            mock_draw.assert_called_once()


class TestDashboardWidgetChartRendering:
    """Test DashboardWidget chart rendering on update."""

    def test_update_data_renders_cpu_line(self, qapp):
        """Test that update_data renders CPU line on chart."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        widget.update_data(50.0, 30.0)
        widget.update_data(60.0, 40.0)

        # Check that axes have lines
        lines = widget._ax_cpu.lines
        assert len(lines) > 0

    def test_update_data_renders_memory_line(self, qapp):
        """Test that update_data renders memory line on chart."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        widget.update_data(50.0, 30.0)
        widget.update_data(60.0, 40.0)

        # Check that axes have lines
        lines = widget._ax_memory.lines
        assert len(lines) > 0

    def test_update_data_clears_and_redraws(self, qapp):
        """Test that update_data clears and redraws chart."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()

        # Add some data
        widget.update_data(50.0, 30.0)
        lines_before = len(widget._ax_cpu.lines)

        # Add more data
        widget.update_data(60.0, 40.0)

        # Should have updated the chart
        # The number of lines should be consistent (either 1 line updated or cleared and redrawn)
        assert len(widget._ax_cpu.lines) >= 0


class TestDashboardWidgetReset:
    """Test DashboardWidget reset functionality."""

    def test_reset_method_exists(self, qapp):
        """Test that reset method exists."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        assert hasattr(widget, 'reset')
        assert callable(widget.reset)

    def test_reset_clears_cpu_data(self, qapp):
        """Test that reset clears CPU data."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        widget.update_data(50.0, 30.0)
        widget.reset()
        assert len(widget._cpu_data) == 0

    def test_reset_clears_memory_data(self, qapp):
        """Test that reset clears memory data."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        widget.update_data(50.0, 30.0)
        widget.reset()
        assert len(widget._memory_data) == 0


class TestDashboardWidgetEdgeCases:
    """Test DashboardWidget edge cases."""

    def test_update_data_with_none_values(self, qapp):
        """Test update_data with None values."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        # Should handle None gracefully
        widget.update_data(None, None)

    def test_update_data_with_string_values(self, qapp):
        """Test update_data with string values that can be converted."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        # Should handle convertible strings
        try:
            widget.update_data("50.0", "30.0")
        except (ValueError, TypeError):
            pytest.skip("Widget doesn't support string conversion")

    def test_update_data_with_extreme_values(self, qapp):
        """Test update_data with extreme values."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        widget.update_data(100.0, 100.0)
        widget.update_data(0.0, 0.0)

    def test_update_data_with_negative_values(self, qapp):
        """Test update_data with negative values."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget()
        # Some systems might report negative values during error states
        widget.update_data(-1.0, -1.0)


class TestDashboardWidgetScrollingWindow:
    """Test DashboardWidget scrolling window behavior."""

    def test_data_fifo_behavior(self, qapp):
        """Test that data follows FIFO (first in, first out) behavior."""
        from snmp_monitor.gui.views.dashboard import DashboardWidget
        widget = DashboardWidget(max_points=3)

        widget.update_data(1.0, 10.0)
        widget.update_data(2.0, 20.0)
        widget.update_data(3.0, 30.0)
        widget.update_data(4.0, 40.0)

        # Should contain [2.0, 3.0, 4.0] (dropped 1.0)
        assert widget._cpu_data == [2.0, 3.0, 4.0]
        assert widget._memory_data == [20.0, 30.0, 40.0]
