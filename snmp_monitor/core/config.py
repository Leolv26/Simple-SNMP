"""Configuration loading utilities for SNMP Monitor."""
import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


def find_config_file(config_path: Optional[str] = None) -> Optional[Path]:
    """Find the configuration file.

    Args:
        config_path: Optional explicit path to config file.

    Returns:
        Path to config file if found, None otherwise.
    """
    if config_path:
        path = Path(config_path)
        if path.exists():
            return path
        return None

    # Search for config.yaml in common locations
    search_paths = [
        Path.cwd() / 'config.yaml',
        Path(__file__).parent.parent.parent / 'config.yaml',
        Path(__file__).parent.parent / 'config.yaml',
    ]

    for path in search_paths:
        if path.exists():
            return path

    return None


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Optional path to configuration file.

    Returns:
        Dictionary containing configuration data.
    """
    config_file = find_config_file(config_path)

    if config_file is None:
        return {}

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config if config else {}
    except Exception:
        return {}


def get_threshold_defaults() -> Dict[str, float]:
    """Get default threshold values.

    Returns:
        Dictionary with default threshold values.
    """
    return {
        'cpu': 80.0,
        'memory': 85.0,
        'disk': 90.0
    }
