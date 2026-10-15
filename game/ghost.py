"""
game/ghost.py
=============
Ghost AI for the Pac-Man game.

Four classic ghost personalities
---------------------------------
Blinky  (red)    — Direct chaser: always targets the player's current tile.
Pinky   (pink)   — Ambusher:  targets 4 tiles ahead of the player.
Inky    (cyan)   — Fickle:    target is a reflection of Blinky's position
                               through a point 2 tiles ahead of the player.
Clyde   (orange) — Random:    chases like Blinky when far, retreats to its
                               scatter corner when within 8 tiles.

Ghost states
------------
CHASE       — Actively pursues the player using personality-specific logic.
SCATTER     — Retreats to a fixed corner of the maze (less aggressive).
FRIGHTENED  — Runs away from the player; can be eaten.
EATEN       — Invisible / returning to spawn; moves fast toward home.

Maze convention
---------------
    0 = corridor  (passable)
    1 = wall      (impassable)

Usage (from your game loop)
----------------------------
    from game.ghost import Blinky, Pinky, Inky, Clyde, GhostState

    blinky = Blinky(start_col=10, start_row=10, tile_size=24, config=config)
    ghosts = [blinky, Pinky(...), Inky(..., blinky=blinky), Clyde(...)]

    # Each frame:
    for ghost in ghosts:
        ghost.update(player, maze, dt)

    # When player eats a super-pacgum:
    for ghost in ghosts:
        ghost.set_frightened(config.frightened_duration)

    # Collision with player:
    if ghost.rect.colliderect(player.rect):
        if ghost.state == GhostState.FRIGHTENED:
            ghost.set_eaten()
            score_manager.add_ghost()
        elif ghost.state != GhostState.EATEN:
            player.lose_life()
"""

from __future__ import annotations

import math
import random
from enum import Enum, auto
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from .config import GameConfig
    from .player import Player, Direction


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class GhostState(Enum):
    CHASE      = auto()
    SCATTER    = auto()
    FRIGHTENED = auto()
    EATEN      = auto()


# Column / row deltas
_DIRS: list[tuple[int, int]] = [(0, -1), (0, 1), (-1, 0), (1, 0)]


# ---------------------------------------------------------------------------
# Ghost base class
# ---------------------------------------------------------------------------

