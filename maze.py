from mazegenerator.mazegenerator import MazeGenerator
from collections import deque


class Maze:
    BITS = {
        "N": 1,
        "E": 2,
        "S": 4,
        "W": 8,
    }

    def __init__(self, width: int, height: int, seed: int) -> None:
        generator = MazeGenerator(size=(width, height), seed=seed)
        self.maze = generator.maze

    def can_move(self, x: int, y: int, direction: str) -> bool:
        return self.maze[y][x] & self.BITS[direction] == 0

    def get_reachable_cells(
            self, start: tuple[int, int]) -> set[tuple[int, int]]:

        queue = deque([start])
        visited = {start}

        directions = {
            "N": (0, -1),
            "E": (1, 0),
            "S": (0, 1),
            "W": (-1, 0),
        }

        height = len(self.maze)
        width = len(self.maze[0])

        while queue:
            x, y = queue.popleft()

            for direction, (dx, dy) in directions.items():
                nx, ny = x + dx, y + dy

                if not (0 <= nx < width and 0 <= ny < height):
                    continue

                if (nx, ny) in visited:
                    continue

                if self.can_move(x, y, direction):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        return visited
