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
    def __init__(self, screen_size: Tuple[int, int],
                 maze_background_pos: Tuple[int, int], 
                 maze_background_size: Tuple[int, int],
                 menu_pos: Tuple[int, int],
                 menu_size: Tuple[int, int]):
        self.width, self.hight = screen_size
        self.background_x, self.background_y = maze_background_pos
        self.background_w, self.background_h = maze_background_size
        self.menu_x, self.menu_y = menu_pos
        self.menu_w, self.menu_h = menu_size
 
class StartGame(ButtonAction):
    
    def __init__(self, screen, background, engine: GameEngine):
        super().__init__(screen, background)
        self._engine = engine
        self.expected_img_size: Tuple[int, int] = (40, 40)
        self.animation_speed = 100
        self._screen_info = self._get_screen_info()
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
    
    def _get_top_left_frames(self):
        return {
            'corner': DrawImgsFrames('assets/maze/walls/corners/wall_top_left_corner',
                                     self.screen, self.animation_speed,
                                     self.expected_img_size, True),
            'end_left': DrawImgsFrames('assets/maze/walls/ends/wall_end_left',
                                     self.screen, self.animation_speed,
                                     self.expected_img_size, True)
        }
        
    def _get_cornes_frames(self) -> Dict[str, DrawImgsFrames]:
        return {
            'bottom_left': DrawImgsFrames(
                'assets/sci_fi_game_assets/maze/walls/corners/wall_bottom_left_corner',
                self.screen, 150, self.expected_img_size, False),
            'bottom_right': DrawImgsFrames(
                'assets/sci_fi_game_assets/maze/walls/corners/wall_bottom_right_corner',
                self.screen, 150, self.expected_img_size, False),
            'top_left': DrawImgsFrames(
                'assets/sci_fi_game_assets/maze/walls/corners/wall_top_left_corner',
                self.screen, 150, self.expected_img_size, False),
            'top_right': DrawImgsFrames(
                'assets/sci_fi_game_assets/maze/walls/corners/wall_top_right_corner',
                self.screen, 150, self.expected_img_size, False),
        }      
    def start(self, events: List[pg.Event]):
        self.screen.fill((2, 1, 36))
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
        
        
    def _get_screen_info(self) -> ScreenInfo:
        screen_w, screen_h = self.screen.get_size()
        
        back_left = screen_w * 5 // 100
        back_top = screen_h * 10 // 100
        
        final_width = screen_w * 60 // 100
        final_hight = screen_h * 80 // 100
        
        menu_x = screen_w * 75 // 100
        menu_y = back_top
        menu_w = screen_w * 20 // 100
        menu_h = final_hight
        return ScreenInfo((screen_w, screen_h),
                          (back_left, back_top),
                          (final_width, final_hight),
                          (menu_x, menu_y),
                          (menu_w, menu_h))
        
    def draw_maze_background(self):
        back_left = self._screen_info.background_x
        back_top = self._screen_info.background_y
        final_width = self._screen_info.background_w
        final_hight = self._screen_info.background_h
        
        now = pg.time.get_ticks()
        if now - self.time >= 1:
            if self.maze_backg_curr_width < final_width:
                self.maze_backg_curr_width += final_width // 10
            if self.maze_backg_curr_hight < final_hight:
                self.maze_backg_curr_hight += final_hight // 10
                
            if self.menu_backg_curr_width < self._screen_info.menu_w:
                self.menu_backg_curr_width += self._screen_info.menu_w // 10
            if self.menu_backg_curr_hight < self._screen_info.menu_h:
                self.menu_backg_curr_hight += self._screen_info.menu_h // 10
            self.time = pg.time.get_ticks()
        
        pg.draw.rect(self.screen,
                     (0, 0, 70),
                     pg.Rect(self._screen_info.menu_x,
                             self._screen_info.menu_y,
                             self.menu_backg_curr_width,
                             self.menu_backg_curr_hight),
                     0, 100)
      
        pg.draw.rect(self.screen,
                     (0, 0, 70),
                     pg.Rect(back_left,
                             back_top,
                             self.maze_backg_curr_width,
                             self.maze_backg_curr_hight),
                     0, 150)

        pg.draw.rect(self.screen,
                    (110, 0, 70),
                    pg.Rect(back_left,
                            back_top,
                            self.maze_backg_curr_width,
                            self.maze_backg_curr_hight),
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
