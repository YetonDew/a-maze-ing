"""Export generated mazes to the subject file format."""

from pathlib import Path

from src.maze import HEX_BITS, Maze


def cell_to_hex(maze: Maze, x: int, y: int) -> str:
    """Encode one cell's closed walls as one hexadecimal digit."""
    cell = maze.get_cell(x, y)
    value = 0
    for direction, bit in HEX_BITS.items():
        if cell.walls[direction]:
            value |= bit
    return format(value, "X")


def export_maze(maze: Maze, path: str, solution: str) -> None:
    """Write the maze using the required hexadecimal wall representation."""
    output = Path(path)
    with output.open("w", encoding="utf-8") as file:
        for y in range(maze.height):
            row = "".join(cell_to_hex(maze, x, y) for x in range(maze.width))
            file.write(row + "\n")
        file.write("\n")
        file.write(f"{maze.entry[0]},{maze.entry[1]}\n")
        file.write(f"{maze.exit[0]},{maze.exit[1]}\n")
        file.write(solution + "\n")
