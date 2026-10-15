"""
game/player.py
==============
Player class for the Pac-Man game.

Responsibilities
----------------
- Grid-based movement through the maze (4 directions).
- Wall collision detection using the maze grid.
- Life management (lose_life, respawn).
- Exposes a pygame.Rect for rendering by the game loop.

Maze convention
---------------
The maze is a 2-D list (list of rows) where:
    0  = open corridor  (player/ghost can pass)
    1  = wall           (impassable)

Coordinate system
-----------------
``col`` increases to the right, ``row`` increases downward.
``tile_size`` is the width/height of one cell in pixels.

Usage (from your game loop)
----------------------------
    from game.player import Player

    player = Player(
        start_col=10, start_row=15,
        tile_size=24,
        config=config,          # GameConfig instance
    )

    # Each frame:
    player.set_direction(direction)   # call when key pressed
    player.update(maze, dt)           # advance movement
    screen.blit(sprite, player.rect)  # render using player.rect

    if player.is_dead():
        game_over()
"""

from __future__ import annotations

import pygame
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import GameConfig


# ---------------------------------------------------------------------------
# Direction enum
# ---------------------------------------------------------------------------

class Direction(Enum):
    UP    = auto()
    DOWN  = auto()
    LEFT  = auto()
    RIGHT = auto()
    NONE  = auto()


# Column / row deltas for each direction
_DELTA: dict[Direction, tuple[int, int]] = {
    Direction.UP:    (0, -1),
    Direction.DOWN:  (0,  1),
    Direction.LEFT:  (-1, 0),
    Direction.RIGHT: (1,  0),
    Direction.NONE:  (0,  0),
}


# ---------------------------------------------------------------------------
# Player class
# ---------------------------------------------------------------------------

class Player:
    """
    Represents the Pac-Man player entity.

    Parameters
    ----------
    start_col, start_row : int
        Initial grid position (column, row).
    tile_size : int
        Pixel size of one maze cell.
    config : GameConfig
        Game configuration (lives, speed, …).
    """

    def __init__(
        self,
        start_col: int,
        start_row: int,
        tile_size: int,
        config: "GameConfig",
    ) -> None:
        self._start_col = start_col
        self._start_row = start_row
        self._tile_size = tile_size
        self._config = config

        # Grid position (float for sub-tile movement)
        self._col: float = float(start_col)
        self._row: float = float(start_row)

        # Current movement direction and buffered next direction
        self._direction: Direction = Direction.NONE
        self._next_direction: Direction = Direction.NONE

        # Lives
        self._lives: int = config.lives

        # Whether the player is currently dying (animation flag for the loop)
        self._dying: bool = False

        # Speed in tiles-per-second
        self._speed: float = config.player_speed

        # Pygame rect (pixel position) — kept in sync with _col/_row
        self.rect: pygame.Rect = pygame.Rect(
            int(start_col * tile_size),
            int(start_row * tile_size),
            tile_size,
            tile_size,
        )

    # ------------------------------------------------------------------
    # Public API — called every frame by the game loop
    # ------------------------------------------------------------------

    def set_direction(self, direction: Direction) -> None:
        """
        Buffer a new desired movement direction.
        The direction is applied only when the player reaches the next tile
        centre (prevents clipping through walls on diagonal input).
        """
        self._next_direction = direction

    def update(self, maze: list[list[int]], dt: float) -> None:
        """
        Advance the player by *dt* seconds.

        Parameters
        ----------
        maze : list[list[int]]
            2-D grid (row-major).  ``maze[row][col] == 1`` means wall.
        dt : float
            Elapsed time since last frame in **seconds**.
        """
        if self._dying:
            return

        # Snap to grid centre before checking direction changes
        # (within half a pixel of a tile centre)
        snap_threshold = 0.15  # tiles

        col_centre = round(self._col)
        row_centre = round(self._row)
        near_centre = (
            abs(self._col - col_centre) < snap_threshold
            and abs(self._row - row_centre) < snap_threshold
        )

        if near_centre:
            # Try to apply buffered direction
            if self._next_direction != Direction.NONE:
                if self._can_move(maze, col_centre, row_centre, self._next_direction):
                    self._direction = self._next_direction
                    self._next_direction = Direction.NONE
                    # Snap exactly to centre so we don't drift
                    self._col = float(col_centre)
                    self._row = float(row_centre)

            # If current direction hits a wall, stop
            if self._direction != Direction.NONE:
                if not self._can_move(maze, col_centre, row_centre, self._direction):
                    self._direction = Direction.NONE
                    self._col = float(col_centre)
                    self._row = float(row_centre)

        # Move
        if self._direction != Direction.NONE:
            dcol, drow = _DELTA[self._direction]
            distance = self._speed * dt
            self._col += dcol * distance
            self._row += drow * distance

        # Wrap horizontally (tunnel)
        num_cols = len(maze[0]) if maze else 0
        if self._col < 0:
            self._col += num_cols
        elif self._col >= num_cols:
            self._col -= num_cols

        # Update pixel rect
        self._sync_rect()

    def lose_life(self) -> None:
        """Deduct one life and mark the player as dying."""
        self._lives -= 1
        self._dying = True

    def respawn(self) -> None:
        """
        Respawn the player at the starting position.
        Call this after the death animation finishes.
        """
        self._col = float(self._start_col)
        self._row = float(self._start_row)
        self._direction = Direction.NONE
        self._next_direction = Direction.NONE
        self._dying = False
        self._sync_rect()

    def reset(self, col: int | None = None, row: int | None = None) -> None:
        """
        Full reset (new game / new level).  Optionally set a new start position.
        """
        if col is not None:
            self._start_col = col
        if row is not None:
            self._start_row = row
        self._lives = self._config.lives
        self.respawn()

    def is_dead(self) -> bool:
        """Return True when all lives are exhausted."""
        return self._lives <= 0

    def is_dying(self) -> bool:
        """Return True while the death animation should play."""
        return self._dying

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def lives(self) -> int:
        return self._lives

    @property
    def col(self) -> float:
        """Current column position (float, sub-tile precision)."""
        return self._col

    @property
    def row(self) -> float:
        """Current row position (float, sub-tile precision)."""
        return self._row

    @property
    def grid_col(self) -> int:
        """Nearest integer column — use for grid lookups."""
        return round(self._col)

    @property
    def grid_row(self) -> int:
        """Nearest integer row — use for grid lookups."""
        return round(self._row)

    @property
    def direction(self) -> Direction:
        return self._direction

    @property
    def speed(self) -> float:
        return self._speed

    @speed.setter
    def speed(self, value: float) -> None:
        """Allow cheat mode to adjust speed."""
        self._speed = max(0.0, value)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _can_move(
        self,
        maze: list[list[int]],
        col: int,
        row: int,
        direction: Direction,
    ) -> bool:
        """Return True if moving one tile in *direction* from (col, row) is valid."""
        dcol, drow = _DELTA[direction]
        next_col = col + dcol
        next_row = row + drow

        num_rows = len(maze)
        num_cols = len(maze[0]) if num_rows else 0

        # Horizontal wrap (tunnels)
        next_col = next_col % num_cols if num_cols else next_col

        if next_row < 0 or next_row >= num_rows:
            return False

        return maze[next_row][next_col] != 1

    def _sync_rect(self) -> None:
        """Update the pixel rect from the float grid position."""
        ts = self._tile_size
        self.rect.x = round(self._col * ts)
        self.rect.y = round(self._row * ts)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Player(col={self._col:.2f}, row={self._row:.2f}, "
            f"lives={self._lives}, dir={self._direction.name})"
        )
