class Timer:
    def __init__(self, level_max_time: float):
        self.level_max_time = level_max_time
        self.passed = 0.0

    def update(self, dt: float) -> None:
        self.passed += dt

    @property
    def finished(self) -> bool:
        return self.passed >= self.level_max_time

    def reset(self) -> None:
        self.passed = 0.0
