"""
game/config.py
==============
Configuration file parser for the Pac-Man game.

Supports standard JSON plus single-line comments starting with '#'.
All keys have robust defaults so the game never crashes on a missing field.

Usage:
    config = GameConfig.load("config.json")
    print(config.lives)          # 3
    print(config.levels[0])      # LevelConfig(width=21, height=21, time_limit=90)
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class LevelConfig:
    """Settings for a single level."""
    width: int = 21
    height: int = 21
    time_limit: int = 90          # seconds; 0 = no limit
    ghost_speed_factor: float = 1.0  # multiplier applied to base ghost speed


@dataclass
class GameConfig:
    """
    Full game configuration loaded from a JSON file.

    Attributes
    ----------
    highscore_filename : str
        Path where the highscore JSON is stored.
    lives : int
        Starting number of lives (default 3).
    pacgum : int
        Number of regular pacgums per level (if maze generation uses it).
    points_per_pacgum : int
        Score awarded per pacgum eaten.
    points_per_super_pacgum : int
        Score awarded per super-pacgum eaten.
    points_per_ghost : int
        Base score for first ghost eaten during a power-up window.
        Subsequent ghosts award 2×, 4×, 8× this value.
    frightened_duration : float
        How long (seconds) ghosts stay frightened after a super-pacgum.
    ghost_respawn_delay : float
        How long (seconds) before an eaten ghost respawns at its corner.
    player_speed : float
        Tile-widths per second for the player.
    ghost_base_speed : float
        Tile-widths per second for ghosts in CHASE/SCATTER mode.
    frightened_speed_factor : float
        Speed multiplier for ghosts while frightened (< 1.0 to slow down).
    levels : list[Lev as a set of (col, row) positions matching the maze
The interface is designed so your UI/game loop stays fully in control — you call player.movelConfig]
        Ordered list of level configurations.
    """

    highscore_filename: str = "highscores.json"
    lives: int = 3
    pacgum: int = 42
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    frightened_duration: float = 7.0
    ghost_respawn_delay: float = 5.0
    player_speed: float = 5.0
    ghost_base_speed: float = 4.0
    frightened_speed_factor: float = 0.5
    levels: list[LevelConfig] = field(default_factory=lambda: [LevelConfig() for _ in range(10)])

    # ------------------------------------------------------------------
    # Class methods
    # ------------------------------------------------------------------

    @classmethod
    def load(cls, filepath: str) -> "GameConfig":
        """
        Parse *filepath* (JSON with optional ``#`` comments) and return a
        ``GameConfig`` instance.  Missing keys fall back to defaults.
        Prints a clear error and exits if the file cannot be parsed.
        """
        if not os.path.isfile(filepath):
            print(f"[Config] ERROR: config file '{filepath}' not found.", file=sys.stderr)
            sys.exit(1)

        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                raw = fh.read()
        except OSError as exc:
            print(f"[Config] ERROR: cannot read '{filepath}': {exc}", file=sys.stderr)
            sys.exit(1)

        cleaned = cls._strip_comments(raw)

        try:
            data: dict[str, Any] = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            print(f"[Config] ERROR: invalid JSON in '{filepath}': {exc}", file=sys.stderr)
            sys.exit(1)

        return cls._from_dict(data)

    @classmethod
    def load_or_default(cls, filepath: str) -> "GameConfig":
        """Like :meth:`load` but returns defaults instead of exiting on errors."""
        try:
            return cls.load(filepath)
        except SystemExit:
            print("[Config] WARNING: using default configuration.", file=sys.stderr)
            return cls()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _strip_comments(text: str) -> str:
        """Remove lines whose first non-whitespace character is ``#``."""
        lines = []
        for line in text.splitlines():
            stripped = line.lstrip()
            if not stripped.startswith("#"):
                lines.append(line)
        return "\n".join(lines)

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> "GameConfig":
        """Build a GameConfig from a raw dict, applying defaults for missing keys."""

        def get(key: str, default: Any) -> Any:
            value = data.get(key, default)
            return value if value is not None else default

        def clamp_int(value: Any, minimum: int, default: int) -> int:
            try:
                v = int(value)
                return max(minimum, v)
            except (TypeError, ValueError):
                return default

        def clamp_float(value: Any, minimum: float, default: float) -> float:
            try:
                v = float(value)
                return max(minimum, v)
            except (TypeError, ValueError):
                return default

        # Parse levels array
        raw_levels = get("levels", [])
        if not isinstance(raw_levels, list) or len(raw_levels) == 0:
            raw_levels = [{}]

        levels: list[LevelConfig] = []
        for lvl in raw_levels:
            if not isinstance(lvl, dict):
                lvl = {}
            levels.append(LevelConfig(
                width=clamp_int(lvl.get("width", 21), 5, 21),
                height=clamp_int(lvl.get("height", 21), 5, 21),
                time_limit=clamp_int(lvl.get("time_limit", 90), 0, 90),
                ghost_speed_factor=clamp_float(lvl.get("ghost_speed_factor", 1.0), 0.1, 1.0),
            ))

        # Ensure at least 10 levels by repeating the last one
        while len(levels) < 10:
            last = levels[-1]
            levels.append(LevelConfig(
                width=last.width,
                height=last.height,
                time_limit=max(10, last.time_limit - 5),
                ghost_speed_factor=min(2.0, last.ghost_speed_factor + 0.1),
            ))

        return cls(
            highscore_filename=str(get("highscore_filename", "highscores.json")),
            lives=clamp_int(get("lives", 3), 1, 99),
            pacgum=clamp_int(get("pacgum", 42), 1, 9999),
            points_per_pacgum=clamp_int(get("points_per_pacgum", 10), 0, 9999),
            points_per_super_pacgum=clamp_int(get("points_per_super_pacgum", 50), 0, 9999),
            points_per_ghost=clamp_int(get("points_per_ghost", 200), 0, 99999),
            frightened_duration=clamp_float(get("frightened_duration", 7.0), 1.0, 60.0),
            ghost_respawn_delay=clamp_float(get("ghost_respawn_delay", 5.0), 1.0, 60.0),
            player_speed=clamp_float(get("player_speed", 5.0), 0.5, 20.0),
            ghost_base_speed=clamp_float(get("ghost_base_speed", 4.0), 0.5, 20.0),
            frightened_speed_factor=clamp_float(get("frightened_speed_factor", 0.5), 0.1, 1.0),
            levels=levels,
        )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"GameConfig(lives={self.lives}, levels={len(self.levels)}, "
            f"pts_pacgum={self.points_per_pacgum}, pts_ghost={self.points_per_ghost})"
        )
