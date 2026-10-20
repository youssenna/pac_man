class Player:
    def __init__(self, x: int, y: int, lives: int,
                 direction: str = "W"):
        self.x = x
        self.y = y
        self.direction = direction
        self.score = 0
        self.lives = lives
        self.next_direction = direction

    def respawn(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.direction = "W"
        self.next_direction = "W"


class Ghost:
    def __init__(
            self,
            x: int,
            y: int,
            direction: str,
            state: str = "chasing"):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.previous_x = x
        self.previous_y = y
        self.direction = direction
        self.state = state


class Blinky(Ghost):
    def __init__(self, x: int, y: int, direction: str):
        super().__init__(x, y, direction)
        self.name = "Blinky"


class Pinky(Ghost):
    def __init__(self, x: int, y: int, direction: str):
        super().__init__(x, y, direction)
        self.name = "Pinky"


class Inky(Ghost):
    def __init__(self, x: int, y: int, direction: str):
        super().__init__(x, y, direction)
        self.name = "Inky"


class Clyde(Ghost):
    def __init__(self, x: int, y: int, direction: str):
        super().__init__(x, y, direction)
        self.name = "Clyde"
