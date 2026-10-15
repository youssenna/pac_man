"""
game/highscore.py
=================
Persistent highscore management for the Pac-Man game.

Responsibilities
----------------
- Load/save a Top-10 highscore list from/to a JSON file.
- Check whether a given score qualifies for the leaderboard.
- Add a new entry (name + score) and keep the list sorted.
- Handle missing files, corruption, and permission errors gracefully.

File format (highscores.json)
------------------------------
[
    {"name": "AAA", "score": 9800},
    {"name": "BBB", "score": 7400},
    ...
]

Usage (from your game loop / UI)
---------------------------------
    from game.highscore import HighscoreManager

    hs = HighscoreManager("highscores.json")

    # After game over:
    if hs.is_highscore(final_score):
        # show name-entry screen, then:
        hs.save("PLAYER", final_score)

    # To display leaderboard:
    for rank, entry in enumerate(hs.get_top10(), start=1):
        print(f"{rank}. {entry['name']:10s} {entry['score']}")
"""

from __future__ import annotations

import json
import os
import sys
from typing import TypedDict


# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------

class HighscoreEntry(TypedDict):
    name: str
    score: int


# ---------------------------------------------------------------------------
# HighscoreManager
# ---------------------------------------------------------------------------

class HighscoreManager:
    """
    Manages a persistent Top-10 highscore list stored in a JSON file.

    Parameters
    ----------
    filepath : str
        Path to the JSON file used for persistence.
        The file is created automatically if it does not exist.
    max_entries : int
        Maximum number of entries to keep (default 10).
    """

    def __init__(self, filepath: str, max_entries: int = 10) -> None:
        self._filepath = filepath
        self._max = max_entries
        self._entries: list[HighscoreEntry] = []
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_highscore(self, score: int) -> bool:
        """
        Return True if *score* qualifies for the leaderboard.

        A score qualifies if:
        - The list has fewer than ``max_entries`` entries, OR
        - The score is strictly greater than the lowest entry.
        """
        if len(self._entries) < self._max:
            return True
        return score > self._entries[-1]["score"]

    def save(self, name: str, score: int) -> int:
        """
        Add a new entry, re-sort, trim to ``max_entries``, and persist to disk.

        Parameters
        ----------
        name : str
            Player name (truncated to 20 characters, stripped of whitespace).
        score : int
            Score to save.

        Returns
        -------
        int
            1-based rank of the new entry in the leaderboard, or -1 if it
            did not make it into the top list.
        """
        clean_name = str(name).strip()[:20] or "---"
        new_entry: HighscoreEntry = {"name": clean_name, "score": int(score)}

        self._entries.append(new_entry)
        self._entries.sort(key=lambda e: e["score"], reverse=True)
        self._entries = self._entries[: self._max]

        try:
            rank = next(
                i + 1
                for i, e in enumerate(self._entries)
                if e is new_entry
            )
        except StopIteration:
            rank = -1  # didn't make the cut (shouldn't happen if is_highscore was checked)

        self._persist()
        return rank

    def get_top10(self) -> list[HighscoreEntry]:
        """Return a copy of the current leaderboard (sorted, high → low)."""
        return list(self._entries)

    def clear(self) -> None:
        """Erase all entries and persist the empty list."""
        self._entries.clear()
        self._persist()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def filepath(self) -> str:
        return self._filepath

    @property
    def count(self) -> int:
        """Number of entries currently stored."""
        return len(self._entries)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Load entries from disk; silently starts fresh on any error."""
        if not os.path.isfile(self._filepath):
            self._entries = []
            return

        try:
            with open(self._filepath, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            print(
                f"[Highscore] WARNING: could not read '{self._filepath}': {exc}. "
                "Starting with empty leaderboard.",
                file=sys.stderr,
            )
            self._entries = []
            return

        if not isinstance(raw, list):
            print(
                f"[Highscore] WARNING: '{self._filepath}' does not contain a list. "
                "Starting with empty leaderboard.",
                file=sys.stderr,
            )
            self._entries = []
            return

        validated: list[HighscoreEntry] = []
        for item in raw:
            if isinstance(item, dict):
                try:
                    entry: HighscoreEntry = {
                        "name": str(item.get("name", "---"))[:20],
                        "score": int(item.get("score", 0)),
                    }
                    validated.append(entry)
                except (TypeError, ValueError):
                    continue  # skip malformed entries

        # Sort and trim in case the file was hand-edited
        validated.sort(key=lambda e: e["score"], reverse=True)
        self._entries = validated[: self._max]

    def _persist(self) -> None:
        """Write current entries to disk."""
        try:
            with open(self._filepath, "w", encoding="utf-8") as fh:
                json.dump(self._entries, fh, indent=2, ensure_ascii=False)
        except OSError as exc:
            print(
                f"[Highscore] ERROR: could not save highscores to '{self._filepath}': {exc}",
                file=sys.stderr,
            )

    def __repr__(self) -> str:  # pragma: no cover
        top = self._entries[0] if self._entries else None
        return (
            f"HighscoreManager(file='{self._filepath}', "
            f"entries={self.count}, top={top})"
        )
