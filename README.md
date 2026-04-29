_This project has been created as part of the 42 curriculum by YetonDew._

# A-Maze-ing

## Description

A-Maze-ing is a Python maze generator that reads a configuration file, builds a maze, writes the hexadecimal wall representation to an output file, and renders the maze in the terminal.

The reusable generation logic lives in the root-level [mazegen.py](mazegen.py) module, which exposes a `MazeGenerator` class and returns a maze object containing the wall grid, the solution path, and ASCII rendering helpers.

## Instructions

Run the project with:

```bash
python3 a_maze_ing.py config.txt
```

The sample configuration shipped with the repository is [config.txt](config.txt). It defines the maze size, the entry and exit, the output file name, whether the maze should be perfect, and an optional seed for reproducibility.

Useful Makefile targets:

```bash
make install
make run
make debug
make clean
make lint
make lint-strict
```

## Configuration

Each non-comment line must contain one `KEY=VALUE` pair.

Mandatory keys:

```text
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
```

Optional keys:

```text
SEED=42
```

Comments start with `#` and are ignored. Coordinates are zero-based.

## Maze Generation Algorithm

The base generator uses a randomized depth-first search backtracker to build a spanning tree over the accessible cells. That gives a perfect maze by default, with one unique path between any two reachable cells. The generator also reserves a small closed-cell 42 pattern when the maze is large enough.

I chose this algorithm because it is simple to reason about, easy to validate, and well suited to reproducible generation with a seed.

## Reusable Module

The reusable part is the [mazegen.py](mazegen.py) module.

Basic example:

```python
from mazegen import MazeGenerator

generator = MazeGenerator(20, 10, (0, 0), (19, 9), seed=42, perfect=True)
maze = generator.generate()

print(maze.render_ascii())
print(maze.to_output_text())
```

Custom parameters:

```python
MazeGenerator(width, height, entry, exit_, seed=123, perfect=False)
```

Access the generated structure through the returned `MazeData` object:

```python
maze.walls
maze.solution
maze.render_ascii(show_path=False)
```

## Resources

Classic references used while building the project:

- Depth-first search maze generation
- Graph theory and spanning trees
- Python `pathlib`, `dataclasses`, `random`, and `collections` documentation

AI was used to help structure the project, trim the split modules into a single reusable generator, and check the config and output-file workflow. The final implementation was written and adjusted manually after review.

## Team And Project Management

This repository was developed solo.

Role: implementation, validation, and documentation.

Planning: start with the config parser and output format, then implement the reusable maze generator, then wire the CLI and documentation. That plan stayed stable because the project scope was compact.

What worked well: keeping the generator reusable from the beginning and validating the output format early.

What could be improved: adding an optional graphical renderer later if the project is extended.

Tools used: Python, the local virtual environment, `make`, and AI-assisted code review support.
