
from enum import Enum, auto


class Direction(Enum):
    UP = (0, -1)
    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)


class GameStatus(Enum):
    READY = auto()
    PLAYING = auto()
    WON = auto()
    LOST = auto()


# Wall bitmasks from your MazeGenerator
WALLS = {
    Direction.UP: 1,
    Direction.RIGHT: 2,
    Direction.DOWN: 4,
    Direction.LEFT: 8,
}


class GameEngine:
    def __init__(
        self,
        maze: list[list[int]],
        player_start: tuple[int, int] = (10, 10),
        ghost_starts: list[tuple[int, int]] | None = None,
        initial_lives: int = 3,
    ):
        if not maze or not maze[0]:
            raise ValueError("Maze cannot be empty")

        if any(len(row) != len(maze[0]) for row in maze):
            raise ValueError("Maze must be rectangular")

        self.maze = maze
        self.rows = len(maze)
        self.cols = len(maze[0])

        self.player_start = player_start
        self.ghost_starts = ghost_starts or [
            (1, 1), (self.cols - 2, 1),
            (1, self.rows - 2), (self.cols - 2, self.rows - 2),
        ]

        self.initial_lives = initial_lives
        self.reset()

    def reset(self):
        """Start a new game."""
        self.player_position = self.player_start
        self.player_direction = Direction.LEFT
        self.requested_direction = Direction.LEFT

        self.ghost_positions = list(self.ghost_starts)
        self.ghost_directions = [
            Direction.UP for _ in self.ghost_positions
        ]

        # One pac-gum per traversable cell, excluding starting positions.
        self.pacgums = {
            (x, y)
            for y in range(self.rows)
            for x in range(self.cols)
            if (x, y) not in self._wall_cells()
            and (x, y) != self.player_start
            and (x, y) not in self.ghost_starts
        }

        self.score = 0
        self.lives = self.initial_lives
        self.status = GameStatus.READY

    def _wall_cells(self):
        """Return cells completely enclosed by four walls."""
        return {
            (x, y)
            for y, row in enumerate(self.maze)
            for x, cell in enumerate(row)
            if cell == 15
        }

    def can_move(
        self,
        position: tuple[int, int],
        direction: Direction,
    ) -> bool:
        """Check the wall and grid boundaries before moving."""
        x, y = position
        dx, dy = direction.value
        nx, ny = x + dx, y + dy

        if not (0 <= nx < self.cols and 0 <= ny < self.rows):
            return False

        current_cell = self.maze[y][x]
        next_cell = self.maze[ny][nx]

        # Check the wall on both sides of the connection.
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.RIGHT: Direction.LEFT,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
        }

        return not (
            current_cell & WALLS[direction]
            or next_cell & WALLS[opposite[direction]]
        )

    def start(self):
        if self.status == GameStatus.READY:
            self.status = GameStatus.PLAYING

    def set_direction(self, direction: Direction):
        """Called when the player presses a direction key."""
        if self.status in (GameStatus.READY, GameStatus.PLAYING):
            self.requested_direction = direction

    def update(self):
        """Advance one logical game step."""
        if self.status == GameStatus.READY:
            self.start()
            return

        if self.status != GameStatus.PLAYING:
            return

        self._update_player()
        self._collect_pacgum()
        self._update_ghosts()
        self._check_collisions()

        if self.status == GameStatus.PLAYING and not self.pacgums:
            self.status = GameStatus.WON

    def _update_player(self):
        # Allow the player to turn as soon as the path is open.
        if self.can_move(
            self.player_position, self.requested_direction
        ):
            self.player_direction = self.requested_direction

        if self.can_move(self.player_position, self.player_direction):
            x, y = self.player_position
            dx, dy = self.player_direction.value
            self.player_position = (x + dx, y + dy)

    def _collect_pacgum(self):
        if self.player_position in self.pacgums:
            self.pacgums.remove(self.player_position)
            self.score += 10

    def _update_ghosts(self):
        # Basic random-turn-free movement for the initial backend.
        # Replace this with your existing Ghost AI when ready.
        for i, position in enumerate(self.ghost_positions):
            direction = self.ghost_directions[i]

            if not self.can_move(position, direction):
                for candidate in Direction:
                    if self.can_move(position, candidate):
                        direction = candidate
                        break

            if self.can_move(position, direction):
                x, y = position
                dx, dy = direction.value
                self.ghost_positions[i] = (x + dx, y + dy)
                self.ghost_directions[i] = direction

    def _check_collisions(self):
        if self.player_position not in self.ghost_positions:
            return

        self.lives -= 1

        if self.lives <= 0:
            self.status = GameStatus.LOST
            return

        self.player_position = self.player_start
        self.player_direction = Direction.LEFT
        self.requested_direction = Direction.LEFT

        # Return ghosts to their starting positions.
        self.ghost_positions = list(self.ghost_starts)
        self.ghost_directions = [
            Direction.UP for _ in self.ghost_positions
        ]

    def get_state(self) -> dict:
        """Return the data needed by the UI."""
        return {
            "player_position": self.player_position,
            "player_direction": self.player_direction,
            "ghost_positions": tuple(self.ghost_positions),
            "pacgums": frozenset(self.pacgums),
            "score": self.score,
            "lives": self.lives,
            "status": self.status,
        }
