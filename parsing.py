from dataclasses import dataclass, field
import random
import json


@dataclass
class LevelConfig:
    width: int = 21
    height: int = 21
    level_max_time: float = 90
    seed: int | None = None


def default_levels() -> list[LevelConfig]:
    return [LevelConfig() for _ in range(10)]


@dataclass
class Config:
    highscore_filename: str = "highscores.json"
    lives: int = 3
    pacgum: int = 300
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    seed: int = 42
    levels: list[LevelConfig] = field(default_factory=default_levels)


def read_config_file(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def remove_comments(text: str) -> str:
    lines = text.splitlines()
    clean_lines = []
    for line in lines:
        index = line.find("#")
        if index != -1:
            line = line[:index]
        clean_lines.append(line)
    return "\n".join(clean_lines)


def resolve_seed(index: int, level_seed: int | None, default_seed: int) -> int:
    if level_seed is not None:
        return level_seed
    if index == 0:
        return default_seed
    return random.randint(1, 9999)


def get_valid_int(
        data: dict, key: str, default: int,
        min_value: int | None = None) -> int:

    value = data.get(key)
    if isinstance(value, int) and not isinstance(value, bool):
        if min_value is not None and value < min_value:
            return default
        return value
    return default


def get_seed_int(data: dict, key: str) -> int | None:
    value = data.get(key)

    if isinstance(value, int) and not isinstance(value, bool):
        return value

    return None


def parse_level(data: dict, index: int, default_seed: int) -> LevelConfig:
    if not isinstance(data, dict):
        data = {}

    width_value = get_valid_int(data, "width", 21, 1)
    height_value = get_valid_int(data, "height", 21, 1)
    level_max_time_value = get_valid_int(data, "level_max_time", 90, 1)

    level_seed = get_seed_int(data, "seed")
    seed_value = resolve_seed(index, level_seed, default_seed)

    return LevelConfig(
        width=width_value,
        height=height_value,
        level_max_time=level_max_time_value,
        seed=seed_value,
    )


def build_levels(
        raw_levels: list[dict], default_seed: int) -> list[LevelConfig]:

    levels: list[LevelConfig] = []
    index = 0
    total = max(10, len(raw_levels))
    while index < total:
        if index < len(raw_levels):
            levels.append(parse_level(raw_levels[index], index, default_seed))
        else:
            levels.append(parse_level({}, index, default_seed))
        index += 1

    return levels


def get_valid_str(data: dict, key: str, default: str) -> str:
    value = data.get(key)
    if isinstance(value, str) and value != "":
        return value
    return default


def build_config(data: dict) -> Config:
    highscore_file = get_valid_str(
        data, "highscore_filename", "highscores.json")
    lives_value = get_valid_int(data, "lives", 3, 1)
    pacgum_value = get_valid_int(data, "pacgum", 42, 1)
    points_per_pacgum = get_valid_int(data, "points_per_pacgum", 10, 1)
    points_per_super_pacgum = get_valid_int(
        data, "points_per_super_pacgum", 50, 1)
    points_per_ghost = get_valid_int(data, "points_per_ghost", 200, 1)
    seed = get_valid_int(data, "seed", 42)
    raw_levels = data.get("levels", [])
    if not isinstance(raw_levels, list):
        raw_levels = []
    levels = build_levels(raw_levels, seed)

    return Config(
        highscore_filename=highscore_file,
        lives=lives_value,
        pacgum=pacgum_value,
        points_per_pacgum=points_per_pacgum,
        points_per_super_pacgum=points_per_super_pacgum,
        points_per_ghost=points_per_ghost,
        seed=seed,
        levels=levels
    )


def load_config(path: str) -> Config:
    try:
        text = read_config_file(path)
    except FileNotFoundError:
        print("File not found.")
        return Config()
    except OSError:
        print("File access error.")
        return Config()

    clean_text = remove_comments(text)

    try:
        data = json.loads(clean_text)
    except json.JSONDecodeError:
        print("Invalid JSon.")
        return Config()

    if not isinstance(data, dict):
        print("Invalid configuration format.")
        return Config()

    return build_config(data)
