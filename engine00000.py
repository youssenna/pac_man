from characters import Player, Ghost
from maze import Maze
from move import move_character, decide_next_move
from parsing import Config
from pacgums import (
    place_pacgums,
    place_super_pacgums,
    get_reserved_cells,
    check_pacgum,
    eat_pacgum,
    scare_ghosts,
)


class GameEngine:
    def __init__(self, player: Player, maze: Maze,
                 config: Config, ghosts: list[Ghost], move_interval=0.15):
        self.player = player
        self.maze = maze
        self.config = config
        self.ghosts = ghosts
        self.move_interval = move_interval
        self.move_elapsed = 0.0
        self.previous_position = (player.x, player.y)
        width = config.levels.width
        height = config.levels.height
        self.super_pacgums = place_super_pacgums(width, height)
        reserved = get_reserved_cells(player, ghosts, width, height)
        self.pacgums = place_pacgums(reserved, config, maze, player)
        self.scared_timer = 0.0
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
            self.scared_timer = 5.0
            self.ghosts_scared = True

    def update_scared_timer(self, dt: float) -> None:
        if not self.ghosts_scared:
            return
        self.scared_timer -= dt
        if self.scared_timer <= 0:
            self.scared_timer = 0.0
            self.ghosts_scared = False
            for ghost in self.ghosts:
                if ghost.state != "eaten":
                    ghost.state = "chasing"

    def update(self, dt: float) -> None:
        self.update_scared_timer(dt)
        self.move_elapsed += dt
        while self.move_elapsed >= self.move_interval:
            self.previous_position = (self.player.x, self.player.y)
            direction = decide_next_move(self.player, self.maze)
            move_character(self.player, self.maze, direction)
            self.move_elapsed -= self.move_interval
            if self.previous_position != (self.player.x, self.player.y):
                self.handle_pacgums()
        else:
            return
