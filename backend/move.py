from .maze import Maze
from .characters import Player, Ghost


def move_character(
        character: Player | Ghost, maze: Maze, direction: str) -> None:
    if direction == "":
        return
    if maze.can_move(character.x, character.y, direction):
        moves = {
            "N": (0, -1),
            "E": (1, 0),
            "S": (0, 1),
            "W": (-1, 0),
        }

        dx, dy = moves[direction]
        character.x += dx
        character.y += dy
        character.direction = direction


def decide_next_move(player: Player, maze: Maze) -> str:
    if player.next_direction and maze.can_move(
            player.x, player.y, player.next_direction):
        player.direction = player.next_direction
        return player.direction
    if player.direction and maze.can_move(
            player.x, player.y, player.direction):
        return player.direction
    return ""
