"""Main command-line entry point for A-Maze-ing."""

import sys
from typing import Any

from src.config_parser import ConfigError, parse_config
from src.exporter import export_maze
from src.generator import MazeGenerationError, MazeGenerator
from src.renderer import COLORS, print_maze
from src.solver import MazeSolveError, shortest_path
from src.validator import MazeValidationError, validate_maze


def build_generator(
    config: dict[str, Any],
) -> MazeGenerator:
    """Create a MazeGenerator from parsed configuration."""
    return MazeGenerator(
        width=config["WIDTH"],
        height=config["HEIGHT"],
        entry=config["ENTRY"],
        exit_cell=config["EXIT"],
        perfect=config["PERFECT"],
        seed=config.get("SEED"),
    )


def generate_export_and_display(
    config: dict[str, Any],
) -> tuple[MazeGenerator, str]:
    """Generate, validate, export, and display one maze."""
    generator = build_generator(config)
    maze = generator.generate()
    validate_maze(maze, config["PERFECT"])
    solution = shortest_path(maze)
    export_maze(maze, config["OUTPUT_FILE"], solution)
    print(f"Maze exported to {config['OUTPUT_FILE']}")
    print_maze(maze, solution, show_path=False)
    return generator, solution


def interactive_loop(
    config: dict[str, Any],
    generator: MazeGenerator,
    solution: str,
) -> None:
    """Handle simple terminal interactions."""
    show_path = False
    wall_color = "default"
    current_generator = generator
    current_solution = solution

    while True:
        print("\nOptions: [p]ath  [r]egenerate  [c]olor  [q]uit")
        choice = input("> ").strip().lower()
        if choice == "q":
            return
        if choice == "p":
            show_path = not show_path
            if current_generator.maze is not None:
                print_maze(
                    current_generator.maze,
                    current_solution,
                    show_path,
                    wall_color,
                )
        elif choice == "r":
            seed = config.get("SEED")
            if seed is not None:
                config["SEED"] = int(seed) + 1
            current_generator, current_solution = generate_export_and_display(
                config,
            )
            show_path = False
        elif choice == "c":
            names = ", ".join(COLORS.keys())
            wall_color = input(f"Color ({names}): ").strip().lower()
            if wall_color not in COLORS:
                print("Unknown color, using default")
                wall_color = "default"
            if current_generator.maze is not None:
                print_maze(
                    current_generator.maze,
                    current_solution,
                    show_path,
                    wall_color,
                )
        else:
            print("Unknown option")


def main(argv: list[str]) -> int:
    """Run the program."""
    if len(argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return 1

    try:
        config = parse_config(argv[1])
        generator, solution = generate_export_and_display(config)
        interactive_loop(config, generator, solution)
        return 0
    except (
        ConfigError,
        MazeGenerationError,
        MazeValidationError,
        MazeSolveError,
        OSError,
    ) as exc:
        print(f"Error: {exc}")
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
