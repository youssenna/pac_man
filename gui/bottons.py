from abc import ABC, abstractmethod
from typing import List, Tuple, Self, Dict

from .animated_png_frames import DrawImgsFrames
from .customed_maze import OptimazedMaze
from .characters import Player, Ghost, Pallet
from .game_info import GameInfo

import pygame as pg
import gif_pygame as gif_pg

class ButtonAction(ABC):
    def __init__(self, screen: pg.Surface, fram_obj: DrawImgsFrames):
        self.screen: pg.Surface = screen
        self.background: DrawImgsFrames = fram_obj
        
    def set_background(self):
        self.background.update_and_draw_frame()
   
    @abstractmethod
    def run(self, events: List[pg.Event]):
        pass
      
 
class StartGame(ButtonAction):
    
    def __init__(self, screen, background, maze: List[List[int]]):
        super().__init__(screen, background)
        self.expected_img_size: Tuple[int, int] = (40, 40)
        self.animation_speed = 100
        self.customized_maze_obj: OptimazedMaze = OptimazedMaze(maze)
        self.maze = self.customized_maze_obj.maze
        self.background__ = gif_pg.load("assets/background3.gif")
        self.player = Player(screen, self.maze[10][10], 'assets/pacman_sprites/pacman', (30, 30), 20, self.maze, padding=7)
        self.green = Ghost(screen, self.maze[0][1], 'assets/pacman_sprites/ghosts/green', (30, 30), 20, self.maze, padding=7)
        self.red = Ghost(screen, self.maze[0][13], 'assets/pacman_sprites/ghosts/red', (30, 30), 20, self.maze, padding=7)
        self.orange = Ghost(screen, self.maze[13][0], 'assets/pacman_sprites/ghosts/orange', (30, 30), 20, self.maze, padding=7)
        self.pink = Ghost(screen, self.maze[13][13], 'assets/pacman_sprites/ghosts/pink', (30, 30), 20, self.maze, padding=7)
        self.super_pallet = Pallet(screen, self.maze[0][0], 'assets/pacman_sprites/pellets/super_pallet', (30, 30), 500, self.maze, padding=7)
        
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
        self.screen.blit(pg.transform.scale(self.background__.blit_ready(), (1280, 800)))
        
        # self.set_background()
        self.draw_maze_background()
        self.draw_maze()
        
        self.player.move(events)
        self.pink.move()
        self.red.move()
        self.orange.move()
        self.green.move()
        self.super_pallet.draw_pallet(0, 0)
        self.super_pallet.draw_pallet(0, 14)
        self.super_pallet.draw_pallet(14, 0)
        self.super_pallet.draw_pallet(14, 14)
        
        
    def draw_maze_background(self):
        # pg.draw.rect(self.screen, (10, 4, 87), pg.Rect(self.maze[0][0].x_pos, self.maze[0][0].y_pos, self.maze[0][0].cell_volume * 15, self.maze[0][0].cell_volume * 15))
        pg.draw.rect(self.screen, (10, 4, 87), pg.Rect(self.screen.get_size()[0] *10/100, self.screen.get_size()[1] *15/100, self.screen.get_size()[0] *80/100, self.screen.get_size()[1] * 80/100))

    def draw_maze(self):
        walls_out_color = (0, 200, 255, 60)
        closed_cell_color = (20, 40, 160)
        for raw in self.maze:
            for cell in raw:
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
