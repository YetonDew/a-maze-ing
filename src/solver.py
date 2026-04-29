"""Shortest-path solver for mazes."""

from collections import deque

from src.maze import PATH_LETTERS, Maze, Cell


class MazeSolveError(Exception):
    """Raised when no path can be found."""


def shortest_path(maze: Maze) -> str:
    """Return the shortest path from entry to exit as N/E/S/W letters."""
    start = maze.get_cell(*maze.entry)
    goal = maze.get_cell(*maze.exit)
    queue: deque[Cell] = deque([start])
    parents: dict[tuple[int, int], tuple[tuple[int, int], str] | None] = {
        (start.x, start.y): None,
    }

    while queue:
        cell = queue.popleft()
        if cell is goal:
            break
        for direction, neighbor in maze.accessible_neighbors(cell):
            coord = (neighbor.x, neighbor.y)
            if coord in parents:
                continue
            parents[coord] = ((cell.x, cell.y), PATH_LETTERS[direction])
            queue.append(neighbor)

    goal_coord = (goal.x, goal.y)
    if goal_coord not in parents:
        raise MazeSolveError("No valid path from entry to exit")

    steps: list[str] = []
    current = goal_coord
    while True:
        parent = parents[current]
        if parent is None:
            break

        previous, letter = parent
        steps.append(letter)
        current = previous
    steps.reverse()
    return "".join(steps)
