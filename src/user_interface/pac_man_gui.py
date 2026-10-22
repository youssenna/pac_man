import pygame as pg
import pygame_widgets
import glob
import pygame
from pygame_widgets.button import Button
# from pygame_widgets.animations import Resize
# from moviepy.editor import VideoFileClip
from typing import Any, List, Dict, Optional, Tuple, Self, Callable, Union
from mazegenerator import MazeGenerator


from abc import ABC, abstractmethod


        
        
class DrawImgsFrames:
    def __init__(self, folder: str, screen: pg.Surface, speed: int,
                 expected_image_size: Tuple[int, int],
                 backround: bool = True, img_pos: Tuple[int, int] = (0, 0)):
        self.screen = screen
        self.speed = speed
        self.img_h, self.img_w = expected_image_size
        self.x, self.y = img_pos
        self._background = backround
        self.frames = self._load_frames(folder)
        self.current_frame = 0
        self.last_update = pg.time.get_ticks()
        self.frame_rect = self.frames[self.current_frame].get_rect(topleft=(self.x, self.y))
        self.current_img: pg.Surface = self.frames[self.current_frame]
        
        
        
    def _load_frames(self, folder_name: str):
        return [
            pg.transform.scale(pg.image.load(img).convert_alpha(), (self.img_h, self.img_w))
            if not self._background else pg.transform.scale(pg.image.load(img).convert(), (self.img_h, self.img_w))
            for img in sorted(glob.glob(folder_name + '/*.png'))
        ]
        
    def _update_frame(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.speed:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = pg.time.get_ticks()
        
    def update_and_draw_frame(self):
        self._update_frame()
        self.current_img = self.frames[self.current_frame]
        self.screen.blit(self.current_img, (self.x, self.y))
        self.frame_rect = self.current_img.get_rect(topleft=(self.x, self.y))
        
    def update_and_draw_frame_at_pos(self, x: int, y: int):
        self._update_frame()
        self.screen.blit(self.frames[self.current_frame], (x, y))


 
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

class ButtonAction(ABC):
    def __init__(self, screen: pg.Surface, fram_obj: DrawImgsFrames):
        self.screen: pg.Surface = screen
        self.background: DrawImgsFrames = fram_obj
        
    def set_background(self):
        self.background.update_and_draw_frame()
   
    @abstractmethod
    def run(self, events: List[pg.Event]):
        pass
    
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
        
class StartGame(ButtonAction):
    
    def __init__(self, screen, background, maze: List[List[int]]):
        super().__init__(screen, background)
        self.expected_img_size: Tuple[int, int] = (40, 40)
        self.animation_speed = 100
        self.customized_maze_obj: OptimazedMaze = OptimazedMaze(maze)
        self.maze = self.customized_maze_obj.maze
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
        self.set_background()
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
        pg.draw.rect(self.screen, (10, 4, 87), pg.Rect(self.maze[0][0].x_pos, self.maze[0][0].y_pos, self.maze[0][0].cell_volume * 15, self.maze[0][0].cell_volume * 15))

    def draw_maze(self):
        walls_out_color = (0, 200, 255, 60)
        closed_cell_color = (20, 40, 160)
        for raw in self.maze:
            for cell in raw:
                if (cell.top_wall() and cell.buttom_wall() and cell.right_wall() and cell.left_wall()):
                    pg.draw.rect(self.screen, closed_cell_color, pg.Rect(cell.x_pos, cell.y_pos, cell.cell_volume, cell.cell_volume))
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

        
# class GameMenuScreen:
#     def __init__(self, screen, )

# class GameMenu:
#     def __init__(self, screen: pg.Surface, screen_size: Tuple[int],
#                  button_imgs: Dict[str, str], screen_center: Tuple[int, int],
#                  maze: MazeGenerator, debug_mod: bool = False) -> Self:
#         self._screen: pg.Surface = screen
#         self._screen_center: Tuple[int, int] = screen_center
#         self._screen_w, self.screen_h = screen_size
#         self._background: pg.Surface = self._load_background(button_imgs)
#         self._button_imgs: Dict[str, pg.Surface] = self._load_button_imgs(button_imgs)
#         self._button_imgs_w, self._button_imgs_h = self._get_button_imgs_size()
        
#         self._start_game_position: Tuple[int, int] = (screen_center[0] - self._button_imgs_w // 2, screen_center[1] - self.screen_h / 3)
#         self._heighscores_position: Tuple[int, int] = (screen_center[0] - self._button_imgs_w // 2, screen_center[1] - self.screen_h / 7)
#         self._instrcuction_position: Tuple[int, int] = (screen_center[0] - self._button_imgs_w // 2, screen_center[1] + self.screen_h / 30)
#         self._exit_position: Tuple[int, int] = (screen_center[0] - self._button_imgs_w // 2, screen_center[1] + self.screen_h / 5)
#         self.start_game: StartGame = StartGame(self._screen, (130, 17, 109), debug_mod, maze)
#         self.heighscores: Heighscores = Heighscores(self._screen, 'green', debug_mod)
#         self.instraction = Instractions(self._screen, 'gray', debug_mod)
#         self.exit = Exit(self._screen, 'red', debug_mod)
#         self.buttons: List[Button] = []
#         self.buttons_obj: List[ButtonAction] = []
        
#     def _load_button_imgs(self, button_imgs_path: Dict[str, str]) -> Dict[str, pg.Surface]:
#         '''this method return dictionary of button images that's you can blit them to the screen
#         :param button_imgs_path: dictionary with name of image and it's path
#         :type button_imgs_path: Tuple[int]
#         :return: dictionary of button images that's you can blit them to the screen
#         :rtype: Dict[str, pygame.Surface]
#         '''
#         imgs: Dict[str, pg.Surface] = {}
#         for name, path in button_imgs_path.items():
#             imgs[name] = pg.image.load(path)
#         return imgs
    
#     def button_clicked(self) -> Tuple[bool, Union[ButtonAction, None]]:
#         for b, b_obj in zip(self.buttons, self.buttons_obj):
#             if b.clicked:
#                 return True, b_obj
#         return False, None
#         # return True if (b.clicked for b in self.buttons) else False
        
#     def _load_background(self, menu_images: Dict[str, str]) -> pg.Surface:
#         '''this method load the background image of main menu
#         :param self: self instance of the Parser class
#         :return: image that's you can blit into pygame screen
#         :rtype: pygame.Surface
#         '''
#         background = pg.image.load(menu_images['background']).convert()
#         # let image comptiable with screen size
#         background = pg.transform.scale(background, self._screen.get_size())
#         return background
        
#     def _get_button_imgs_size(self) -> Tuple[int]:
#         '''return the size of the button images'''
#         return self._button_imgs['start'].get_size()
    
#     def _creat_buttons(self, x: int, y: int, width: int, height: int, img: pg.Surface) -> Button:
#         return Button(self._screen, x, y, width, height, image=img)
     
#     def hide_buttons(self) -> None:
#         for but in self.buttons:
#             but.hide()
        
    
#     def create_menu_screen(self) -> None:
#         self._screen.blit(self._background)
#         self.start_button: Button = self._creat_buttons(self._start_game_position[0],
#                                                       self._start_game_position[1],
#                                                       self._button_imgs_w,
#                                                       self._button_imgs_h,
#                                                       self._button_imgs['start'])
#         self.scores_button: Button = self._creat_buttons(self._heighscores_position[0],
#                                                       self._heighscores_position[1],
#                                                       self._button_imgs_w,
#                                                       self._button_imgs_h,
#                                                       self._button_imgs['scores'])
#         self.instraction_button: Button = self._creat_buttons(self._instrcuction_position[0],
#                                                       self._instrcuction_position[1],
#                                                       self._button_imgs_w,
#                                                       self._button_imgs_h,
#                                                       self._button_imgs['instructions'])
#         self.exit_button: Button = self._creat_buttons(self._exit_position[0],
#                                                       self._exit_position[1],
#                                                       self._button_imgs_w,
#                                                       self._button_imgs_h,
#                                                       self._button_imgs['exit'])

#         self.buttons.extend([self.start_button, self.scores_button,
#                         self.instraction_button, self.exit_button])
#         self.buttons_obj.extend([self.start_game, self.heighscores, self.instraction, self.exit])
    


 
    
       
class GameMenu:
    def __init__(self, screen: pg.Surface, tools: Dict[str, DrawImgsFrames], actions: Dict[str, ButtonAction]):
        self._screen = screen
        self._tools = tools
        self.actions = actions
        self.button_clicked: bool = False
        
        
    
    def _render_background(self):
        self._tools['menu_background'].update_and_draw_frame()
        
    def _handel_mouse_event(self, events: List[pg.Event], img_rect, action: ButtonAction):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if img_rect.collidepoint(event.pos):
                        self.action: ButtonAction = action
                        self.button_clicked = True
    
    def _create_buttons(self, events: List[pg.Event]):
        self._tools['start_game'].update_and_draw_frame()
        self._tools['instructions'].update_and_draw_frame()
        self._tools['high_scores'].update_and_draw_frame()
        self._tools['exit'].update_and_draw_frame()
        self._handel_mouse_event(events, self._tools['start_game'].frame_rect, self.actions['start_game'])
        self._handel_mouse_event(events, self._tools['instructions'].frame_rect, self.actions['instructions'])
        self._handel_mouse_event(events, self._tools['high_scores'].frame_rect, self.actions['high_scores'])
        self._handel_mouse_event(events, self._tools['exit'].frame_rect, self.actions['exit'])
    
    def create_menu_screen(self, events: List[pg.Event], clicked):
        if not clicked:
            self._render_background()
            self._create_buttons(events)
        else:
            self.action.run(events)




class PacmanGui:
    def __init__(self, maze: List[List[int]]):
        self.maze: List[List[int]] = maze
        pg.init()
        self.screen_w = 1200
        self.screen_h = 900
        self.font1 = pg.font.SysFont(None, 100)
        self.center: Tuple[int] = (self.screen_w / 2, self.screen_h / 2)
        self.scale = 12
        self.screen = self.creat_window()
    
    def creat_window(self) -> pg.Surface:
        
        screen: pg.Surface = pg.display.set_mode((self.screen_w, self.screen_h))
        pg.display.set_caption("Pac-Man yousenna && aessabri")
        icon_img = pg.image.load('assets/pacman_icon.png')
        pg.display.set_icon(icon_img)
        return screen
    
        
    def _get_imgs_tools(self, screen: pg.Surface) -> Dict[str, DrawImgsFrames]:
        return {
            'menu_background': DrawImgsFrames('assets/backgrounds/main_menu', screen, 300, (self.screen_w, self.screen_h)),
            'maze_background': DrawImgsFrames('assets/backgrounds/maze_background', screen, 200, (self.screen_w, self.screen_h)),
            'start_game': DrawImgsFrames('assets/buttons/start_game', screen,  150, (300, 200), False, (275, 350)),
            'instructions': DrawImgsFrames('assets/buttons/instructions', screen, 150, (300, 200), False, (625, 350)),
            'high_scores': DrawImgsFrames('assets/buttons/high_scores', screen, 150, (300, 200), False, (275, 525)),
            'exit': DrawImgsFrames('assets/buttons/exit', screen, 150, (300, 200), False, (625, 525)),
            # 'back': DrawImgsFrames('assets/buttons/back', screen, 150, (150, 70), False, (,)),
            # 'new_game': DrawImgsFrames('assets/buttons/new_game', screen, 150, (150, 70), False, (,)),
            # 'pause': DrawImgsFrames('assets/buttons/pause', screen, 150, (150, 70), False, (,)),
            # 'resume': DrawImgsFrames('assets/buttons/resume', screen, 150, (150, 70), False, (,)),
        }
        
    def _welcome_message(self, screen):
        screen.fill('yellow')
        text = self.font1.render("welcome back", True, "white", 2)
        screen.blit(text, (400, 400))
        pg.display.update()
        
    def _get_buttons_action(self, tools: Dict[str, DrawImgsFrames]):
        return {
            'start_game': StartGame(self.screen, tools['maze_background'], self.maze),
            'instructions': Instractions(self.screen, tools['maze_background']),
            'high_scores': Heighscores(self.screen, tools['maze_background']),
            'exit': Exit(self.screen, tools['maze_background']),
        }    

    def run(self):
        screen = self.screen
        self._welcome_message(screen)
        clock = pg.Clock()
        frames_tool = self._get_imgs_tools(screen)
        actions: Dict[str, ButtonAction] = self._get_buttons_action(frames_tool)
        menu = GameMenu(screen, frames_tool, actions)

        run_game = True
        button_clicked = False
        while run_game:
            events = pg.event.get()
            

            for event in events:
                if event.type == pg.QUIT:
                    run_game = False
            menu.create_menu_screen(events, button_clicked)
            if menu.button_clicked:
                button_clicked = True
            pg.display.update()
            clock.tick(10)
        pg.quit()
    