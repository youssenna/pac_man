from mazegenerator import MazeGenerator

from typing import List, Tuple, Self


 
class Cell:
    def __init__(self, x: int, y: int, wall_stat: int,
                 cell_volume_w: float, cell_volume_h: float,
                 x_dep: int, y_dep: int) -> Self:
        self.x = x
        self.y = y
        self.wall_stat = wall_stat
        self.cell_volume_w = cell_volume_w
        self.cell_volume_h = cell_volume_h
        print(cell_volume_w, cell_volume_h)
        self.x_desplacement = x_dep
        self.y_desplacement = y_dep
        self.x_pos = self.cell_volume_w * self.x + self.x_desplacement
        self.y_pos = self.cell_volume_h * self.y + self.y_desplacement
        self.top_wall_pos: Tuple[Tuple[int, int]] = self._get_top_wall_position()
        self.right_wall_pos: Tuple[Tuple[int, int]] = self._get_right_wall_position()
        self.buttom_wall_pos: Tuple[Tuple[int, int]] = self._get_buttom_wall_position()
        self.left_wall_pos: Tuple[Tuple[int, int]] = self._get_left_wall_position()
        
        
    def top_wall(self) -> bool:
            return self.wall_stat & 1
        
    def left_wall(self) -> bool:
            return self.wall_stat & 8
        
        
    def buttom_wall(self) -> bool:
            return self.wall_stat & 4
        
    def right_wall(self) -> bool:
            return self.wall_stat & 2
    
    def _get_top_wall_position(self) -> Tuple[Tuple[int, int]]:
        start_point = (self.x_pos, self.y_pos)
        end_point = (self.x_pos + self.cell_volume_w, self.y_pos)
        return start_point, end_point
    
        
    def _get_right_wall_position(self) -> Tuple[Tuple[int, int]]:
        
        start_point = (self.x_pos + self.cell_volume_w, self.y_pos)
        end_point = (self.x_pos + self.cell_volume_w, self.y_pos + self.cell_volume_h)
        return start_point, end_point
    
        
    def _get_buttom_wall_position(self) -> Tuple[Tuple[int, int]]:
        start_point = (self.x_pos, self.y_pos + self.cell_volume_h)
        end_point = (self.x_pos + self.cell_volume_w, self.y_pos + self.cell_volume_h)
        return start_point, end_point
    
        
    def _get_left_wall_position(self) -> Tuple[Tuple[int, int]]:
        
        start_point = (self.x_pos, self.y_pos)
        end_point = (self.x_pos, self.y_pos + self.cell_volume_h)
        return start_point, end_point
    
    
    
        
    def __str__(self):
        return str(f'x = {self.x} | '
                   f'y = {self.y} | '
                   f'walls status: {self.wall_stat}')
    def __repr__(self):
        return self.__str__()


class OptimazedMaze:
    def __init__(self, maze: MazeGenerator, cell_volume_w: float,
                 cell_volume_h: float, x_dep: int, y_dep: int):
        self._cell_volume_w = cell_volume_w
        self._cell_volume_h = cell_volume_h
        self._x_dep = x_dep
        self._y_dep = y_dep
        self.maze: List[List[Cell]] = self._get_customized_maze(maze)

    def _get_customized_maze(self, maze: List[List[int]]) -> List[List[Cell]]:
        customed_maze: List[List[Cell]] = []
        

        for y_index, col in enumerate(maze):
            maze_raw: List[Cell] = []
            for x_index, raw in enumerate(col):
                maze_raw.append(Cell(x_index, y_index, raw,
                                     self._cell_volume_w,
                                     self._cell_volume_h,
                                     self._x_dep,
                                     self._y_dep))
            customed_maze.append(maze_raw)

        return customed_maze