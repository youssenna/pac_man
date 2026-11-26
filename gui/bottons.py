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
      
      
class MazeRendring:
    def __init__(self, screen: pg.Surface, engine: GameEngine, maze: List[List[Cell]]):
        self._screen = screen
        self._engine = engine
        self._maze = maze
        
    def render(self) -> None:
        pass
        # start_position = 
       
class ScreenInfo:
    def __init__(self):
        self.maze_screen = pg.Surface((840, 520))
        self.maze_screen_pos = 64, 65
        self.menu_screen = pg.Surface((280, 520))
        self.menu_screen_pos = 955, 65
        
        self.maze_rect = pg.Rect(64, 65, 840, 520)
        self.menu_rect = pg.Rect(955, 65, 280, 520)
        
    def blit_screens(self, screen: pg.Surface):
        self.maze_screen.fill('red')
        self.menu_screen.fill('red')
        screen.blit(self.maze_screen, self.maze_screen_pos)
        screen.blit(self.menu_screen, self.menu_screen_pos)
        
        
        
 
class StartGame(ButtonAction):
    
    def __init__(self, screen, background, engine: GameEngine):
        super().__init__(screen, background)
        self._engine = engine
        self._game_screens = ScreenInfo()
        self.animation_speed = 100
        
        # self.original_maze = self._get_maze_from_mazegenerator()
        # self.customized_maze_obj: OptimazedMaze = OptimazedMaze(self.original_maze)
        # self.maze = self.customized_maze_obj.maze
        self.time = pg.time.get_ticks()
        self.maze_backg_curr_width = 0
        self.maze_backg_curr_hight = 0
        self.menu_backg_curr_width = 0
        self.menu_backg_curr_hight = 0
        self.background__ = gif_pg.load("assets/background3.gif")
        # self.player = Player(screen, self.maze[0][0], 'assets/pacmites/ghosts/green', (30, 30), 20, self.maze, padding=7)
        # self.red = Ghost(screen, self.maze[0][1], 'assets/pacman_sprian_sprites/pacman', (30, 30), 20, self.maze, padding=7)
        # self.green = Ghost(screen, self.maze[0][1], 'assets/pacman_sprtes/ghosts/red', (30, 30), 20, self.maze, padding=7)
        # self.orange = Ghost(screen, self.maze[3][0], 'assets/pacman_sprites/ghosts/orange', (30, 30), 20, self.maze, padding=7)
        # self.pink = Ghost(screen, self.maze[1][3], 'assets/pacman_sprites/ghosts/pink', (30, 30), 20, self.maze, padding=7)
        # self.super_pallet = Pallet(screen, self.maze[1][0], 'assets/pacman_sprites/pellets/super_pallet', (30, 30), 500, self.maze, padding=7)
        
            
    @staticmethod
    def _get_maze_from_mazegenerator(current_level: LevelConfig):
        maze_obj = MazeGenerator((current_level.width,
                                  current_level.height),
                                 seed=current_level.seed)
        return maze_obj.maze
    
    
    def start(self, events: List[pg.Event]):
        self.screen.fill((2, 1, 36))
        self._game_screens.blit_screens(self.screen)
        # self.screen.blit(pg.transform.scale(self.background__.blit_ready(), (1280, 800)))
        
        # self.set_background()
        self.draw_maze_background()
        current_level = self._engine.level_config
        original_maze = self._get_maze_from_mazegenerator(current_level)
        maze_obj = OptimazedMaze(original_maze)
        maze_render = MazeRendring(self.screen, self._engine, maze_obj.maze)
        maze_render.render()
        
        # self.draw_maze()
        
        # self.player.move(events)
        # self.pink.move()
        # self.red.move()
        # self.orange.move()
        # self.green.move()
        # self.super_pallet.draw_pallet(0, 0)
        # self.super_pallet.draw_pallet(0, 14)
        # self.super_pallet.draw_pallet(14, 0)
        # self.super_pallet.draw_pallet(14, 14)
        
        
        
    def draw_maze_background(self):
        
        now = pg.time.get_ticks()
        if now - self.time >= 1:
            if self.maze_backg_curr_width < self._game_screens.maze_screen.get_size()[0]:
                self.maze_backg_curr_width += 10
            if self.maze_backg_curr_hight < self._game_screens.maze_screen.get_size()[1]:
                self.maze_backg_curr_hight += 10
                
            if self.menu_backg_curr_width < self._game_screens.menu_screen.get_size()[0]:
                self.menu_backg_curr_width += 10
            if self.menu_backg_curr_hight < self._game_screens.menu_screen.get_size()[1]:
                self.menu_backg_curr_hight += 10
            self.time = pg.time.get_ticks()
        # print(final_width)
        
        pg.draw.rect(self.screen,
                     (0, 0, 70),
                     self._game_screens.menu_rect,
                     0, 100)
      
        pg.draw.rect(self.screen,
                     (0, 0, 70),
                     self._game_screens.maze_rect,
                     0, 150)

        pg.draw.rect(self.screen,
                    (110, 0, 70),
                    self._game_screens.maze_rect,
                    5, 150)

    def draw_maze(self):
        cell_volume = 500 / min(self._engine.level_config.width, self._engine.level_config.height)
        walls_out_color = (0, 200, 255, 60)
        closed_cell_color = (20, 40, 160)
        for raw in self.maze:
            for cell in raw:
                cell.cell_volume = cell_volume
                print(cell_volume)
                if (cell.top_wall() and cell.buttom_wall() and cell.right_wall() and cell.left_wall()):
                    pg.draw.rect(self.screen, closed_cell_color, pg.Rect(cell.x_pos, cell.y_pos, cell.cell_volume, cell.cell_volume))
                if not cell.top_wall() and not cell.left_wall():
                    s, _ = cell.top_wall_pos
                    
                    pg.draw.circle(self.screen, walls_out_color, s, 5)
                if not cell.buttom_wall() and not cell.left_wall():
                    _, e = cell.top_wall_pos
                    
                    pg.draw.circle(self.screen, walls_out_color, e, 5)
                if cell.top_wall():
                    s, e = cell.top_wall_pos
                    s_x, s_y  = s
                    e_x, e_y = e
                    # pygame.draw.circle(self.screen, walls_out_color, (s_x, s_y), 5, 4)
                    # pygame.draw.circle(self.screen, walls_out_color, (s_x + 15, s_y), 5, 4)
                    # pygame.draw.circle(self.screen, walls_out_color, (s_x + 30, s_y), 5, 4)
                    # pygame.draw.circle(self.screen, walls_out_color, (s_x, s_y), 5)
                    pg.draw.line(self.screen, walls_out_color, (s_x, s_y), (e_x, e_y), 5)
                    # pg.draw.line(self.screen, walls_in_color, (s_x, s_y), (e_x, e_y), 4)
                    # pg.draw.line(self.screen, walls_in_color, (s_x, s_y), (e_x, e_y), 5)
                if cell.buttom_wall():
                    
                    s, e = cell.buttom_wall_pos
                    s_x, s_y  = s
                    e_x, e_y = e
                    # pygame.draw.circle(self.screen, walls_out_color, (s_x, s_y), 5, 4)
                    # pygame.draw.circle(self.screen, walls_out_color, (s_x + 15, s_y), 5, 4)
                    # pygame.draw.circle(self.screen, walls_out_color, (s_x + 30, s_y), 5, 4)
                    
                    pg.draw.line(self.screen, walls_out_color, (s_x, s_y), (e_x, e_y), 5)
                    # pg.draw.line(self.screen, walls_in_color, (s_x, s_y), (e_x, e_y), 4)
                    # pg.draw.line(self.screen, walls_in_color, (s_x, s_y), (e_x, e_y), 5)
                if cell.right_wall():
                    s, e = cell.right_wall_pos
                    s_x, s_y  = s
                    e_x, e_y = e
                    # pygame.draw.circle(self.screen, walls_out_color, (s_x, s_y), 5, 4)
                    # pygame.draw.circle(self.screen, walls_out_color, (s_x, s_y + 15), 5, 4)
                    # pygame.draw.circle(self.screen, walls_out_color, (s_x, s_y + 30), 5, 4)
                    # pygame.draw.circle(self.screen, walls_out_color, (s_x, s_y + 45), 5, 4)
                    # pygame.draw.circle(self.screen, walls_out_color, (s_x, s_y + 30), 5)
                    pg.draw.line(self.screen, walls_out_color, (s_x, s_y), (e_x, e_y), 4)
                    # pg.draw.line(self.screen, walls_in_color, (s_x, s_y), (e_x, e_y), 5)
                if cell.left_wall():
                    s, e = cell.left_wall_pos
                    s_x, s_y  = s
                    e_x, e_y = e
                    # pygame.draw.circle(self.screen, walls_out_color, (s_x, s_y), 5, 4)
                    # pygame.draw.circle(self.screen, walls_out_color, (s_x, s_y + 15), 5, 4)
                    # pygame.draw.circle(self.screen, walls_out_color, (s_x, s_y + 30), 5, 4)
                    pg.draw.line(self.screen, walls_out_color, (s_x, s_y), (e_x, e_y), 5)
                    # pg.draw.line(self.screen, walls_in_color, (s_x, s_y), (e_x, e_y), 4)
                    # pg.draw.line(self.screen, walls_in_color, (s_x, s_y), (e_x, e_y), 5)
        
        
        
    
    def run(self, events: List[pg.Event]):
        self.start(events)
    
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
