"""
Pac-Man game backend package.

Modules (friend's part):
    config      — JSON config parser (supports # comments)
    player      — Player movement & wall collision
    ghost       — Ghost AI: Blinky, Pinky, Inky, Clyde
    pellets     — Pacgum & super-pacgum management
    scoring     — Score tracking with ghost multiplier
    highscore   — Top-10 highscore persistence (JSON)
"""

from .config import GameConfig
from .player import Player
from .ghost import Ghost, Blinky, Pinky, Inky, Clyde, GhostState
from .pellets import PelletManager, PelletType
from .scoring import ScoreManager
from .highscore import HighscoreManager

__all__ = [
    "GameConfig",
    "Player",
    "Ghost", "Blinky", "Pinky", "Inky", "Clyde", "GhostState",
    "PelletManager", "PelletType",
    "ScoreManager",
    "HighscoreManager",
]
