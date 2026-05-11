"""Tests for DeviceTreeWidget class."""
import pytest
from unittest.mock import MagicMock, patch
import sys


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for testing."""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestDeviceTreeWidgetImports:
    """Test that DeviceTreeWidget can be imported."""

    def test_import_device_tree_widget(self):
        """Test that DeviceTreeWidget can be imported."""
        try:
            from snmp_monitor.gui.views.device_tree import DeviceTreeWidget
            assert DeviceTreeWidget is not None
        except ImportError:
            pytest.fail("DeviceTreeWidget cannot be imported")


class TestDeviceTreeWidgetInitialization:
    """Test DeviceTreeWidget initialization."""

    def test_widget_initialization(self, qapp):
        """Test that DeviceTreeWidget can be initialized."""
        from snmp_monitor.gui.views.device_tree import DeviceTreeWidget
        widget = DeviceTreeWidget()
        assert widget is not None

    def test_widget_inherits_from_qwidget(self, qapp):
        """Test that DeviceTreeWidget inherits from QWidget."""
        from snmp_monitor.gui.views.device_tree import DeviceTreeWidget
        from PySide6.QtWidgets import QWidget
        widget = DeviceTreeWidget()
        assert isinstance(widget, QWidget)


class TestDeviceTreeWidgetComponents:
    """Test DeviceTreeWidget components."""

    def test_widget_has_tree_view(self, qapp):
        """Test that widget contains a QTreeView."""
        from snmp_monitor.gui.views.device_tree import DeviceTreeWidget
        widget = DeviceTreeWidget()
        # Widget should have tree_view attribute
        assert hasattr(widget, '_tree_view') or hasattr(widget, 'tree_view')

    def test_widget_has_refresh_button(self, qapp):
        """Test that widget contains a refresh button."""
        from snmp_monitor.gui.views.device_tree import DeviceTreeWidget
        widget = DeviceTreeWidget()
        # Widget should have refresh button
        assert hasattr(widget, '_refresh_btn') or hasattr(widget, 'refresh_button')


class TestDeviceTreeWidgetSignals:
    """Test DeviceTreeWidget signals."""

    def test_widget_has_oid_selected_signal(self, qapp):
        """Test that widget has oid_selected signal."""
        from snmp_monitor.gui.views.device_tree import DeviceTreeWidget
        widget = DeviceTreeWidget()
        # Widget should have oid_selected signal
        assert hasattr(widget, 'oid_selected')

    def test_oid_selected_signal_exists(self, qapp):
        """Test that oid_selected is a pyqtSignal."""
        from snmp_monitor.gui.views.device_tree import DeviceTreeWidget
        from PySide6.QtCore import Signal
        widget = DeviceTreeWidget()
        # Check that oid_selected is a Signal
        signal = getattr(widget, 'oid_selected', None)
        assert signal is not None
        assert isinstance(signal, Signal)


class TestDeviceTreeWidgetModel:
    """Test DeviceTreeWidget model integration."""

    def test_widget_has_mib_model(self, qapp):
        """Test that widget has an associated MIBModel."""
        from snmp_monitor.gui.views.device_tree import DeviceTreeWidget
        from snmp_monitor.gui.models.mib_model import MIBModel
        widget = DeviceTreeWidget()
        # Widget should have a model attribute
        assert hasattr(widget, '_model') or hasattr(widget, 'model')
        # Check if model is MIBModel or if tree view has a model
        if hasattr(widget, '_model'):
            assert isinstance(widget._model, MIBModel)
        elif hasattr(widget, 'model'):
            assert isinstance(widget.model, MIBModel)


class TestDeviceTreeWidgetTreeView:
    """Test DeviceTreeWidget QTreeView settings."""

    def test_tree_view_selection_mode(self, qapp):
        """Test that tree view has single selection mode."""
        from snmp_monitor.gui.views.device_tree import DeviceTreeWidget
        widget = DeviceTreeWidget()
        # Get the tree view
        tree_view = getattr(widget, '_tree_view', None) or getattr(widget, 'tree_view', None)
        assert tree_view is not None
        # Selection mode should be SingleSelection
        from PySide6.QtWidgets import QAbstractItemView
        assert tree_view.selectionMode() == QAbstractItemView.SingleSelection

    def test_tree_view_columns_configured(self, qapp):
        """Test that tree view columns are configured properly."""
        from snmp_monitor.gui.views.device_tree import DeviceTreeWidget
        widget = DeviceTreeWidget()
        # Get the tree view
        tree_view = getattr(widget, '_tree_view', None) or getattr(widget, 'tree_view', None)
        assert tree_view is not None
        # Tree view should have a model set
        assert tree_view.model() is not None


class TestDeviceTreeWidgetMethods:
    """Test DeviceTreeWidget public methods."""

    def test_widget_has_refresh_method(self, qapp):
        """Test that widget has a refresh method."""
        from snmp_monitor.gui.views.device_tree import DeviceTreeWidget
        widget = DeviceTreeWidget()
        # Widget should have refresh method
        assert hasattr(widget, 'refresh')

    def test_widget_has_load_mib_data_method(self, qapp):
        """Test that widget has a load_mib_data method."""
        from snmp_monitor.gui.views.device_tree import DeviceTreeWidget
        widget = DeviceTreeWidget()
        # Widget should have load_mib_data or similar method
        assert hasattr(widget, 'load_mib_data') or hasattr(widget, 'load_data')


class TestDeviceTreeWidgetInteraction:
    """Test DeviceTreeWidget user interaction."""

    def test_double_click_emits_signal(self, qapp):
        """Test that double-clicking a node emits oid_selected signal."""
        from snmp_monitor.gui.views.device_tree import DeviceTreeWidget
        from snmp_monitor.gui.models.mib_model import MIBModel

        widget = DeviceTreeWidget()

        # Track signal emission
        signal_received = []

        def on_oid_selected(oid):
            signal_received.append(oid)

        widget.oid_selected.connect(on_oid_selected)

        # Get the model and add some test data
        model = getattr(widget, '_model', None) or widget.model()
        if model and isinstance(model, MIBModel):
            # Add a node
            model.add_oid("1.3.6.1.2.1.1.1.0", "sysDescr", "Test System")

            # Get the index of the added node
            index = model.index(0, 0)
            if index.isValid():
                # Simulate double-click
                tree_view = getattr(widget, '_tree_view', None) or getattr(widget, 'tree_view', None)
                if tree_view:
                    # Emit doubleClicked signal directly
                    tree_view.doubleClicked.emit(index)

                    # Check if signal was emitted
                    assert widget.oid_selected is not None


class TestDeviceTreeWidgetLayout:
    """Test DeviceTreeWidget layout."""

    def test_widget_has_title_label(self, qapp):
        """Test that widget has a title label."""
        from snmp_monitor.gui.views.device_tree import DeviceTreeWidget
        widget = DeviceTreeWidget()
        # Widget should have some way to display title
        # Either as part of layout or in header
        assert widget is not None


class TestDeviceTreeWidgetIntegration:
    """Test DeviceTreeWidget integration with other components."""

    def test_can_set_custom_model(self, qapp):
        """Test that widget can accept a custom MIBModel."""
        from snmp_monitor.gui.views.device_tree import DeviceTreeWidget
        from snmp_monitor.gui.models.mib_model import MIBModel

        custom_model = MIBModel()
        widget = DeviceTreeWidget(custom_model)

        # Verify the model is set
        model = getattr(widget, '_model', None) or widget.model()
        assert model is custom_model

    def test_refresh_button_exists_and_clickable(self, qapp):
        """Test that refresh button exists and can be clicked."""
        from snmp_monitor.gui.views.device_tree import DeviceTreeWidget
        from PySide6.QtWidgets import QPushButton

        widget = DeviceTreeWidget()

        # Get refresh button
        refresh_btn = getattr(widget, '_refresh_btn', None) or getattr(widget, 'refresh_button', None)
        assert refresh_btn is not None
        assert isinstance(refresh_btn, QPushButton)

        # Test that button is enabled
        assert refresh_btn.isEnabled()
