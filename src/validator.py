"""Validation helpers for generated mazes."""

from collections import deque

from src.maze import DIRECTIONS, OPPOSITE, Maze, Cell


class MazeValidationError(Exception):
    """Raised when a generated maze is invalid."""


def validate_maze(maze: Maze, perfect: bool) -> None:
    """Validate the generated maze and raise a clear error if invalid."""
    if not wall_consistency_ok(maze):
        raise MazeValidationError("Neighboring walls are not coherent")
    if not borders_are_closed(maze):
        raise MazeValidationError("External borders must stay closed")
    if not is_connected(maze):
        raise MazeValidationError("Maze is not fully connected")
    if perfect and not is_perfect(maze):
        raise MazeValidationError(
            "PERFECT=True requires exactly one path between cells"
        )
    if has_forbidden_open_area(maze):
        raise MazeValidationError("Maze contains a forbidden 3x3 open area")


def wall_consistency_ok(maze: Maze) -> bool:
    """Return True if adjacent cells agree on shared walls."""
    for cell in maze.cells():
        for direction in DIRECTIONS:
            neighbor = maze.get_neighbor(cell, direction)
            if neighbor is None:
                continue
            if cell.walls[direction] != neighbor.walls[OPPOSITE[direction]]:
                return False
    return True


def borders_are_closed(maze: Maze) -> bool:
    """Return True if the maze has walls on all outside borders."""
    for x in range(maze.width):
        if not maze.get_cell(x, 0).walls["TOP"]:
            return False
        if not maze.get_cell(x, maze.height - 1).walls["BOT"]:
            return False
    for y in range(maze.height):
        if not maze.get_cell(0, y).walls["LEFT"]:
            return False
        if not maze.get_cell(maze.width - 1, y).walls["RIGHT"]:
            return False
    return True


def is_connected(maze: Maze) -> bool:
    """Return True if every non-blocked cell is reachable from entry."""
    start = maze.get_cell(*maze.entry)
    if start.blocked:
        return False

    target_count = len(maze.carveable_cells())
    seen = _reachable_cells(maze, start)
    return len(seen) == target_count


def is_perfect(maze: Maze) -> bool:
    """Return True if the maze is connected and acyclic over non-blocked
    cells."""
    if not is_connected(maze):
        return False
    nodes = len(maze.carveable_cells())
    edges = 0
    for cell in maze.carveable_cells():
        for _direction, _neighbor in maze.accessible_neighbors(cell):
            edges += 1
    edges //= 2
    return edges == nodes - 1


def has_forbidden_open_area(maze: Maze) -> bool:
    """Detect a fully connected 3x3 open area.

    The subject allows 2x3 or 3x2 open spaces but not 3x3 open spaces. This
    check flags any 3x3 block where all inner shared walls are open.
    """
    if maze.width < 3 or maze.height < 3:
        return False

    for y in range(maze.height - 2):
        for x in range(maze.width - 2):
            cells = [
                maze.get_cell(cx, cy)
                for cy in range(y, y + 3)
                for cx in range(x, x + 3)
            ]
            if any(cell.blocked for cell in cells):
                continue
            if _three_by_three_is_open(maze, x, y):
                return True
    return False


def _three_by_three_is_open(maze: Maze, x: int, y: int) -> bool:
    """Return True if all shared walls inside one 3x3 area are open."""
    for cy in range(y, y + 3):
        for cx in range(x, x + 2):
            if maze.get_cell(cx, cy).walls["RIGHT"]:
                return False
    for cy in range(y, y + 2):
        for cx in range(x, x + 3):
            if maze.get_cell(cx, cy).walls["BOT"]:
                return False
    return True


def _reachable_cells(maze: Maze, start: Cell) -> set[tuple[int, int]]:
    """Return all cells reachable through open walls from start."""
    queue: deque[Cell] = deque([start])
    seen = {(start.x, start.y)}

    while queue:
        cell = queue.popleft()
        for _direction, neighbor in maze.accessible_neighbors(cell):
            coord = (neighbor.x, neighbor.y)
            if coord in seen:
                continue
            seen.add(coord)
            queue.append(neighbor)
    return seen
