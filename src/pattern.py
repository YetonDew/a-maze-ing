"""Utilities for drawing the mandatory 42 pattern with closed cells."""

from src.maze import Maze


class PatternPlacementError(Exception):
    """Raised when the 42 pattern cannot be placed because it overlaps."""


# 5 rows high, 7 columns wide. Cells marked with X stay fully closed.
PATTERN_42 = (
    "X   XXX",
    "X     X",
    "XXX XXX",
    "  X X  ",
    "  X XXX",
)
PATTERN_WIDTH = len(PATTERN_42[0])
PATTERN_HEIGHT = len(PATTERN_42)


def can_place_42(maze: Maze) -> bool:
    """Return True if the maze is large enough for the 42 pattern."""
    return (
        maze.width >= PATTERN_WIDTH + 2
        and maze.height >= PATTERN_HEIGHT + 2
    )


def place_42_pattern(maze: Maze) -> bool:
    """Place a closed-cell 42 pattern near the center of the maze.

    Returns:
        True if the pattern was placed, False if the maze is too small or the
        pattern would cover entry or exit.
    """
    if not can_place_42(maze):
        return False

    start_x = max(1, (maze.width - PATTERN_WIDTH) // 2)
    start_y = max(1, (maze.height - PATTERN_HEIGHT) // 2)
    pattern_cells = set()

    for dy, row in enumerate(PATTERN_42):
        for dx, char in enumerate(row):
            if char == "X":
                coord = (start_x + dx, start_y + dy)
                if coord == maze.entry:
                    raise PatternPlacementError(
                        "Entry point is inside the 42 pattern; cannot "
                        "create the maze"
                    )
                if coord == maze.exit:
                    raise PatternPlacementError(
                        "Exit point is inside the 42 pattern; cannot "
                        "create the maze"
                    )
                pattern_cells.add(coord)

    for x, y in pattern_cells:
        maze.mark_blocked(x, y)
    return True
