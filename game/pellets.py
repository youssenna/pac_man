"""
game/pellets.py
===============
Pacgum and super-pacgum (power pellet) management.

Responsibilities
----------------
- Store the position of every remaining pacgum and super-pacgum.
- Detect collection when the player walks over a pellet.
- Report when all pellets are eaten (level win condition).
- Support reset for new levels.

Maze convention
---------------
The maze grid uses:
    0 = empty corridor (pellet may be placed here)
    1 = wall
    2 = pacgum pre-placed in the maze (optional, used by some generators)
    3 = super-pacgum pre-placed in the maze (optional)

When you call ``PelletManager(maze)``, it scans for cells with value 2/3
OR places pellets in every open corridor (value 0), with super-pellets at
the 4 corners of the inner bounding box.

Usage (from your game loop)
----------------------------
    from game.pellets import PelletManager, PelletType

    pellets = PelletManager(maze, tile_size=24)

    # Each frame:
    result = pellets.check_collection(player.rect)
    if result == PelletType.PACGUM:
        score.add_pacgum()
    elif result == PelletType.SUPER:
        score.add_super_pacgum()
        for ghost in ghosts:
            ghost.set_frightened(config.frightened_duration)

    if pellets.all_eaten():
        # Level complete!
        pass

    # Draw remaining pellets:
    for col, row in pellets.pacgums:
        pygame.draw.circle(screen, WHITE, pellets.center_px(col, row), 3)
    for col, row in pellets.super_pacgums:
        pygame.draw.circle(screen, WHITE, pellets.center_px(col, row), 7)
"""

from __future__ import annotations

from enum import Enum, auto
from typing import Iterator

import pygame


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class PelletType(Enum):
    PACGUM = auto()
    SUPER  = auto()


# ---------------------------------------------------------------------------
# PelletManager
# ---------------------------------------------------------------------------

class PelletManager:
    """
    Manages all pellets (pacgums + super-pacgums) for a single level.

    Parameters
    ----------
    maze : list[list[int]]
        2-D grid (1 = wall, 0 = corridor).  Cells with value 2 are treated
        as pre-placed pacgums; cells with value 3 as super-pacgums.
        If no 2/3 values are found the manager auto-places pellets.
    tile_size : int
        Pixel size of one maze cell.
    super_positions : list[tuple[int,int]] | None
        Explicit (col, row) positions for super-pacgums.  If None, the 4
        open corners of the maze are used.
    """

    def __init__(
        self,
        maze: list[list[int]],
        tile_size: int = 24,
        super_positions: list[tuple[int, int]] | None = None,
    ) -> None:
        self._tile_size = tile_size

        # Sets of (col, row) tuples
        self._pacgums: set[tuple[int, int]] = set()
        self._super_pacgums: set[tuple[int, int]] = set()

        self._populate(maze, super_positions)

        # Total at start of level (for progress reporting)
        self._total = len(self._pacgums) + len(self._super_pacgums)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_collection(self, player_rect: pygame.Rect) -> PelletType | None:
        """
        Check whether *player_rect* overlaps a pellet and remove it.

        Returns the type of pellet eaten, or None if none was eaten.
        """
        # Use the centre of the player rect for grid lookup
        px = player_rect.centerx
        py = player_rect.centery
        ts = self._tile_size
        col = px // ts
        row = py // ts
        pos = (col, row)

        if pos in self._super_pacgums:
            self._super_pacgums.discard(pos)
            return PelletType.SUPER

        if pos in self._pacgums:
            self._pacgums.discard(pos)
            return PelletType.PACGUM

        return None

    def all_eaten(self) -> bool:
        """Return True when every pellet has been collected."""
        return len(self._pacgums) == 0 and len(self._super_pacgums) == 0

    def remaining(self) -> int:
        """Number of pellets still on the board."""
        return len(self._pacgums) + len(self._super_pacgums)

    def total(self) -> int:
        """Total pellets at the start of the level."""
        return self._total

    def reset(self, maze: list[list[int]], super_positions: list[tuple[int, int]] | None = None) -> None:
        """Re-populate pellets for a new level (or level restart)."""
        self._pacgums.clear()
        self._super_pacgums.clear()
        self._populate(maze, super_positions)
        self._total = len(self._pacgums) + len(self._super_pacgums)

    def center_px(self, col: int, row: int) -> tuple[int, int]:
        """Return the pixel centre of tile (col, row) for drawing."""
        ts = self._tile_size
        return (col * ts + ts // 2, row * ts + ts // 2)

    # ------------------------------------------------------------------
    # Properties (read-only views)
    # ------------------------------------------------------------------

    @property
    def pacgums(self) -> frozenset[tuple[int, int]]:
        """Frozen set of remaining pacgum positions (col, row)."""
        return frozenset(self._pacgums)

    @property
    def super_pacgums(self) -> frozenset[tuple[int, int]]:
        """Frozen set of remaining super-pacgum positions (col, row)."""
        return frozenset(self._super_pacgums)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _populate(
        self,
        maze: list[list[int]],
        super_positions: list[tuple[int, int]] | None,
    ) -> None:
        """Scan maze and fill pellet sets."""
        num_rows = len(maze)
        num_cols = len(maze[0]) if num_rows else 0

        has_prebuilt = any(
            cell in (2, 3)
            for row in maze
            for cell in row
        )

        if has_prebuilt:
            # Maze generator encoded pellets directly
            for r in range(num_rows):
                for c in range(num_cols):
                    cell = maze[r][c]
                    if cell == 2:
                        self._pacgums.add((c, r))
                    elif cell == 3:
                        self._super_pacgums.add((c, r))
        else:
            # Auto-place: pacgum on every open corridor
            for r in range(num_rows):
                for c in range(num_cols):
                    if maze[r][c] == 0:
                        self._pacgums.add((c, r))

            # Super-pacgums: use explicit positions or 4 open corners
            if super_positions:
                for pos in super_positions:
                    col, row = pos
                    self._pacgums.discard(pos)
                    self._super_pacgums.add(pos)
            else:
                for pos in self._find_corner_positions(maze, num_cols, num_rows):
                    self._pacgums.discard(pos)
                    self._super_pacgums.add(pos)

    @staticmethod
    def _find_corner_positions(
        maze: list[list[int]],
        num_cols: int,
        num_rows: int,
    ) -> list[tuple[int, int]]:
        """
        Find 4 open cells near the corners of the maze for super-pacgums.
        Searches in expanding rings from each corner until an open cell is found.
        """
        corners = [
            (1, 1),
            (num_cols - 2, 1),
            (1, num_rows - 2),
            (num_cols - 2, num_rows - 2),
        ]
        result = []
        for (cc, cr) in corners:
            found = None
            for radius in range(0, max(num_cols, num_rows)):
                for dc in range(-radius, radius + 1):
                    for dr in range(-radius, radius + 1):
                        c, r = cc + dc, cr + dr
                        if 0 <= c < num_cols and 0 <= r < num_rows:
                            if maze[r][c] == 0:
                                found = (c, r)
                                break
                    if found:
                        break
                if found:
                    break
            if found:
                result.append(found)
        return result

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"PelletManager(pacgums={len(self._pacgums)}, "
            f"super={len(self._super_pacgums)}, total={self._total})"
        )
