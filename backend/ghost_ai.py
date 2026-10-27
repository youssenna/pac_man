from .maze import Maze
from .pathfinding import find_path
from .characters import Player, Ghost, Blinky, Pinky, Inky, Clyde
import random


def decide_blinky_move(blinky: Ghost, player: Player, maze: Maze) -> str:
    start = (blinky.x, blinky.y)
    target = (player.x, player.y)

    path = find_path(maze, start, target)

    if not path:
        return ""

    return path[0]


def decide_pinky_move(
        pinky: Pinky,
        player: Player, maze: Maze, width: int, height: int) -> str:
    directions = {
        "N": (0, -1),
        "E": (1, 0),
        "S": (0, 1),
        "W": (-1, 0)
    }
    start = (pinky.x, pinky.y)
    dx, dy = directions[player.direction]
    tx = player.x + (dx * 4)
    ty = player.y + (dy * 4)

    tx = max(0, min(tx, width - 1))
    ty = max(0, min(ty, height - 1))
    target = (tx, ty)

    if start == target:
        return decide_blinky_move(pinky, player, maze)

    path = find_path(maze, start, target)

    if not path:
        target = (player.x, player.y)
        path = find_path(maze, start, target)

    if not path:
        return ""

    return path[0]


def decide_random_move(ghost: Ghost, maze: Maze) -> str:
    directions = ["N", "E", "S", "W"]

    opposites = {
        "N": "S",
        "S": "N",
        "E": "W",
        "W": "E",
    }

    available_moves = [
        direction for direction in directions
        if maze.can_move(ghost.x, ghost.y, direction)]

    if not available_moves:
        return ""

    opposite_direction = opposites[ghost.direction]

    valid_moves = [
        direction for direction in available_moves
        if direction != opposite_direction]

    if not valid_moves:
        valid_moves = available_moves

    return random.choice(valid_moves)


def decide_inky_move(inky: Inky, maze: Maze) -> str:
    return decide_random_move(inky, maze)


def decide_clyde_move(
        clyde: Clyde,
        player: Player, maze: Maze, width: int, height: int) -> str:

    start = (clyde.x, clyde.y)
    target = (player.x, player.y)
    corner = (width - 1, height - 1)

    path = find_path(maze, start, target)

    if len(path) < 5:
        path = find_path(maze, start, corner)

    if path:
        return path[0]

    return decide_blinky_move(clyde, player, maze)


def decide_ghost_move(
        ghost: Ghost,
        player: Player, maze: Maze, width: int, height: int) -> str:
    if ghost.state == "chasing":
        if isinstance(ghost, Blinky):
            return decide_blinky_move(ghost, player, maze)
        elif isinstance(ghost, Pinky):
            return decide_pinky_move(ghost, player, maze, width, height)
        elif isinstance(ghost, Inky):
            return decide_inky_move(ghost, maze)
        elif isinstance(ghost, Clyde):
            return decide_clyde_move(ghost, player, maze, width, height)
    elif ghost.state == "scared":
        return decide_random_move(ghost, maze)
    elif ghost.state == "eaten":
        start = (ghost.x, ghost.y)
        target = (ghost.start_x, ghost.start_y)
        path = find_path(maze, start, target)
        if not path:
            return ""
        return path[0]

    return ""
