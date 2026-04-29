"""Package-local models (copied from flat `src/models.py`)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, List, Set

Coordinate = Tuple[int, int]


@dataclass
class MazeData:
    width: int
    height: int
    entry: Coordinate
    exit_: Coordinate
    walls: List[List[int]]
    solution: List[Coordinate]
    pattern_cells: Set[Coordinate]
    pattern_warning: str | None = None


class MazeGenerationError(Exception):
    pass
