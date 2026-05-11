"""Tests for GUI module structure and initialization."""
import sys
import importlib
from pathlib import Path


class TestGUIModuleStructure:
    """Test that GUI module structure is properly created."""

    def test_gui_package_exists(self):
        """Test that snmp_monitor.gui package can be imported."""
        import snmp_monitor.gui
        assert snmp_monitor.gui is not None

    def test_gui_models_subpackage_exists(self):
        """Test that snmp_monitor.gui.models subpackage exists."""
        import snmp_monitor.gui.models
        assert snmp_monitor.gui.models is not None

    def test_gui_views_subpackage_exists(self):
        """Test that snmp_monitor.gui.views subpackage exists."""
        import snmp_monitor.gui.views
        assert snmp_monitor.gui.views is not None

    def test_gui_workers_subpackage_exists(self):
        """Test that snmp_monitor.gui.workers subpackage exists."""
        import snmp_monitor.gui.workers
        assert snmp_monitor.gui.workers is not None

    def test_gui_main_module_exists(self):
        """Test that snmp_monitor.gui.__main__ module exists."""
        import snmp_monitor.gui.__main__
        assert snmp_monitor.gui.__main__ is not None

    def test_gui_main_has_main_function(self):
        """Test that __main__ module has a main() function."""
        import snmp_monitor.gui.__main__ as gui_main
        assert hasattr(gui_main, 'main')
        assert callable(gui_main.main)

    def test_gui_main_runnable_as_module(self):
        """Test that GUI can be run as python -m snmp_monitor.gui."""
        gui_path = Path(__file__).parent.parent.parent / 'snmp_monitor' / 'gui' / '__main__.py'
        assert gui_path.exists(), "GUI __main__.py should exist"

        # Read the file and verify it has the required structure
        content = gui_path.read_text()
        assert 'if __name__ == "__main__"' in content, "__main__.py should have entry point"
        assert 'main()' in content, "__main__.py should call main()"

    def test_gui_main_has_error_handling(self):
        """Test that main() function includes error handling."""
        import snmp_monitor.gui.__main__ as gui_main
        import inspect

        # Get the source code of the main function
        source = inspect.getsource(gui_main.main)
        assert 'try' in source, "main() should have try-except error handling"
        assert 'except' in source, "main() should have try-except error handling"

    def test_gui_main_has_logging(self):
        """Test that main() function includes logging configuration."""
        import snmp_monitor.gui.__main__ as gui_main
        import inspect

        # Get the source code of the main function
        source = inspect.getsource(gui_main.main)
        assert 'logging' in source, "main() should use logging"
        assert '_configure_logging' in source, "main() should call logging configuration"