class Ghost:
    """
    Base class for all ghosts.

    Sub-classes must override :meth:`_target_tile` to implement their
    unique AI personality.

    Parameters
    ----------
    start_col, start_row : int
        Initial (and respawn) grid position.
    scatter_col, scatter_row : int
        Corner the ghost retreats to in SCATTER mode.
    tile_size : int
        Pixel size of one maze tile.
    config : GameConfig
        Shared game configuration.
    color : tuple[int, int, int]
        RGB colour used by the renderer (passes through; not drawn here).
    """

    def __init__(
        self,
        start_col: int,
        start_row: int,
        scatter_col: int,
        scatter_row: int,
        tile_size: int,
        config: "GameConfig",
        color: tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        self._start_col = start_col
        self._start_row = start_row
        self._scatter_col = scatter_col
        self._scatter_row = scatter_row
        self._tile_size = tile_size
        self._config = config
        self.color = color

        # Current grid position (float for smooth movement)
        self._col: float = float(start_col)
        self._row: float = float(start_row)

        # Movement direction as (dcol, drow)
        self._direction: tuple[int, int] = (1, 0)

        # State
        self.state: GhostState = GhostState.SCATTER

        # Timers (seconds)
        self._frightened_timer: float = 0.0
        self._eaten_timer: float = 0.0

        # Speed in tiles / second
        self._base_speed: float = config.ghost_base_speed

        # Pygame rect (kept in sync)
        self.rect: pygame.Rect = pygame.Rect(
            int(start_col * tile_size),
            int(start_row * tile_size),
            tile_size,
            tile_size,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(
        self,
        player: "Player",
        maze: list[list[int]],
        dt: float,
        all_ghosts: "list[Ghost] | None" = None,
    ) -> None:
        """
        Advance the ghost by *dt* seconds.

        Parameters
        ----------
        player     : Player instance (for position/direction).
        maze       : 2-D grid (1 = wall).
        dt         : Delta time in seconds.
        all_ghosts : All ghosts in the scene (needed by Inky).
        """
        # Update timers
        if self.state == GhostState.FRIGHTENED:
            self._frightened_timer -= dt
            if self._frightened_timer <= 0:
                self.state = GhostState.CHASE

        elif self.state == GhostState.EATEN:
            self._eaten_timer -= dt
            if self._eaten_timer <= 0:
                self._respawn()

        # Determine speed
        speed = self._current_speed()

        # Move toward next tile (tile-by-tile AI decision)
        snap_threshold = 0.15
        col_i = round(self._col)
        row_i = round(self._row)
        near_centre = (
            abs(self._col - col_i) < snap_threshold
            and abs(self._row - row_i) < snap_threshold
        )

        if near_centre:
            self._col = float(col_i)
            self._row = float(row_i)
            target = self._get_target(player, all_ghosts)
            self._choose_direction(maze, col_i, row_i, target)

        # Apply movement
        dcol, drow = self._direction
        self._col += dcol * speed * dt
        self._row += drow * speed * dt

        # Horizontal tunnel wrap
        num_cols = len(maze[0]) if maze else 0
        if num_cols:
            if self._col < 0:
                self._col += num_cols
            elif self._col >= num_cols:
                self._col -= num_cols

        self._sync_rect()

    def set_frightened(self, duration: float) -> None:
        """Put the ghost into FRIGHTENED state for *duration* seconds."""
        if self.state != GhostState.EATEN:
            self.state = GhostState.FRIGHTENED
            self._frightened_timer = duration
            # Reverse direction when frightened starts
            self._direction = (-self._direction[0], -self._direction[1])

    def set_eaten(self) -> None:
        """Mark the ghost as eaten; it will respawn after a delay."""
        self.state = GhostState.EATEN
        self._eaten_timer = self._config.ghost_respawn_delay

    def reset(self) -> None:
        """Full reset to starting position and SCATTER state."""
        self._respawn()
        self.state = GhostState.SCATTER

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def is_frightened(self) -> bool:
        return self.state == GhostState.FRIGHTENED

    @property
    def is_eaten(self) -> bool:
        return self.state == GhostState.EATEN

    @property
    def frightened_timer(self) -> float:
        """Remaining frightened seconds (0 when not frightened)."""
        return max(0.0, self._frightened_timer)

    @property
    def grid_col(self) -> int:
        return round(self._col)

    @property
    def grid_row(self) -> int:
        return round(self._row)

    # ------------------------------------------------------------------
    # Override in subclasses
    # ------------------------------------------------------------------

    def _target_tile(
        self,
        player: "Player",
        all_ghosts: "list[Ghost] | None",
    ) -> tuple[int, int]:
        """Return the (col, row) this ghost is trying to reach."""
        return (player.grid_col, player.grid_row)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_target(
        self,
        player: "Player",
        all_ghosts: "list[Ghost] | None",
    ) -> tuple[int, int]:
        if self.state == GhostState.FRIGHTENED:
            # Random target when frightened
            return (
                random.randint(0, 30),
                random.randint(0, 30),
            )
        if self.state == GhostState.SCATTER:
            return (self._scatter_col, self._scatter_row)
        if self.state == GhostState.EATEN:
            return (self._start_col, self._start_row)
        # CHASE
        return self._target_tile(player, all_ghosts)

    def _choose_direction(
        self,
        maze: list[list[int]],
        col: int,
        row: int,
        target: tuple[int, int],
    ) -> None:
        """
        Classic Pac-Man direction-selection algorithm:
        - Ghosts cannot reverse direction (except when entering FRIGHTENED).
        - Among valid moves, pick the one that minimises Euclidean distance
          to the target (or random when frightened).
        """
        reverse = (-self._direction[0], -self._direction[1])
        num_rows = len(maze)
        num_cols = len(maze[0]) if num_rows else 0

        # If frightened, pick a random valid direction (not reverse)
        if self.state == GhostState.FRIGHTENED:
            candidates = []
            for dcol, drow in _DIRS:
                if (dcol, drow) == reverse:
                    continue
                nc, nr = col + dcol, row + drow
                nc = nc % num_cols if num_cols else nc
                if 0 <= nr < num_rows and maze[nr][nc] != 1:
                    candidates.append((dcol, drow))
            if candidates:
                self._direction = random.choice(candidates)
            return

        # Otherwise: pick direction minimising distance to target
        best_dir = None
        best_dist = float("inf")
        for dcol, drow in _DIRS:
            if (dcol, drow) == reverse:
                continue
            nc, nr = col + dcol, row + drow
            nc = nc % num_cols if num_cols else nc
            if 0 <= nr < num_rows and maze[nr][nc] != 1:
                dist = math.hypot(nc - target[0], nr - target[1])
                if dist < best_dist:
                    best_dist = dist
                    best_dir = (dcol, drow)

        if best_dir:
            self._direction = best_dir

    def _current_speed(self) -> float:
        if self.state == GhostState.FRIGHTENED:
            return self._base_speed * self._config.frightened_speed_factor
        if self.state == GhostState.EATEN:
            return self._base_speed * 2.0   # rush back home
        return self._base_speed

    def _respawn(self) -> None:
        self._col = float(self._start_col)
        self._row = float(self._start_row)
        self._direction = (1, 0)
        self.state = GhostState.SCATTER
        self._frightened_timer = 0.0
        self._eaten_timer = 0.0
        self._sync_rect()

    def _sync_rect(self) -> None:
        ts = self._tile_size
        self.rect.x = round(self._col * ts)
        self.rect.y = round(self._row * ts)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"{self.__class__.__name__}(col={self._col:.1f}, row={self._row:.1f}, "
            f"state={self.state.name})"
        )


# ---------------------------------------------------------------------------
# Blinky — The direct chaser (red)
# ---------------------------------------------------------------------------

class Blinky(Ghost):
    """
    Blinky always targets the player's exact current tile.
    Scatter corner: top-right.
    """

    def __init__(
        self,
        start_col: int,
        start_row: int,
        tile_size: int,
        config: "GameConfig",
        maze_cols: int = 28,
    ) -> None:
        super().__init__(
            start_col=start_col,
            start_row=start_row,
            scatter_col=maze_cols - 2,
            scatter_row=1,
            tile_size=tile_size,
            config=config,
            color=(255, 0, 0),
        )

    def _target_tile(
        self,
        player: "Player",
        all_ghosts: "list[Ghost] | None",
    ) -> tuple[int, int]:
        return (player.grid_col, player.grid_row)


# ---------------------------------------------------------------------------
# Pinky — The ambusher (pink)
# ---------------------------------------------------------------------------

class Pinky(Ghost):
    """
    Pinky targets a point 4 tiles ahead of the player's current direction.
    Scatter corner: top-left.

    Note: the original game had an overflow bug where "up" added a left offset
    too.  We implement the clean version (pure 4-tile look-ahead).
    """

    def __init__(
        self,
        start_col: int,
        start_row: int,
        tile_size: int,
        config: "GameConfig",
    ) -> None:
        super().__init__(
            start_col=start_col,
            start_row=start_row,
            scatter_col=1,
            scatter_row=1,
            tile_size=tile_size,
            config=config,
            color=(255, 184, 255),
        )

    def _target_tile(
        self,
        player: "Player",
        all_ghosts: "list[Ghost] | None",
    ) -> tuple[int, int]:
        from .player import Direction, _DELTA
        dcol, drow = _DELTA.get(player.direction, (0, 0))
        target_col = player.grid_col + dcol * 4
        target_row = player.grid_row + drow * 4
        return (target_col, target_row)


# ---------------------------------------------------------------------------
# Inky — The fickle one (cyan)
# ---------------------------------------------------------------------------

class Inky(Ghost):
    """
    Inky's target is computed using Blinky as a reference:
    1. Take a point 2 tiles ahead of the player (P2).
    2. Draw a vector from Blinky's position to P2.
    3. Double that vector — the tip is Inky's target.

    Scatter corner: bottom-right.
    """

    def __init__(
        self,
        start_col: int,
        start_row: int,
        tile_size: int,
        config: "GameConfig",
        blinky: Ghost | None = None,
        maze_cols: int = 28,
        maze_rows: int = 31,
    ) -> None:
        super().__init__(
            start_col=start_col,
            start_row=start_row,
            scatter_col=maze_cols - 2,
            scatter_row=maze_rows - 2,
            tile_size=tile_size,
            config=config,
            color=(0, 255, 255),
        )
        self._blinky = blinky
        self._maze_cols = maze_cols
        self._maze_rows = maze_rows

    def set_blinky(self, blinky: Ghost) -> None:
        """Inject Blinky reference after construction if needed."""
        self._blinky = blinky

    def _target_tile(
        self,
        player: "Player",
        all_ghosts: "list[Ghost] | None",
    ) -> tuple[int, int]:
        from .player import Direction, _DELTA

        # Point 2 tiles ahead of player
        dcol, drow = _DELTA.get(player.direction, (0, 0))
        pivot_col = player.grid_col + dcol * 2
        pivot_row = player.grid_row + drow * 2

        # Blinky reference — search from all_ghosts if not set directly
        blinky = self._blinky
        if blinky is None and all_ghosts:
            for g in all_ghosts:
                if isinstance(g, Blinky):
                    blinky = g
                    break

        if blinky is None:
            # Fallback: behave like Blinky
            return (player.grid_col, player.grid_row)

        # Double the vector from Blinky → pivot
        target_col = pivot_col + (pivot_col - blinky.grid_col)
        target_row = pivot_row + (pivot_row - blinky.grid_row)
        return (target_col, target_row)


# ---------------------------------------------------------------------------
# Clyde — The unpredictable one (orange)
# ---------------------------------------------------------------------------

class Clyde(Ghost):
    """
    Clyde chases the player when far away (> 8 tiles) but retreats to his
    scatter corner when within 8 tiles.  This creates an oscillating pattern
    that keeps him away from the player near his corner.

    Scatter corner: bottom-left.
    """

    CHASE_RADIUS = 8  # tiles

    def __init__(
        self,
        start_col: int,
        start_row: int,
        tile_size: int,
        config: "GameConfig",
        maze_rows: int = 31,
    ) -> None:
        super().__init__(
            start_col=start_col,
            start_row=start_row,
            scatter_col=1,
            scatter_row=maze_rows - 2,
            tile_size=tile_size,
            config=config,
            color=(255, 184, 81),
        )

    def _target_tile(
        self,
        player: "Player",
        all_ghosts: "list[Ghost] | None",
    ) -> tuple[int, int]:
        dist = math.hypot(
            player.grid_col - self.grid_col,
            player.grid_row - self.grid_row,
        )
        if dist > self.CHASE_RADIUS:
            # Far — chase directly like Blinky
            return (player.grid_col, player.grid_row)
        else:
            # Close — flee to scatter corner
            return (self._scatter_col, self._scatter_row)
