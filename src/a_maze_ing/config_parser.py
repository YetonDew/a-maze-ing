"""Configuration parsing utilities moved into package."""

from __future__ import annotations

from pathlib import Path
from typing import Any

REQUIRED_KEYS = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}
OPTIONAL_KEYS = {"SEED", "DISPLAY", "COLOR"}
ALLOWED_KEYS = REQUIRED_KEYS | OPTIONAL_KEYS


class ConfigError(Exception):
    """Raised when the configuration file is invalid."""


def parse_coordinate(key: str, value: str) -> tuple[int, int]:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 2:
        raise ConfigError(f"{key} must contain exactly 2 integers separated by a comma")

    try:
        x, y = (int(part) for part in parts)
    except ValueError as exc:
        raise ConfigError(f"{key} must contain valid integers") from exc

    return x, y


def convert_value(key: str, value: str) -> Any:
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


def clean_line(line: str) -> str:
    return line.split("#", 1)[0].strip()


def parse_config(path: str) -> dict[str, Any]:
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

    # Basic validation
    width = converted_config["WIDTH"]
    height = converted_config["HEIGHT"]
    entry = converted_config["ENTRY"]
    exit_ = converted_config["EXIT"]
    output_file = converted_config["OUTPUT_FILE"]

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

    return converted_config
