"""Maze generation algorithms."""

import random

from src.maze import DIRECTIONS, Maze, Cell
from src.pattern import PatternPlacementError, place_42_pattern
from src.validator import has_forbidden_open_area, is_connected, is_perfect


class MazeGenerationError(Exception):
    """Raised when a valid maze cannot be generated."""


class MazeGenerator:
    """Reusable maze generator class.

    The generator currently uses randomized depth-first search.
    It creates a perfect maze first, then optionally removes extra walls to
    make it imperfect.
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_cell: tuple[int, int],
        perfect: bool = True,
        seed: int | None = None,
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit_cell
        self.perfect = perfect
        self.seed = seed
        self.random = random.Random(seed)
        self.maze: Maze | None = None

    def generate(self) -> Maze:
        """Generate and return a valid maze."""
        for attempt in range(200):
            if self.seed is not None:
                self.random = random.Random(self.seed + attempt)
            maze = Maze(self.width, self.height, self.entry, self.exit)

            try:
                placed = place_42_pattern(maze)
            except PatternPlacementError as exc:
                raise MazeGenerationError(str(exc)) from exc
            if not placed:
                print(
                    "Warning: maze too small or invalid position for "
                    "visible 42 pattern"
                )

            start = maze.get_cell(*self.entry)
            if start.blocked or maze.get_cell(*self.exit).blocked:
                continue

            self._depth_first_carve(maze, start)
            if not self.perfect:
                self._make_imperfect(maze)

            if not is_connected(maze):
                continue
            if self.perfect and not is_perfect(maze):
                continue
            if has_forbidden_open_area(maze):
                continue

            self.maze = maze
            return maze

        raise MazeGenerationError(
            "Could not generate a valid maze after many attempts"
        )

    def _depth_first_carve(self, maze: Maze, start: Cell) -> None:
        """Generate a perfect maze using iterative DFS."""
        stack = [start]
        start.visited = True

        while stack:
            current = stack[-1]
            choices = [
                (direction, neighbor)
                for direction, neighbor in maze.get_neighbors(current)
                if not neighbor.visited
            ]
            if not choices:
                stack.pop()
                continue
            direction, neighbor = self.random.choice(choices)
            maze.open_wall(current, direction)
            neighbor.visited = True
            stack.append(neighbor)

        maze.reset_visited()

    def _make_imperfect(self, maze: Maze) -> None:
        """Remove a few extra walls to create cycles."""
        candidates: list[tuple[Cell, str]] = []
        for cell in maze.carveable_cells():
            for direction in DIRECTIONS:
                neighbor = maze.get_neighbor(cell, direction)
                if neighbor is None or neighbor.blocked:
                    continue
                if cell.walls[direction]:
                    candidates.append((cell, direction))

        self.random.shuffle(candidates)
        target = max(1, len(maze.carveable_cells()) // 12)
        opened = 0
        for cell, direction in candidates:
            if opened >= target:
                break
            neighbor = maze.get_neighbor(cell, direction)
            if neighbor is None or neighbor.blocked:
                continue
            old_a = cell.walls[direction]
            opposite_index = (DIRECTIONS.index(direction) + 2) % 4
            opposite_direction = DIRECTIONS[opposite_index]
            old_b = neighbor.walls[opposite_direction]
            try:
                maze.open_wall(cell, direction)
            except ValueError:
                continue
            if has_forbidden_open_area(maze):
                cell.walls[direction] = old_a
                opposite = opposite_direction
                neighbor.walls[opposite] = old_b
            else:
                opened += 1
