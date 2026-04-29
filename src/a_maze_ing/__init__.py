"""A-Maze-ing package public API."""

from .generator import MazeGenerator, MazeData, MazeGenerationError
from .config_parser import parse_config, ConfigError

__all__ = [
    "MazeGenerator",
    "MazeData",
    "MazeGenerationError",
    "parse_config",
    "ConfigError",
]
