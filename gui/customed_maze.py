from mazegenerator import MazeGenerator

from typing import List, Tuple, Self


 
class Cell:
    def __init__(self, x: int, y: int, wall_stat: int) -> Self:
        self.x = x
        self.y = y
        self.wall_stat = wall_stat
        self.cell_volume = 45
        self.x_desplacement = 300
        self.y_desplacement = 200
        self.x_pos = self.cell_volume * self.x + self.x_desplacement
        self.y_pos = self.cell_volume * self.y + self.y_desplacement
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
        end_point = (self.x_pos + self.cell_volume, self.y_pos)
        return start_point, end_point
    
        
    def _get_right_wall_position(self) -> Tuple[Tuple[int, int]]:
        
        start_point = (self.x_pos + self.cell_volume, self.y_pos)
        end_point = (self.x_pos + self.cell_volume, self.y_pos + self.cell_volume)
        return start_point, end_point
    
        
    def _get_buttom_wall_position(self) -> Tuple[Tuple[int, int]]:
        start_point = (self.x_pos, self.y_pos + self.cell_volume)
        end_point = (self.x_pos + self.cell_volume, self.y_pos + self.cell_volume)
        return start_point, end_point
    
        
    def _get_left_wall_position(self) -> Tuple[Tuple[int, int]]:
        
        start_point = (self.x_pos, self.y_pos)
        end_point = (self.x_pos, self.y_pos + self.cell_volume)
        return start_point, end_point
    
    
    
        
    def __str__(self):
        return str(f'x = {self.x} | '
                   f'y = {self.y} | '
                   f'walls status: {self.wall_stat}')
    def __repr__(self):
        return self.__str__()


class OptimazedMaze:
    def __init__(self, maze: MazeGenerator):
        self.maze: List[List[Cell]] = self._get_customized_maze(maze)
        
    def _get_customized_maze(self, maze: List[List[int]]):
        customed_maze = []
        

        for y_index, col in enumerate(maze):
            maze_raw = []
            for x_index, raw in enumerate(col):
                maze_raw.append(Cell(x_index, y_index, raw))
            customed_maze.append(maze_raw)

        return customed_maze