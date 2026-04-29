"""Configuration parser for the A-Maze-ing project."""

from pathlib import Path
from typing import Any

REQUIRED_KEYS = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}
OPTIONAL_KEYS = {"SEED", "ALGORITHM", "DISPLAY"}
ALLOWED_KEYS = REQUIRED_KEYS | OPTIONAL_KEYS


class ConfigError(Exception):
    """Raised when the configuration file is invalid."""


def _parse_coordinate(key: str, value: str) -> tuple[int, int]:
    """Parse a coordinate written as x,y."""
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 2:
        raise ConfigError(f"{key} must contain exactly two integers: x,y")
    try:
        x, y = (int(part) for part in parts)
    except ValueError as exc:
        raise ConfigError(f"{key} must contain valid integers") from exc
    return x, y


def _parse_bool(key: str, value: str) -> bool:
    """Parse a boolean value."""
    lowered = value.strip().lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise ConfigError(f"{key} must be True or False")


def _convert_value(key: str, value: str) -> Any:
    """Convert one raw configuration value to its Python type."""
    if key in {"ENTRY", "EXIT"}:
        return _parse_coordinate(key, value)
    if key == "PERFECT":
        return _parse_bool(key, value)
    if key in {"WIDTH", "HEIGHT", "SEED"}:
        try:
            return int(value)
        except ValueError as exc:
            raise ConfigError(f"{key} must be an integer") from exc
    return value.strip()


def _clean_line(line: str) -> str:
    """Remove inline comments and surrounding whitespace."""
    return line.split("#", 1)[0].strip()


def parse_config(path: str) -> dict[str, Any]:
    """Parse and validate a configuration file.

    Args:
        path: Path to the configuration file.

    Returns:
        A dictionary containing typed configuration values.

    Raises:
        ConfigError: If the file cannot be read or contains invalid data.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {path}")
    if not config_path.is_file():
        raise ConfigError(f"Not a regular file: {path}")

    raw_config: dict[str, str] = {}
    try:
        with config_path.open("r", encoding="utf-8") as config_file:
            for line_number, raw_line in enumerate(config_file, start=1):
                line = _clean_line(raw_line)
                if not line:
                    continue
                if "=" not in line:
                    raise ConfigError(f"Line {line_number}: missing '='")
                key, value = line.split("=", 1)
                key = key.strip().upper()
                value = value.strip()
                if not key:
                    raise ConfigError(f"Line {line_number}: empty key")
                if not value:
                    raise ConfigError(f"Line {line_number}: empty value")
                if key not in ALLOWED_KEYS:
                    raise ConfigError(
                        f"Line {line_number}: unknown key '{key}'"
                    )
                if key in raw_config:
                    raise ConfigError(
                        f"Line {line_number}: duplicate key '{key}'"
                    )
                raw_config[key] = value
    except OSError as exc:
        raise ConfigError(f"Could not read config file: {path}") from exc

    missing = REQUIRED_KEYS - raw_config.keys()
    if missing:
        raise ConfigError("Missing required key(s): "
                          + ", ".join(sorted(missing)))

    config = {key: _convert_value(key, value) for key,
              value in raw_config.items()}
    _validate_config(config)
    return config


def _validate_config(config: dict[str, Any]) -> None:
    """Validate typed configuration values."""
    width = config["WIDTH"]
    height = config["HEIGHT"]
    entry = config["ENTRY"]
    exit_cell = config["EXIT"]

    if width <= 0:
        raise ConfigError("WIDTH must be greater than 0")
    if height <= 0:
        raise ConfigError("HEIGHT must be greater than 0")
    if entry == exit_cell:
        raise ConfigError("ENTRY and EXIT must be different")

    entry_x, entry_y = entry
    exit_x, exit_y = exit_cell
    if not (0 <= entry_x < width and 0 <= entry_y < height):
        raise ConfigError("ENTRY must be inside maze bounds")
    if not (0 <= exit_x < width and 0 <= exit_y < height):
        raise ConfigError("EXIT must be inside maze bounds")

    if "SEED" in config and config["SEED"] < 0:
        raise ConfigError("SEED must be greater than or equal to 0")
    if "ALGORITHM" in config and str(config["ALGORITHM"]).lower() != "dfs":
        raise ConfigError("Only ALGORITHM=dfs is currently supported")
