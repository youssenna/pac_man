from .characters import Player, Ghost
from .move import move_character, decide_next_move
from .ghost_ai import decide_ghost_move
from .parsing import Config
from .level import Level
from .collisions import check_ghosts_collision


class GameEngine:
    def __init__(self, config: Config, level_index: int = 0):
        self.config = config
        self.level_index = level_index
        self.level_config = config.levels[level_index]
        self.player = Player(0, 0, lives=config.lives)
        self.reset_player_position()
        self.level = Level(config, level_index, self.player)
        self.state = "playing"
        self.move_interval = 0.15
        self.move_elapsed = 0.0
        self.ghost_move_interval = 0.5
        self.ghost_move_elapsed = 0.0
        self.previous_position = (self.player.x, self.player.y)

    def handle_input(self, direction: str) -> None:
        if self.state != "playing":
            return
        if direction not in ("N", "E", "S", "W"):
            return
        self.player.next_direction = direction

    def get_visual_position(self) -> tuple[float, float]:
        progress = min(self.move_elapsed / self.move_interval, 1.0)
        previous_x, previous_y = self.previous_position
        current_x, current_y = self.player.x, self.player.y
        visual_x = previous_x + (current_x - previous_x) * progress
        visual_y = previous_y + (current_y - previous_y) * progress
        return visual_x, visual_y

    def get_ghost_visual_position(self, ghost: Ghost) -> tuple[float, float]:
        progress = min(self.ghost_move_elapsed / self.ghost_move_interval, 1.0)
        visual_x = ghost.previous_x + (ghost.x - ghost.previous_x) * progress
        visual_y = ghost.previous_y + (ghost.y - ghost.previous_y) * progress
        return visual_x, visual_y

    def check_collisions(self) -> None:
        lives_before = self.player.lives
        check_ghosts_collision(
            self.level.level_config.width,
            self.level.level_config.height,
            self.player,
            self.level.ghosts,
            self.config,
        )
        if self.player.lives < lives_before:
            self.previous_position = (self.player.x, self.player.y)
        if self.player.lives <= 0:
            self.state = "game_over"

    def update(self, dt: float) -> None:
        if self.state != "playing":
            return
        dt = min(dt, 0.05)
        self.level.update(dt)
        if self.level.time_expired:
            self.state = "game_over"
            return
        self.move_elapsed += dt
        self.ghost_move_elapsed += dt
        while self.move_elapsed >= self.move_interval:
            if self.state != "playing":
                break
            self.move_elapsed -= self.move_interval
            self.previous_position = (self.player.x, self.player.y)
            direction = decide_next_move(self.player, self.level.maze)
            move_character(self.player, self.level.maze, direction)
            self.level.handle_pacgums()
            if self.level.completed:
                if self.level_index + 1 < len(self.config.levels):
                    self.state = "level_complete"
                else:
                    self.state = "victory"
                break
            self.check_collisions()
            if self.state != "playing":
                break
        while self.ghost_move_elapsed >= self.ghost_move_interval:
            if self.state != "playing":
                break
            self.ghost_move_elapsed -= self.ghost_move_interval
            self.move_ghosts()
            self.check_collisions()
            if self.state != "playing":
                return

    def reset_player_position(self) -> None:
        center_x = self.level_config.width // 2
        center_y = self.level_config.height // 2
        self.player.respawn(center_x, center_y)

    def move_ghosts(self) -> None:
        for ghost in self.level.ghosts:
            ghost.previous_x = ghost.x
            ghost.previous_y = ghost.y
            direction = decide_ghost_move(
                ghost,
                self.player,
                self.level.maze,
                self.level.level_config.width,
                self.level.level_config.height,
            )
            if direction:
                move_character(ghost, self.level.maze, direction)
            if (
                ghost.state == "eaten"
                and ghost.x == ghost.start_x
                and ghost.y == ghost.start_y
            ):
                ghost.state = "chasing"

    def next_level(self) -> None:
        if self.state != "level_complete":
            return
        next_index = self.level_index + 1
        if next_index >= len(self.config.levels):
            self.state = "victory"
            return
        self.level_index = next_index
        self.level_config = self.config.levels[self.level_index]
        self.reset_player_position()
        self.level = Level(self.config, self.level_index, self.player)
        self.move_elapsed = 0.0
        self.ghost_move_elapsed = 0.0
        self.previous_position = (self.player.x, self.player.y)
        self.state = "playing"

    def toggle_pause(self) -> None:
        if self.state == "playing":
            self.state = "paused"
        elif self.state == "paused":
            self.state = "playing"
