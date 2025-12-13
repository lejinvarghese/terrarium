"""Landscape path helpers - assumes consistent structure"""

from pathlib import Path

LANDSCAPES_DIR = Path(__file__).parent.parent / "landscapes"


def get_landscape_path(landscape_name: str) -> Path:
    """Get path to landscape incubator directory"""
    return LANDSCAPES_DIR / landscape_name / "incubator"


def get_observations_path(landscape_name: str) -> Path:
    """Get observations database path"""
    return get_landscape_path(landscape_name) / "observations.db"


def get_memory_path(landscape_name: str) -> Path:
    """Get memory database path"""
    return get_landscape_path(landscape_name) / "memory.db"


def list_landscapes() -> list:
    """List all available landscapes"""
    landscapes = []
    for landscape_dir in LANDSCAPES_DIR.iterdir():
        if landscape_dir.is_dir() and not landscape_dir.name.startswith("_"):
            incubator_path = landscape_dir / "incubator"
            if incubator_path.exists():
                landscapes.append(landscape_dir.name)
    return landscapes
