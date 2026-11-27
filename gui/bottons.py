from abc import ABC, abstractmethod
from typing import List, Tuple, Self, Dict

from .animated_png_frames import DrawImgsFrames
from .customed_maze import OptimazedMaze, Cell
from .characters import Player, Ghost, Pallet
from .game_info import GameInfo

from backend import GameEngine, LevelConfig
import pygame as pg
import gif_pygame as gif_pg


from mazegenerator import MazeGenerator


class ButtonAction(ABC):
    def __init__(self, screen: pg.Surface, fram_obj: DrawImgsFrames):
        self.screen: pg.Surface = screen
        self.background: DrawImgsFrames = fram_obj
        
    def set_background(self):
        self.background.update_and_draw_frame()
   
    @abstractmethod
    def run(self, events: List[pg.Event]):
        pass
      
      

       
class Game:
    def __init__(self, screen: pg.Surface, engine: GameEngine):
        self._screen = screen
        self._engine = engine
        self.maze_screen_x = 64
        self.maze_screen_y = 65
        self.maze_screen_w = 840
        self.maze_screen_h = 520
        self.maze_screen_pos = self.maze_screen_x, self.maze_screen_y
        self.maze_screen_size = self.maze_screen_w, self.maze_screen_h
        self.maze_screen = pg.Surface((self.maze_screen_w, self.maze_screen_h))
        
        self.menu_screen_x = 955
        self.menu_screen_y = 65
        self.menu_screen_w = 280
        self.menu_screen_h = 520
        self.menu_screen_pos = self.menu_screen_x, self.menu_screen_y
        self.menu_screen_size = self.menu_screen_w, self.menu_screen_h
        self.menu_screen = pg.Surface((self.menu_screen_w, self.menu_screen_h))
        
        self.maze_background_w, self.maze_background_h = 0, 0
        self.menu_background_w, self.menu_background_h = 0, 0
        
        self.maze_background_color = (0, 0, 70)
        self.menu_background_color = (110, 0, 70)

        self.maze_rect = self._get_rect(0, 0, 0, 0)
        self.menu_rect = self._get_rect(0, 0, 0, 0)
        
        self.create_new_maze = True
        
    def _get_rect(self, x, y, w, h) -> pg.Rect:
        return pg.Rect(x, y, w, h)
    
    def update_maze_background(self, dt: float):
        self.maze_background_w = min(
            self.maze_background_w + 2000 * dt,
            self.maze_screen_w - 40
        )

        self.maze_background_h = min(
            self.maze_background_h + 1000 * dt,
            self.maze_screen_h - 20
        )

        self.maze_rect = self._get_rect(20, 10, self.maze_background_w, self.maze_background_h)

    def update_menu_background(self, dt: float):
        self.menu_background_w = min(
            self.menu_background_w + 500 * dt,
            self.menu_screen_w - 20
        )
        self.menu_background_h = min(
            self.menu_background_h + 1000 * dt,
            self.menu_screen_h - 20
        )

        self.menu_rect = self._get_rect(10, 10, self.menu_background_w, self.menu_background_h)
        
    def draw_maze_background(self):
        pg.draw.rect(self.maze_screen, self.maze_background_color, self.maze_rect, 0, 20)

    def draw_menu_background(self):
        pg.draw.rect(self.menu_screen, self.menu_background_color, self.menu_rect, 0, 20)
        
    def reset_background_animation(self):
        self.maze_background_w = 0
        self.maze_background_h = 0
        self.menu_background_w = 0
        self.menu_background_h = 0
        
    @staticmethod
    def _get_maze_from_mazegenerator(width: int, height: int, seed: int) -> List[List[int]]:
        maze_obj = MazeGenerator((width, height), seed=seed)
        return maze_obj.maze
        
    def get_optomized_maze(self, width: int, height: int, seed: int,
                           cell_volume_w: float, cell_volume_h: float,
                           x_dep: int, y_dep: int) -> List[List[Cell]]:
        maze = self._get_maze_from_mazegenerator(width, height, seed)
        maze_obj: OptimazedMaze = OptimazedMaze(maze, cell_volume_w,
                                                cell_volume_h, x_dep, y_dep)
        return maze_obj.maze

    def render_maze(self):
        if self.create_new_maze:
            width = self._engine.level_config.width
            height = self._engine.level_config.height
            seed = self._engine.level_config.seed
            # print(width, height)
            cell_volume_w = (self.maze_screen_w - 80) / width
            cell_volume_h = (self.maze_screen_h - 60) / height
            # print(cell_volume_w, cell_volume_h)
            self.maze: List[List[Cell]] = self.get_optomized_maze(width,
                                                                  height,
                                                                  seed,
                                                                  cell_volume_w,
                                                                  cell_volume_h,
                                                                  x_dep=40,
                                                                  y_dep=30)
            self.create_new_maze= False
        # print((self.maze_screen_w ))
        walls_out_color = (0, 200, 255, 60)
        closed_cell_color = (20, 40, 160)
        for raw in self.maze:
            for cell in raw:
                # cell.cell_volume_w = cell_volume_w
                # cell.cell_volume_h = cell_volume_h
                if (cell.top_wall() and cell.buttom_wall() and cell.right_wall() and cell.left_wall()):
                    pg.draw.rect(self.maze_screen, closed_cell_color, pg.Rect(cell.x_pos, cell.y_pos, cell.cell_volume_w, cell.cell_volume_h))
                if not cell.top_wall() and not cell.left_wall():
                    s, _ = cell.top_wall_pos
                    
                    pg.draw.circle(self.maze_screen, walls_out_color, s, 5)
                if not cell.buttom_wall() and not cell.left_wall():
                    _, e = cell.top_wall_pos
                    
                    pg.draw.circle(self.maze_screen, walls_out_color, e, 5)
                if cell.top_wall():
                    s, e = cell.top_wall_pos
                    s_x, s_y  = s
                    e_x, e_y = e
                    pg.draw.line(self.maze_screen, walls_out_color, (s_x, s_y), (e_x, e_y), 5)
                if cell.buttom_wall():
                    
                    s, e = cell.buttom_wall_pos
                    s_x, s_y  = s
                    e_x, e_y = e
                    
                    pg.draw.line(self.maze_screen, walls_out_color, (s_x, s_y), (e_x, e_y), 5)
                if cell.right_wall():
                    s, e = cell.right_wall_pos
                    s_x, s_y  = s
                    e_x, e_y = e
                    pg.draw.line(self.maze_screen, walls_out_color, (s_x, s_y), (e_x, e_y), 4)
                if cell.left_wall():
                    s, e = cell.left_wall_pos
                    s_x, s_y  = s
                    e_x, e_y = e
                    pg.draw.line(self.maze_screen, walls_out_color, (s_x, s_y), (e_x, e_y), 5)
        
        
        
    def blit_screens(self, screen: pg.Surface, dt: float):
        self.maze_screen.fill('red')
        self.menu_screen.fill('red')
        self.update_maze_background(dt)
        self.update_menu_background(dt)
        self.draw_maze_background()
        self.draw_menu_background()
        self.render_maze()
        screen.blit(self.maze_screen, self.maze_screen_pos)
        screen.blit(self.menu_screen, self.menu_screen_pos)

        
        
 
class StartGame(ButtonAction):
    
    def __init__(self, screen, background, engine: GameEngine):
        super().__init__(screen, background)
        self._game_screens = Game(self.screen, engine)
        self.generate_new_maze = False

    
    def run(self, events: List[pg.Event], dt: float):
        self.screen.fill((2, 1, 36))
        self._game_screens.blit_screens(self.screen, dt)
    
class Heighscores(ButtonAction):
    def show_heighscores(self, events: List[pg.Event]):
        print('show heighscores.')
        
    def run(self, events: List[pg.Event]):
        self.show_heighscores(events)
    
class Instractions(ButtonAction):
    def show_instractions(self, events: List[pg.Event]):
        print('show instractions.')

    def run(self, events: List[pg.Event]):
        self.show_instractions(events)
    
class Exit(ButtonAction):
    def exit_game(self, events: List[pg.Event]):
        print('exit game.')
    
    def run(self, events: List[pg.Event]):
        self.exit_game(events)
