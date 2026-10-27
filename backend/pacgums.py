from .parsing import Config
from .characters import Player, Ghost
from .maze import Maze
import random


def place_super_pacgums(width: int, height: int) -> set[tuple[int, int]]:
    return {
        (0, 0),
        (0, height - 1),
        (width - 1, 0),
        (width - 1, height - 1)
    }


def get_reserved_cells(
        player: Player,
        ghosts: list[Ghost],
        width: int,
        height: int,
        ) -> set[tuple[int, int]]:
    reserved = {(player.x, player.y)}
    reserved.update((ghost.x, ghost.y) for ghost in ghosts)
    reserved.update(place_super_pacgums(width, height))

    return reserved


def place_pacgums(
        reserved: set[tuple[int, int]],
        config: Config,
        maze: Maze,
        player: Player,
        ) -> set[tuple[int, int]]:

    reachable = maze.get_reachable_cells((player.x, player.y))
    available = reachable - reserved

    count = min(config.pacgum, len(available))

    return set(random.sample(list(available), count))


def check_pacgum(
        position: tuple[int, int],
        pacgums: set[tuple[int, int]],
        super_pacgums: set[tuple[int, int]]) -> int:
    if position in super_pacgums:
        return 2
    elif position in pacgums:
        return 1
    else:
        return 0


def eat_pacgum(
        player: Player,
        position: tuple[int, int],
        pacgums_type: int,
        pacgums: set[tuple[int, int]],
        super_pacgums: set[tuple[int, int]],
        config: Config) -> None:
    if pacgums_type == 2:
        player.score += config.points_per_super_pacgum
        super_pacgums.remove(position)
    elif pacgums_type == 1:
        player.score += config.points_per_pacgum
        pacgums.remove(position)
    else:
        return


def scare_ghosts(ghosts: list[Ghost]) -> None:
    for ghost in ghosts:
        if ghost.state != "eaten":
            ghost.state = "scared"
