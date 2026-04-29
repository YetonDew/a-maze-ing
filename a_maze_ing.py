"""Command-line entry point for the A-Maze-ing project.

This CLI is intentionally thin: it loads configuration using the
`a_maze_ing.config` module and delegates generation to the package API.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Ensure the local `src` package directory is importable when running this
# script from the repository root.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from a_maze_ing.config_parser import ConfigError, parse_config
from a_maze_ing.generator import MazeGenerationError, MazeGenerator


def main(argv: list[str] | None = None) -> int:
    """Run the maze generator CLI."""

    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 1:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1

    try:
        config = parse_config(arguments[0])
        generator = MazeGenerator(
            width=config["WIDTH"],
            height=config["HEIGHT"],
            entry=config["ENTRY"],
            exit_=config["EXIT"],
            seed=config.get("SEED"),
            perfect=config["PERFECT"],
        )
        maze = generator.generate()
        output_path = Path(config["OUTPUT_FILE"])
        output_path.write_text(maze.to_output_text(), encoding="utf-8")

        if maze.pattern_warning is not None:
            print(f"Warning: {maze.pattern_warning}", file=sys.stderr)

        print(maze.render_ascii())
        return 0
    except (ConfigError, MazeGenerationError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
