from dataclasses import dataclass, field

TOP = "TOP"
RIGHT = "RIGHT"
BOT = "BOT"
LEFT = "LEFT"

DIRECTIONS = (TOP, RIGHT, BOT, LEFT)

OFFSETS = {
    TOP: (0, -1),
    RIGHT: (1, 0),
    BOT: (0, 1),
    LEFT: (-1, 0),
}

OPPOSITE = {
    TOP: BOT,
    RIGHT: LEFT,
    BOT: TOP,
    LEFT: RIGHT,
}


@dataclass
class Cell:
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


class Maze:
    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_: tuple[int, int],
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit_
        self.grid = [[Cell(x, y) for x in range(width)] for y in range(height)]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get_cell(self, x: int, y: int) -> Cell:
        if not self.in_bounds(x, y):
            raise ValueError(f"Cell ({x}, {y}) is out of bounds")
        return self.grid[y][x]

    def get_neighbor(self, cell: Cell, direction: str) -> Cell | None:
        dx, dy = OFFSETS[direction]
        nx = cell.x + dx
        ny = cell.y + dy

        if not self.in_bounds(nx, ny):
            return None
        return self.get_cell(nx, ny)

    def get_neighbors(self, cell: Cell) -> list[tuple[str, Cell]]:
        neighbors = []
        for direction in DIRECTIONS:
            neighbor = self.get_neighbor(cell, direction)
            if neighbor is not None:
                neighbors.append((direction, neighbor))
        return neighbors

    def open_wall(self, cell: Cell, direction: str) -> None:
        neighbor = self.get_neighbor(cell, direction)
        if neighbor is None:
            raise ValueError(f"No neighbor in direction {direction}")

        cell.walls[direction] = False
        neighbor.walls[OPPOSITE[direction]] = False
