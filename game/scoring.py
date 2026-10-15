"""
game/scoring.py
===============
Score management for the Pac-Man game.

Features
--------
- Tracks total score across the full game session.
- Classic ghost-eating multiplier: 200 → 400 → 800 → 1600 per power pellet.
  The chain resets when frightened mode ends or a new super-pacgum is eaten.
- Score never decreases.
- Exposes current score and per-category history.

Usage (from your game loop)
----------------------------
    from game.scoring import ScoreManager

    score = ScoreManager(config)

    # Player eats a pacgum:
    score.add_pacgum()

    # Player eats a super-pacgum (resets ghost chain):
    score.add_super_pacgum()

    # Player eats a ghost while super-pacgum is active:
    pts = score.add_ghost()   # returns points awarded
    print(pts)                # 200, then 400, then 800, then 1600, 1600, ...

    # When frightened mode ends, reset ghost chain:
    score.reset_ghost_chain()

    # New level or new game:
    score.reset()             # full reset
    score.reset(keep_score=True)  # keep score but reset chain (new level)

    print(score.score)        # current total
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import GameConfig


class ScoreManager:
    """
    Manages the player's score.

    Parameters
    ----------
    config : GameConfig
        Provides points_per_pacgum, points_per_super_pacgum, points_per_ghost.
    """

    # Ghost chain multipliers (index 0 → first ghost, capped at index 3)
    _GHOST_MULTIPLIERS: tuple[int, ...] = (1, 2, 4, 8)

    def __init__(self, config: "GameConfig") -> None:
        self._config = config

        # Running totals
        self._score: int = 0
        self._pacgums_eaten: int = 0
        self._super_pacgums_eaten: int = 0
        self._ghosts_eaten: int = 0          # total across the game
        self._ghost_chain: int = 0           # consecutive ghosts in one power-up

        # History list of (category, points) for debug / UI
        self._history: list[tuple[str, int]] = []

    # ------------------------------------------------------------------
    # Scoring actions
    # ------------------------------------------------------------------

    def add_pacgum(self) -> int:
        """Award points for eating a regular pacgum. Returns points added."""
        pts = self._config.points_per_pacgum
        self._score += pts
        self._pacgums_eaten += 1
        self._history.append(("pacgum", pts))
        return pts

    def add_super_pacgum(self) -> int:
        """
        Award points for eating a super-pacgum and reset the ghost chain.
        Returns points added.
        """
        pts = self._config.points_per_super_pacgum
        self._score += pts
        self._super_pacgums_eaten += 1
        self._ghost_chain = 0            # fresh chain for this power-up
        self._history.append(("super_pacgum", pts))
        return pts

    def add_ghost(self) -> int:
        """
        Award points for eating a frightened ghost.

        Points double with each consecutive ghost eaten during the same
        power-up window (200, 400, 800, 1600).  After index 3 the value
        stays at 1600.

        Returns
        -------
        int
            Points awarded for this ghost.
        """
        idx = min(self._ghost_chain, len(self._GHOST_MULTIPLIERS) - 1)
        pts = self._config.points_per_ghost * self._GHOST_MULTIPLIERS[idx]
        self._score += pts
        self._ghosts_eaten += 1
        self._ghost_chain += 1
        self._history.append(("ghost", pts))
        return pts

    def reset_ghost_chain(self) -> None:
        """
        Reset the consecutive ghost counter.
        Call this when frightened mode ends without eating all ghosts.
        """
        self._ghost_chain = 0

    # ------------------------------------------------------------------
    # Game / level control
    # ------------------------------------------------------------------

    def reset(self, keep_score: bool = False) -> None:
        """
        Reset the score manager.

        Parameters
        ----------
        keep_score : bool
            If True, the accumulated score is preserved (useful between
            levels).  Per-level counters are always reset.
        """
        if not keep_score:
            self._score = 0
            self._history.clear()

        self._pacgums_eaten = 0
        self._super_pacgums_eaten = 0
        self._ghosts_eaten = 0
        self._ghost_chain = 0

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def score(self) -> int:
        """Current total score."""
        return self._score

    @property
    def pacgums_eaten(self) -> int:
        """Pacgums eaten this level."""
        return self._pacgums_eaten

    @property
    def super_pacgums_eaten(self) -> int:
        """Super-pacgums eaten this level."""
        return self._super_pacgums_eaten

    @property
    def ghosts_eaten(self) -> int:
        """Total ghosts eaten across the entire game session."""
        return self._ghosts_eaten

    @property
    def ghost_chain(self) -> int:
        """Current consecutive ghost chain count (resets per super-pacgum)."""
        return self._ghost_chain

    @property
    def next_ghost_points(self) -> int:
        """Preview: points that would be awarded for the next ghost eaten."""
        idx = min(self._ghost_chain, len(self._GHOST_MULTIPLIERS) - 1)
        return self._config.points_per_ghost * self._GHOST_MULTIPLIERS[idx]

    @property
    def history(self) -> list[tuple[str, int]]:
        """Read-only scoring history: list of (category, points) tuples."""
        return list(self._history)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ScoreManager(score={self._score}, "
            f"chain={self._ghost_chain}, ghosts={self._ghosts_eaten})"
        )
