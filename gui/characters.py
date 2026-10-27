from .animated_png_frames import DrawImgsFrames
from .customed_maze import Cell

from abc import ABC, abstractmethod
from typing import Tuple, List, Dict, Self


import pygame as pg

class Pallet:
    def __init__(self, screen: pg.Surface, cell: Cell, folder_name: str, img_size: Tuple[int, int], speed: int, maze: List[List[Cell]], padding: int = 10):
        self.screen: pg.Surface = screen
        self.cell: Cell = cell
        self.maze: List[List[Cell]] = maze
        self.padding: int = padding
        self.pallets_frames = DrawImgsFrames(folder_name, screen, speed, img_size, False, (cell.x_pos + padding, cell.y_pos + padding))
        
    def draw_pallet(self, x: int, y: int):
        x_pos = self.maze[y][x].x_pos + self.padding
        y_pos = self.maze[y][x].y_pos + self.padding
        self.pallets_frames.update_and_draw_frame_at_pos(x_pos, y_pos)

class Character(ABC):
    def __init__(self, screen: pg.Surface, cell: Cell, imgs_folder: str,
                 image_size: Tuple[int, int], speed: int, maze: List[List[Cell]],
                 maze_size: Tuple[int, int] = (15, 15), padding: int = 10):
        self.screen: pg.Surface = screen
        self.cell: Cell = cell
        self.maze = maze
        self.x, self.y = self.cell.x, self.cell.y
        self.x_pos = self.cell.x_pos
        self.y_pos = self.cell.y_pos
        self.column, self.raw = maze_size
        self.padding: int = padding
        self.frames: Dict[str, DrawImgsFrames] = {
            'up': DrawImgsFrames(imgs_folder + '/up', screen, speed, image_size, False, (self.x_pos + padding, self.y_pos + padding)),
            'right': DrawImgsFrames(imgs_folder + '/right', screen, speed, image_size, False, (self.x_pos + padding, self.y_pos + padding)),
            'down': DrawImgsFrames(imgs_folder + '/down', screen, speed, image_size, False, (self.x_pos + padding, self.y_pos + padding)),
            'left': DrawImgsFrames(imgs_folder + '/left', screen, speed, image_size, False, (self.x_pos + padding, self.y_pos + padding))
        }
        self.direction: str = self._get_direction(cell)
    
    def _get_direction(self, cell: Cell) -> str:
        if not cell.top_wall():
            return 'up'
        elif not cell.left_wall():
            return 'left'
        elif not cell.right_wall():
            return 'right'
        elif not cell.buttom_wall():
            return 'down'
        return 'right'
    
    
    
    def draw_frame(self):
        self.frames[self.direction].update_and_draw_frame_at_pos(self.x_pos + self.padding, self.y_pos + self.padding)
    
    def move_up(self):
        if self.y > 0:
            self.y -= 1
            self.y_pos -= self.cell.cell_volume
            self.cell = self.maze[self.y][self.x]
    
    def move_down(self):
        if self.y < self.raw - 1:
            self.y += 1
            self.y_pos += self.cell.cell_volume
            self.cell = self.maze[self.y][self.x]
    
    def move_right(self):
        if self.x < self.column - 1:
            self.x += 1
            self.x_pos += self.cell.cell_volume
            self.cell = self.maze[self.y][self.x]
    
    def move_left(self):
        if self.x > 0:
            self.x -= 1
            self.x_pos -= self.cell.cell_volume
            self.cell = self.maze[self.y][self.x]
    
    @abstractmethod
    def move(self) -> None:
        pass
    
    
    
class Ghost(Character):
    def move(self):
        self.draw_frame()

class Player(Character):
    def __init__(self, screen, cell, imgs_folder, image_size, speed: int, maze, maze_size = (15, 15), padding = 10):
        super().__init__(screen, cell, imgs_folder, image_size, speed, maze, maze_size, padding)
        self.frames[self.direction].update_and_draw_frame()
        
    def move(self, events: List[pg.Event]):
        keys = pg.key.get_pressed()
        print(self.direction)
        if any([keys[pg.K_DOWN], keys[pg.K_s]]) and not self.cell.buttom_wall():
            self.direction = 'down'
            self.move_down()
        elif any([keys[pg.K_UP], keys[pg.K_w]]) and not self.cell.top_wall():
            self.direction = 'up'
            self.move_up()
        elif any([keys[pg.K_RIGHT], keys[pg.K_d]]) and not self.cell.right_wall():
            self.direction = 'right'
            self.move_right()
        elif any([keys[pg.K_LEFT], keys[pg.K_a]]) and not self.cell.left_wall():
            self.direction = 'left'
            self.move_left()
        self.draw_frame()