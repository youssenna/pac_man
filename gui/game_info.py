from backend.parsing import Config, LevelConfig
from typing import Tuple, Self, List

class GameInfo:
    def __init__(self, config: Config, screen_size: Tuple[int, int]) -> Self:
        self.conf: Config = config
        self.screen_w, self.screen_h = screen_size
        # self._cell_volume = self.cell_volume
        
    # @property
    # def cell_volume(self) -> int:
    #     return self._cell_volume
    
    # @cell_volume.setter
    # def cell_volume(self) -> None:
    #     min_size = min(self.screen_w, self.screen_h)
    #     self._cell_volume = (min_size * 80) // 100
    def get_cell_volume(self, level: int) -> Tuple[int, int]:
        columns = self.conf.levels[level].width 
        raws = self.conf.levels[level].height
        # maze_width = 