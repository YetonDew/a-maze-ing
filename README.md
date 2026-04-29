_This project has been created as part of the 42 curriculum by ajeffers, msakalin._

# A-Maze-ing

## Description

A-Maze-ing is a Python 3.10+ maze generator. It reads a configuration file, generates a valid maze, exports the maze in the required hexadecimal wall format, and displays it in the terminal using ASCII rendering.

The current implementation uses randomized depth-first search. With `PERFECT=True`, the generated maze is a spanning tree over the non-blocked cells, so there is exactly one path between reachable cells. With `PERFECT=False`, the program opens extra walls after generation to create cycles.

The visual maze also tries to place a visible `42` pattern using fully closed cells. If the maze is too small, the program prints a warning and continues.

## Instructions

Install dependencies:

```sh
make install
```

Run the project:

```sh
make run
```

Or directly:

```sh
python3 a_maze_ing.py config.txt
```

Clean generated files:

```sh
make clean
```

Run linting:

```sh
make lint
```

Build the reusable package:

```sh
make build
```

## Configuration file

The config file must contain one `KEY=VALUE` pair per line. Empty lines and comments starting with `#` are ignored.

Mandatory keys:

```txt
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
```

Optional keys:

```txt
SEED=42
ALGORITHM=dfs
DISPLAY=ascii
```

Meaning:

- `WIDTH`: maze width in cells.
- `HEIGHT`: maze height in cells.
- `ENTRY`: entry coordinate as `x,y`.
- `EXIT`: exit coordinate as `x,y`.
- `OUTPUT_FILE`: destination file for the hexadecimal maze output.
- `PERFECT`: `True` for a perfect maze, `False` for an imperfect maze.
- `SEED`: reproducible random seed.
- `ALGORITHM`: currently only `dfs`.
- `DISPLAY`: currently `ascii`.

## Output format

Each cell is exported as one hexadecimal digit. Closed walls are encoded using bits:

- bit 0: North / top
- bit 1: East / right
- bit 2: South / bottom
- bit 3: West / left

Rows are written line by line. After an empty line, the file contains the entry coordinate, exit coordinate, and shortest path using `N`, `E`, `S`, and `W`.

## Algorithm choice

We chose randomized depth-first search because it is simple to explain, easy to debug, and naturally creates a perfect maze. It also works well with seed-based reproducibility.

## Reusable code

The reusable class is `MazeGenerator` in `src/generator.py`.

Basic usage:

```python
from src.generator import MazeGenerator
from src.solver import shortest_path

generator = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit_cell=(19, 14),
    perfect=True,
    seed=42,
)
maze = generator.generate()
solution = shortest_path(maze)
print(solution)
```

The generated `Maze` object gives access to:

- `maze.grid`
- `maze.get_cell(x, y)`
- `maze.accessible_neighbors(cell)`
- `maze.entry`
- `maze.exit`

## Project structure

```txt
a_maze_ing.py          main program
config.txt             default configuration
src/config_parser.py   config parser and config validation
src/maze.py            Cell and Maze core structures
src/pattern.py         42 pattern placement
src/generator.py       reusable MazeGenerator class
src/validator.py       maze validation helpers
src/solver.py          shortest path solver
src/exporter.py        output file exporter
src/renderer.py        ASCII renderer
Makefile               install/run/debug/clean/lint/build rules
pyproject.toml         package build metadata
```

## Team and project management

splited roles:

- ajeffers: parser, maze model, generator, seed support.
- msakalin: validator, solver, exporter, renderer, README and packaging.

What worked well:

- Separating generation, validation, solving, exporting, and rendering.
- Keeping wall synchronization inside the `Maze` class.

What could be improved:

- Add more generation algorithms.
- Add graphical MLX rendering.
- Improve the placement strategy for the `42` pattern.

Tools used:

- Python 3.10+
- flake8
- mypy
- setuptools/build
- AI assistance for planning and explanation

## Resources

- Python documentation: https://docs.python.org/3/
- `dataclasses`: https://docs.python.org/3/library/dataclasses.html
- `random`: https://docs.python.org/3/library/random.html
- Graph traversal concepts: DFS and BFS
- Maze generation concepts: recursive backtracker / randomized DFS
