"""Command-line entry point for the A-Maze-ing project."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from mazegen import MazeGenerationError, MazeGenerator


class ConfigError(Exception):
    """Raised when the configuration file is invalid."""


REQUIRED_KEYS = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}
OPTIONAL_KEYS = {"SEED"}
ALLOWED_KEYS = REQUIRED_KEYS | OPTIONAL_KEYS


def clean_line(line: str) -> str:
    """Strip comments and surrounding whitespace from one line."""

    return line.split("#", 1)[0].strip()


def parse_coordinate(key: str, value: str) -> tuple[int, int]:
    """Parse a coordinate pair from the configuration file."""

    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 2:
        raise ConfigError(f"{key} must contain exactly 2 integers separated by a comma")

    try:
        x, y = (int(part) for part in parts)
    except ValueError as exc:
        raise ConfigError(f"{key} must contain valid integers") from exc

    return x, y


def convert_value(key: str, value: str) -> Any:
    """Convert a raw string value to the expected Python type."""

    if key in {"ENTRY", "EXIT"}:
        return parse_coordinate(key, value)

    if key == "PERFECT":
        lowered = value.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        raise ConfigError("PERFECT must be True or False")

    if key in {"WIDTH", "HEIGHT", "SEED"}:
        try:
            return int(value)
        except ValueError as exc:
            raise ConfigError(f"{key} must be an integer") from exc

    return value.strip()


def parse_config(path: str) -> dict[str, Any]:
    """Parse and validate the maze configuration file."""

    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {path}")
    if not config_path.is_file():
        raise ConfigError(f"Not a valid file: {path}")

    raw_config: dict[str, str] = {}

    try:
        with config_path.open("r", encoding="utf-8") as config_file:
            for line_number, raw_line in enumerate(config_file, start=1):
                line = clean_line(raw_line)
                if not line:
                    continue

                if "=" not in line:
                    raise ConfigError(f"Line {line_number}: missing '='")

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                if not key:
                    raise ConfigError(f"Line {line_number}: empty key")
                if not value:
                    raise ConfigError(f"Line {line_number}: empty value")
                if key not in ALLOWED_KEYS:
                    raise ConfigError(f"Line {line_number}: unknown key '{key}'")
                if key in raw_config:
                    raise ConfigError(f"Line {line_number}: duplicate key '{key}'")

                raw_config[key] = value
    except OSError as exc:
        raise ConfigError(f"Could not read config file: {path}") from exc

    missing_keys = REQUIRED_KEYS - raw_config.keys()
    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise ConfigError(f"Missing required key(s): {missing}")

    converted_config = {
        key: convert_value(key, value) for key, value in raw_config.items()
    }
    validate_config(converted_config)
    return converted_config


def validate_config(config: dict[str, Any]) -> None:
    """Validate the converted configuration values."""

    width = config["WIDTH"]
    height = config["HEIGHT"]
    entry = config["ENTRY"]
    exit_ = config["EXIT"]
    output_file = config["OUTPUT_FILE"]

    if width <= 0:
        raise ConfigError("WIDTH must be greater than 0")
    if height <= 0:
        raise ConfigError("HEIGHT must be greater than 0")

    entry_x, entry_y = entry
    exit_x, exit_y = exit_

    if not (0 <= entry_x < width and 0 <= entry_y < height):
        raise ConfigError("ENTRY must be inside maze bounds")
    if not (0 <= exit_x < width and 0 <= exit_y < height):
        raise ConfigError("EXIT must be inside maze bounds")
    if entry == exit_:
        raise ConfigError("ENTRY and EXIT must be different")
    if not isinstance(output_file, str) or not output_file.strip():
        raise ConfigError("OUTPUT_FILE must be a non-empty string")


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
