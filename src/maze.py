"""Core maze data structures."""

from dataclasses import dataclass, field

TOP = "TOP"
RIGHT = "RIGHT"
BOT = "BOT"
LEFT = "LEFT"

DIRECTIONS = (TOP, RIGHT, BOT, LEFT)

OFFSETS: dict[str, tuple[int, int]] = {
    TOP: (0, -1),
    RIGHT: (1, 0),
    BOT: (0, 1),
    LEFT: (-1, 0),
}

OPPOSITE: dict[str, str] = {
    TOP: BOT,
    RIGHT: LEFT,
    BOT: TOP,
    LEFT: RIGHT,
}

PATH_LETTERS: dict[str, str] = {
    TOP: "N",
    RIGHT: "E",
    BOT: "S",
    LEFT: "W",
}

HEX_BITS: dict[str, int] = {
    TOP: 1,
    RIGHT: 2,
    BOT: 4,
    LEFT: 8,
}


@dataclass
class Cell:
    """Represent one cell of the maze."""

    x: int
    y: int
    walls: dict[str, bool] = field(
        default_factory=lambda: {
            TOP: True,
            RIGHT: True,
            BOT: True,
            LEFT: True,
        }
    )
    visited: bool = False
    blocked: bool = False

    def is_closed(self) -> bool:
        """Return True if all four walls are closed."""
        return all(self.walls.values())


class Maze:
    """Represent a maze as a two-dimensional grid of cells."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_cell: tuple[int, int],
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit_cell
        self.grid: list[list[Cell]] = [
            [Cell(x, y) for x in range(width)] for y in range(height)
        ]

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if coordinates are inside the maze."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_cell(self, x: int, y: int) -> Cell:
        """Return the cell at coordinates x,y."""
        if not self.in_bounds(x, y):
            raise ValueError(f"Cell ({x}, {y}) is out of bounds")
        return self.grid[y][x]

    def cells(self) -> list[Cell]:
        """Return every cell as a flat list."""
        return [cell for row in self.grid for cell in row]

    def carveable_cells(self) -> list[Cell]:
        """Return cells that are not part of the closed 42 pattern."""
        return [cell for cell in self.cells() if not cell.blocked]

    def get_neighbor(self, cell: Cell, direction: str) -> Cell | None:
        """Return a neighboring cell in one direction, or None at borders."""
        dx, dy = OFFSETS[direction]
        nx = cell.x + dx
        ny = cell.y + dy
        if not self.in_bounds(nx, ny):
            return None
        return self.get_cell(nx, ny)

    def get_neighbors(
        self,
        cell: Cell,
        include_blocked: bool = False,
    ) -> list[tuple[str, Cell]]:
        """Return valid neighbors with their direction."""
        neighbors: list[tuple[str, Cell]] = []
        for direction in DIRECTIONS:
            neighbor = self.get_neighbor(cell, direction)
            if neighbor is None:
                continue
            if neighbor.blocked and not include_blocked:
                continue
            neighbors.append((direction, neighbor))
        return neighbors

    def open_wall(self, cell: Cell, direction: str) -> None:
        """Open a wall and its opposite wall in the neighbor."""
        neighbor = self.get_neighbor(cell, direction)
        if neighbor is None:
            raise ValueError(f"No neighbor in direction {direction}")
        if cell.blocked or neighbor.blocked:
            raise ValueError("Cannot open a wall connected to a blocked cell")
        cell.walls[direction] = False
        neighbor.walls[OPPOSITE[direction]] = False

    def accessible_neighbors(self, cell: Cell) -> list[tuple[str, Cell]]:
        """Return neighbors reachable through open walls."""
        result: list[tuple[str, Cell]] = []
        for direction, neighbor in self.get_neighbors(cell):
            if not cell.walls[direction]:
                result.append((direction, neighbor))
        return result

    def reset_visited(self) -> None:
        """Clear temporary visited flags."""
        for cell in self.cells():
            cell.visited = False

    def mark_blocked(self, x: int, y: int) -> None:
        """Mark a cell as blocked and keep it fully closed."""
        cell = self.get_cell(x, y)
        cell.blocked = True
        cell.walls = {direction: True for direction in DIRECTIONS}
