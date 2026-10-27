from .maze import Maze
from collections import deque


def find_path(
        maze: Maze,
        start: tuple[int, int] | None,
        target: tuple[int, int]) -> list[str]:

    dq = deque([start])
    visited = {start}
    parent = {start: None}
    directions = {
        "N": (0, -1),
        "E": (1, 0),
        "S": (0, 1),
        "W": (-1, 0)
    }
    moves = {}
    while dq:
        x, y = dq.popleft()
        if (x, y) == target:
            path = []
            while (x, y) != start:
                path.append(moves[(x, y)])
                x, y = parent[(x, y)]
            return path[::-1]
        for direction, (dx, dy) in directions.items():
            if maze.can_move(x, y, direction):
                next_pos = (x + dx, y + dy)
                if next_pos not in visited:
                    visited.add(next_pos)
                    parent[next_pos] = (x, y)
                    moves[next_pos] = direction
                    dq.append(next_pos)

    return []
