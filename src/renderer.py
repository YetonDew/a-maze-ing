"""Terminal ASCII renderer for mazes."""

from src.maze import Maze

RESET = "\033[0m"
COLORS = {
    "default": "",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
}


def render_maze(
    maze: Maze,
    solution: str = "",
    show_path: bool = False,
    wall_color: str = "default",
) -> str:
    """Return an ASCII representation of the maze."""
    path_cells = _solution_cells(maze, solution) if show_path else set()
    color = COLORS.get(wall_color, "")
    reset = RESET if color else ""

    lines: list[str] = []
    top_line = (
        color
        + "+"
        + "+".join("---" for _ in range(maze.width))
        + "+"
        + reset
    )
    lines.append(top_line)

    for y in range(maze.height):
        body = color + "|" + reset
        bottom = color + "+" + reset
        for x in range(maze.width):
            cell = maze.get_cell(x, y)
            coord = (x, y)
            if cell.blocked:
                content = "###"
            elif coord == maze.entry:
                content = " E "
            elif coord == maze.exit:
                content = " X "
            elif coord in path_cells:
                content = " . "
            else:
                content = "   "

            right_wall = color + "|" + reset if cell.walls["RIGHT"] else " "
            bot_wall = color + "---" + reset if cell.walls["BOT"] else "   "
            body += content + right_wall
            bottom += bot_wall + color + "+" + reset
        lines.append(body)
        lines.append(bottom)
    return "\n".join(lines)


def print_maze(
    maze: Maze,
    solution: str = "",
    show_path: bool = False,
    wall_color: str = "default",
) -> None:
    """Print an ASCII maze to the terminal."""
    print(render_maze(maze, solution, show_path, wall_color))


def _solution_cells(maze: Maze, solution: str) -> set[tuple[int, int]]:
    """Convert a solution string into the set of cells on the path."""
    x, y = maze.entry
    cells = {(x, y)}
    moves = {
        "N": (0, -1),
        "E": (1, 0),
        "S": (0, 1),
        "W": (-1, 0),
    }
    for step in solution:
        dx, dy = moves[step]
        x += dx
        y += dy
        if maze.in_bounds(x, y):
            cells.add((x, y))
    return cells
