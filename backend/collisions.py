from .characters import Player, Ghost
from .parsing import Config


def check_collision(
        width: int,
        height: int,
        player: Player,
        ghost: Ghost,
        config: Config) -> None:
    if player.x != ghost.x or player.y != ghost.y:
        return
    if ghost.state == "eaten":
        return
    if ghost.state == "scared":
        player.score += config.points_per_ghost
        ghost.state = "eaten"
    else:
        player.lives -= 1
        player.respawn(width // 2, height // 2)


def check_ghosts_collision(
        width: int,
        height: int,
        player: Player,
        ghosts: list[Ghost],
        config: Config) -> None:

    for ghost in ghosts:
        check_collision(width, height, player, ghost, config)
        if player.lives <= 0:
            return
