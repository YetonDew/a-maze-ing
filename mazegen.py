"""Reusable maze generation module for A-Maze-ing."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from random import Random

Coordinate = tuple[int, int]
Direction = str

NORTH = "N"
EAST = "E"
SOUTH = "S"
WEST = "W"

WALL_BITS: dict[Direction, int] = {
    NORTH: 1,
    EAST: 2,
    SOUTH: 4,
    WEST: 8,
}

OFFSETS: dict[Direction, Coordinate] = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0),
}

OPPOSITE: dict[Direction, Direction] = {
    NORTH: SOUTH,
    EAST: WEST,
    SOUTH: NORTH,
    WEST: EAST,
}

PATTERN_BITMAP: tuple[str, ...] = (
    "#..#.####",
    "#..#....#",
    "#..#.####",
    "####.#...",
    "...#.#...",
    "...#.#...",
    "...#.####",
)


class MazeGenerationError(Exception):
    """Raised when maze generation cannot proceed."""


@dataclass(slots=True)
class MazeData:
    """Generated maze data and rendering helpers."""

    width: int
    height: int
    entry: Coordinate
    exit_: Coordinate
    walls: list[list[int]]
    solution: list[Coordinate]
    pattern_cells: set[Coordinate] = field(default_factory=set)
    pattern_warning: str | None = None

    def wall_digit(self, x: int, y: int) -> str:
        """Return the hexadecimal wall encoding for one cell."""

        return format(self.walls[y][x], "X")

    def solution_directions(self) -> list[str]:
        """Return the shortest path as cardinal directions."""

        directions: list[str] = []
        for current, nxt in zip(self.solution, self.solution[1:]):
            current_x, current_y = current
            next_x, next_y = nxt
            delta = (next_x - current_x, next_y - current_y)
            for direction, offset in OFFSETS.items():
                if delta == offset:
                    directions.append(direction)
                    break
        return directions

    def to_output_text(self) -> str:
        """Render the maze using the mandated file format."""

        rows = [
            "".join(self.wall_digit(x, y) for x in range(self.width))
            for y in range(self.height)
        ]
        path = "".join(self.solution_directions())
        return (
            "\n".join(
                [
                    *rows,
                    "",
                    f"{self.entry[0]},{self.entry[1]}",
                    f"{self.exit_[0]},{self.exit_[1]}",
                    path,
                ]
            )
            + "\n"
        )

    def render_ascii(self, show_path: bool = True) -> str:
        """Render the maze as terminal-friendly ASCII art."""

        canvas_height = self.height * 2 + 1
        canvas_width = self.width * 2 + 1
        canvas = [["#" for _ in range(canvas_width)] for _ in range(canvas_height)]
        path_cells = set(self.solution) if show_path else set()

        for y in range(self.height):
            for x in range(self.width):
                center_y = y * 2 + 1
                center_x = x * 2 + 1

                if (x, y) in self.pattern_cells:
                    canvas[center_y][center_x] = "█"
                elif (x, y) in path_cells:
                    canvas[center_y][center_x] = "."
                else:
                    canvas[center_y][center_x] = " "

                walls = self.walls[y][x]
                if walls & WALL_BITS[NORTH] == 0:
                    canvas[center_y - 1][center_x] = " "
                if walls & WALL_BITS[EAST] == 0:
                    canvas[center_y][center_x + 1] = " "
                if walls & WALL_BITS[SOUTH] == 0:
                    canvas[center_y + 1][center_x] = " "
                if walls & WALL_BITS[WEST] == 0:
                    canvas[center_y][center_x - 1] = " "

        entry_x, entry_y = self.entry
        exit_x, exit_y = self.exit_
        canvas[entry_y * 2 + 1][entry_x * 2 + 1] = "S"
        canvas[exit_y * 2 + 1][exit_x * 2 + 1] = "E"

        return "\n".join("".join(row) for row in canvas)


class MazeGenerator:
    """Generate maze structures that can be reused in later projects."""

    pattern_width = len(PATTERN_BITMAP[0])
    pattern_height = len(PATTERN_BITMAP)

    def __init__(
        self,
        width: int,
        height: int,
        entry: Coordinate,
        exit_: Coordinate,
        *,
        seed: int | None = None,
        perfect: bool = True,
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_ = exit_
        self.perfect = perfect
        self.random = Random(seed)

    def generate(self) -> MazeData:
        """Build a maze and return all data needed by the CLI."""

        self._validate_geometry()
        pattern_cells, pattern_warning = self._build_pattern_cells()

        if self.entry in pattern_cells or self.exit_ in pattern_cells:
            raise MazeGenerationError("Entry or exit overlaps the reserved 42 pattern")

        accessible = {
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in pattern_cells
        }
        if self.entry not in accessible or self.exit_ not in accessible:
            raise MazeGenerationError("Entry and exit must be inside the maze")

        walls = [[15 for _ in range(self.width)] for _ in range(self.height)]
        self._carve_depth_first(walls, accessible)
        solution = self._solve(walls, pattern_cells)

        return MazeData(
            width=self.width,
            height=self.height,
            entry=self.entry,
            exit_=self.exit_,
            walls=walls,
            solution=solution,
            pattern_cells=pattern_cells,
            pattern_warning=pattern_warning,
        )

    def _validate_geometry(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise MazeGenerationError("Maze dimensions must be positive")

        entry_x, entry_y = self.entry
        exit_x, exit_y = self.exit_

        if not (0 <= entry_x < self.width and 0 <= entry_y < self.height):
            raise MazeGenerationError("Entry is outside the maze bounds")
        if not (0 <= exit_x < self.width and 0 <= exit_y < self.height):
            raise MazeGenerationError("Exit is outside the maze bounds")
        if self.entry == self.exit_:
            raise MazeGenerationError("Entry and exit must be different")

    def _build_pattern_cells(self) -> tuple[set[Coordinate], str | None]:
        if self.width < self.pattern_width + 2 or self.height < self.pattern_height + 2:
            return set(), "Maze too small for the 42 pattern; generating without it"

        for origin_x, origin_y in self._pattern_candidates():
            cells = {
                (origin_x + x, origin_y + y)
                for y, row in enumerate(PATTERN_BITMAP)
                for x, pixel in enumerate(row)
                if pixel == "#"
            }
            if self.entry in cells or self.exit_ in cells:
                continue
            return cells, None

        return set(), "Maze has no room for a non-overlapping 42 pattern"

    def _pattern_candidates(self) -> list[Coordinate]:
        positions = [
            (1, 1),
            (self.width - self.pattern_width - 1, 1),
            (1, self.height - self.pattern_height - 1),
            (
                self.width - self.pattern_width - 1,
                self.height - self.pattern_height - 1,
            ),
            (
                max(1, (self.width - self.pattern_width) // 2),
                max(1, (self.height - self.pattern_height) // 2),
            ),
        ]
        unique_positions: list[Coordinate] = []
        seen: set[Coordinate] = set()
        for origin_x, origin_y in positions:
            if origin_x < 1 or origin_y < 1:
                continue
            if origin_x + self.pattern_width >= self.width:
                continue
            if origin_y + self.pattern_height >= self.height:
                continue
            origin = (origin_x, origin_y)
            if origin in seen:
                continue
            seen.add(origin)
            unique_positions.append(origin)
        self.random.shuffle(unique_positions)
        return unique_positions

    def _carve_depth_first(
        self,
        walls: list[list[int]],
        accessible: set[Coordinate],
    ) -> None:
        stack: list[Coordinate] = [self.entry]
        visited = {self.entry}

        while stack:
            current_x, current_y = stack[-1]
            neighbors = [
                neighbor
                for neighbor in self._accessible_neighbors(
                    current_x, current_y, accessible
                )
                if (neighbor[0], neighbor[1]) not in visited
            ]

            if not neighbors:
                stack.pop()
                continue

            next_x, next_y, direction = self.random.choice(neighbors)
            self._open_wall(walls, current_x, current_y, next_x, next_y, direction)
            visited.add((next_x, next_y))
            stack.append((next_x, next_y))

        if visited != accessible:
            missing = len(accessible - visited)
            raise MazeGenerationError(
                f"Maze generation failed to reach {missing} accessible cell(s)"
            )

    def _solve(
        self,
        walls: list[list[int]],
        pattern_cells: set[Coordinate],
    ) -> list[Coordinate]:
        queue: deque[Coordinate] = deque([self.entry])
        parents: dict[Coordinate, Coordinate | None] = {self.entry: None}

        while queue:
            current_x, current_y = queue.popleft()
            if (current_x, current_y) == self.exit_:
                break

            for next_x, next_y in self._reachable_neighbors(
                walls,
                current_x,
                current_y,
                pattern_cells,
            ):
                next_cell = (next_x, next_y)
                if next_cell in parents:
                    continue
                parents[next_cell] = (current_x, current_y)
                queue.append(next_cell)

        if self.exit_ not in parents:
            raise MazeGenerationError("No valid path between entry and exit")

        path: list[Coordinate] = []
        cursor: Coordinate | None = self.exit_
        while cursor is not None:
            path.append(cursor)
            cursor = parents[cursor]

        path.reverse()
        return path

    def _reachable_neighbors(
        self,
        walls: list[list[int]],
        x: int,
        y: int,
        pattern_cells: set[Coordinate],
    ) -> list[Coordinate]:
        neighbors: list[Coordinate] = []
        for direction, (offset_x, offset_y) in OFFSETS.items():
            if walls[y][x] & WALL_BITS[direction] != 0:
                continue

            neighbor_x = x + offset_x
            neighbor_y = y + offset_y
            if not self._in_bounds(neighbor_x, neighbor_y):
                continue
            if (neighbor_x, neighbor_y) in pattern_cells:
                continue
            neighbors.append((neighbor_x, neighbor_y))
        return neighbors

    def _accessible_neighbors(
        self,
        x: int,
        y: int,
        accessible: set[Coordinate],
    ) -> list[tuple[int, int, Direction]]:
        neighbors: list[tuple[int, int, Direction]] = []
        for direction, (offset_x, offset_y) in OFFSETS.items():
            neighbor_x = x + offset_x
            neighbor_y = y + offset_y
            if not self._in_bounds(neighbor_x, neighbor_y):
                continue
            if (neighbor_x, neighbor_y) not in accessible:
                continue
            neighbors.append((neighbor_x, neighbor_y, direction))
        return neighbors

    def _open_wall(
        self,
        walls: list[list[int]],
        x: int,
        y: int,
        neighbor_x: int,
        neighbor_y: int,
        direction: Direction,
    ) -> None:
        walls[y][x] &= ~WALL_BITS[direction]
        walls[neighbor_y][neighbor_x] &= ~WALL_BITS[OPPOSITE[direction]]

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height
