from characters import Player, Ghost, Blinky, Pinky, Inky, Clyde
from maze import Maze
from parsing import Config
from pacgums import (
    place_pacgums,
    place_super_pacgums,
    get_reserved_cells,
    check_pacgum,
    eat_pacgum,
    scare_ghosts,
)
from timer import Timer


class Level:
    def __init__(
            self,
            config: Config,
            level_index: int,
            player: Player) -> None:
        self.config = config
        self.level_config = config.levels[level_index]
        self.player = player
        self.maze = Maze(self.level_config.width,
                         self.level_config.height,
                         self.level_config.seed)
        width = self.level_config.width
        height = self.level_config.height
        self.ghosts: list[Ghost] = [
            Blinky(0, 0, direction="W"),
            Pinky(width - 1, 0, direction="E"),
            Inky(0, height - 1, direction="N"),
            Clyde(width - 1, height - 1, direction="S")
        ]
        self.super_pacgums = place_super_pacgums(width, height)
        reserved = get_reserved_cells(self.player, self.ghosts, width, height)
        self.pacgums = place_pacgums(reserved, config, self.maze, self.player)
        self.timer = Timer(self.level_config.level_max_time)
        self.scared_timer = 7.0
        self.ghosts_scared = False

    def handle_pacgums(self) -> None:
        position = (self.player.x, self.player.y)
        pacgum_type = check_pacgum(position, self.pacgums, self.super_pacgums)
        if pacgum_type == 0:
            return
        eat_pacgum(self.player, position, pacgum_type,
                   self.pacgums, self.super_pacgums, self.config)
        if pacgum_type == 2:
            scare_ghosts(self.ghosts)
            self.ghosts_scared = True
            self.scared_timer = 7.0

    def update_scared_timer(self, dt: float) -> None:
        if not self.ghosts_scared:
            return
        self.scared_timer -= dt
        if self.scared_timer <= 0:
            self.scared_timer = 0.0
            self.ghosts_scared = False
            for ghost in self.ghosts:
                if ghost.state == "scared":
                    ghost.state = "chasing"

    def update(self, dt: float) -> None:
        self.timer.update(dt)
        self.update_scared_timer(dt)

    @property
    def completed(self) -> bool:
        return not self.pacgums and not self.super_pacgums

    @property
    def time_expired(self) -> bool:
        return self.timer.finished
