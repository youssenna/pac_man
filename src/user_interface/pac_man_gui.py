import pygame as pg
import pygame_widgets
import glob
from pygame_widgets.button import Button
# from pygame_widgets.animations import Resize
# from moviepy.editor import VideoFileClip
from typing import Any, List, Dict, Optional, Tuple, Self, Callable, Union
from mazegenerator import MazeGenerator


from abc import ABC, abstractmethod

 
    
class Cell:
    def __init__(self, x: int, y: int, wall_stat: int) -> Self:
        self.x = x
        self.y = y
        self.wall_stat = wall_stat
        self.cell_volume = 65
        self.x_desplacement = 420
        self.y_desplacement = 20
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
                 image_size: Tuple[int, int], maze: List[List[Cell]],
                 maze_size: Tuple[int, int] = (15, 15), padding: int = 10):
        self.screen: pg.Surface = screen
        self.cell: Cell = cell
        self.maze = maze
        self.x, self.y = self.cell.x, self.cell.y
        self.x_pos = self.cell.x_pos
        self.y_pos = self.cell.y_pos
        self.column, self.raw = maze_size
        self.padding: int = padding
        self.animation: Dict[str, List[pg.Surface]] = {
            'up': self._get_imgs_frames(imgs_folder + '/up', image_size),
            'right': self._get_imgs_frames(imgs_folder + '/right', image_size),
            'down': self._get_imgs_frames(imgs_folder + '/down', image_size),
            'left': self._get_imgs_frames(imgs_folder + '/left', image_size)
        }
        self.direction: str = self._get_direction(cell)
        self.current_frame: int = 0
        self.speed: int = 75
        self.last_update = pg.time.get_ticks()
    
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
    
    def _get_imgs_frames(self, imgs_folder: str, image_size) -> List[pg.Surface]:
        frames: List[pg.Surface] = []
        
        for img in glob.glob(imgs_folder + '/*.png'):
            img = pg.transform.scale(pg.image.load(img), image_size)
            frames.append(img)
        return frames
    
    def update_frame(self):
        now = pg.time.get_ticks()
        
        if now - self.last_update >= self.speed:
            self.current_frame = (self.current_frame + 1) % len(self.animation[self.direction])
            self.last_update = pg.time.get_ticks()
    
    
    def draw_frame(self):
        self.update_frame()
        self.screen.blit(self.animation[self.direction][self.current_frame], (self.x_pos + self.padding, self.y_pos + self.padding))
    
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
    def __init__(self, screen, cell, imgs_folder, image_size, maze, maze_size = (15, 15), padding = 10):
        super().__init__(screen, cell, imgs_folder, image_size, maze, maze_size, padding)
        self.draw_frame()
        
    def move(self, events: List[pg.Event]):
        for event in events:
            if event.type == pg.KEYDOWN:
                if event.key in (pg.K_DOWN, pg.K_s) and not self.cell.buttom_wall():
                    self.direction = 'down'
                    self.move_down()
                elif event.key in (pg.K_UP, pg.K_w) and not self.cell.top_wall():
                    self.direction = 'up'
                    self.move_up()
                elif event.key in (pg.K_RIGHT, pg.K_d) and not self.cell.right_wall():
                    self.direction = 'right'
                    self.move_right()
                elif event.key in (pg.K_LEFT, pg.K_a) and not self.cell.left_wall():
                    self.direction = 'left'
                    self.move_left()
        self.draw_frame()

class ButtonAction(ABC):
    def __init__(self, screen: pg.Surface, color: str, debug_mod: bool):
        self.screen: pg.Surface = screen
        self.color: str = color
        self.set_background_color()
        self.debug = debug_mod
        
    def set_background_color(self):
        self.screen.fill(self.color)
   
    @abstractmethod
    def run(self, events: List[pg.Event]):
        pass
    
class OptimazedMaze:
    def __init__(self, maze: MazeGenerator, debug_mod: bool = False):
        self.maze: List[List[Cell]] = self._get_customized_maze(maze, debug_mod)
        
    def _get_customized_maze(self, maze: List[List[int]], debug: bool = False):
        customed_maze = []
        
        if debug:
            print('#'*20, 'debug customized_maze', '#'*20)
        for y_index, col in enumerate(maze):
            maze_raw = []
            for x_index, raw in enumerate(col):
                maze_raw.append(Cell(x_index, y_index, raw))
            customed_maze.append(maze_raw)
            if debug:
                print(maze_raw)
        return customed_maze
        

class StartGame(ButtonAction):
    
    def __init__(self, screen, color, debug_mod, maze: MazeGenerator):
        super().__init__(screen, color, debug_mod)
        self.customized_maze_obj: OptimazedMaze = OptimazedMaze(maze, debug_mod)
        self.maze = self.customized_maze_obj.maze
        self.player = Player(self.screen, self.maze[6][7], 'assets/pacman_sprites/pacman', (45, 45), self.maze)
        self.green_ghost = Ghost(self.screen, self.maze[0][1], 'assets/pacman_sprites/ghosts/green', (45, 45), self.maze)
        self.red_ghost = Ghost(self.screen, self.maze[14][13], 'assets/pacman_sprites/ghosts/red', (45, 45), self.maze)
        self.orange_ghost = Ghost(self.screen, self.maze[1][14], 'assets/pacman_sprites/ghosts/orange', (45, 45), self.maze)
        self.pink_ghost = Ghost(self.screen, self.maze[14][1], 'assets/pacman_sprites/ghosts/pink', (45, 45), self.maze)

    def start(self, events: List[pg.Event]):
        # pg.draw.line(self.screen, 'blue', (100, 100), (100, 250), 5)
        # pg.draw.line(self.screen, 'blue', (100, 100), (250, 100), 5)
        # pg.draw.line(self.screen, 'blue', (100, 250), (250, 250), 5)
        # pg.draw.line(self.screen, 'blue', (250, 100), (250, 250), 5)
        # pg.draw.line(self.screen, 'orange', (105, 105), (105, 245), 5)
        # pg.draw.line(self.screen, 'orange', (105, 105), (245, 105), 5)
        # pg.draw.line(self.screen, 'orange', (105, 245), (245, 245), 5)
        # pg.draw.line(self.screen, 'orange', (245, 105), (245, 245), 5)
        # pg.draw.line(self.screen, 'blue', (110, 110), (110, 240), 5)
        # pg.draw.line(self.screen, 'blue', (110, 110), (240, 110), 5)
        # pg.draw.line(self.screen, 'blue', (110, 240), (240, 240), 5)
        # pg.draw.line(self.screen, 'blue', (240, 110), (240, 240), 5)
        # backround = pg.image.load("assets/background.png").convert()
        # backround = pg.transform.scale(backround, self.screen.get_size())
        # self.screen.blit(backround)
        self.draw_maze()
        self.player.move(events)
        self.green_ghost.move()
        self.red_ghost.move()
        self.pink_ghost.move()
        self.orange_ghost.move()
         
    def draw_maze(self):
        walls_out_color = (228, 87, 89)
        walls_in_color = (249, 248, 113)
        for raw in self.maze:
            for cell in raw:
                if cell.top_wall():
                    s, e = cell.top_wall_pos
                    s_x, s_y  = s
                    e_x, e_y = e
                    pg.draw.line(self.screen, walls_out_color, (s_x, s_y), (e_x, e_y), 5)
                    # pg.draw.line(self.screen, walls_in_color, (s_x, s_y), (e_x, e_y), 2)
                    # pg.draw.line(self.screen, walls_in_color, (s_x, s_y), (e_x, e_y), 2)
                if cell.buttom_wall():
                    
                    s, e = cell.buttom_wall_pos
                    s_x, s_y  = s
                    e_x, e_y = e
                    pg.draw.line(self.screen, walls_out_color, (s_x, s_y), (e_x, e_y), 5)
                    # pg.draw.line(self.screen, walls_in_color, (s_x, s_y), (e_x, e_y), 2)
                    # pg.draw.line(self.screen, walls_in_color, (s_x, s_y), (e_x, e_y), 2)
                if cell.right_wall():
                    s, e = cell.right_wall_pos
                    s_x, s_y  = s
                    e_x, e_y = e
                    pg.draw.line(self.screen, walls_out_color, (s_x, s_y), (e_x, e_y), 5)
                    # pg.draw.line(self.screen, walls_in_color, (s_x, s_y), (e_x, e_y), 2)
                    # pg.draw.line(self.screen, walls_in_color, (s_x, s_y), (e_x, e_y), 2)
                if cell.left_wall():
                    s, e = cell.left_wall_pos
                    s_x, s_y  = s
                    e_x, e_y = e
                    pg.draw.line(self.screen, walls_out_color, (s_x, s_y), (e_x, e_y), 5)
                    # pg.draw.line(self.screen, walls_in_color, (s_x, s_y), (e_x, e_y), 2)
                    # pg.draw.line(self.screen, walls_in_color, (s_x, s_y), (e_x, e_y), 2)
        
        if self.debug:
            print('#'*20, 'original maze', '#'*20,)
            print(self.maze)
        # exit()
        
        
    
    def run(self, events: List[pg.Event]):
        self.start(events)
    
class Heighscores(ButtonAction):
    def show_heighscores(self):
        print('show heighscores.')
        
    def run(self):
        self.show_heighscores()
    
class Instractions(ButtonAction):
    def show_instractions(self):
        print('show instractions.')

    def run(self):
        self.show_instractions()
    
class Exit(ButtonAction):
    def exit_game(self):
        print('exit game.')
    
    def run(self):
        self.exit_game()

class GameMenu:
    def __init__(self, screen: pg.Surface, screen_size: Tuple[int],
                 button_imgs: Dict[str, str], screen_center: Tuple[int, int],
                 maze: MazeGenerator, debug_mod: bool = False) -> Self:
        self._screen: pg.Surface = screen
        self._screen_center: Tuple[int, int] = screen_center
        self._screen_w, self.screen_h = screen_size
        self._background: pg.Surface = self._load_background(button_imgs)
        self._button_imgs: Dict[str, pg.Surface] = self._load_button_imgs(button_imgs)
        self._button_imgs_w, self._button_imgs_h = self._get_button_imgs_size()
        
        self._start_game_position: Tuple[int, int] = (screen_center[0] - self._button_imgs_w // 2, screen_center[1] - self.screen_h / 3)
        self._heighscores_position: Tuple[int, int] = (screen_center[0] - self._button_imgs_w // 2, screen_center[1] - self.screen_h / 7)
        self._instrcuction_position: Tuple[int, int] = (screen_center[0] - self._button_imgs_w // 2, screen_center[1] + self.screen_h / 30)
        self._exit_position: Tuple[int, int] = (screen_center[0] - self._button_imgs_w // 2, screen_center[1] + self.screen_h / 5)
        self.start_game: StartGame = StartGame(self._screen, (130, 17, 109), debug_mod, maze)
        self.heighscores: Heighscores = Heighscores(self._screen, 'green', debug_mod)
        self.instraction = Instractions(self._screen, 'gray', debug_mod)
        self.exit = Exit(self._screen, 'red', debug_mod)
        self.buttons: List[Button] = []
        self.buttons_obj: List[ButtonAction] = []
        
    def _load_button_imgs(self, button_imgs_path: Dict[str, str]) -> Dict[str, pg.Surface]:
        '''this method return dictionary of button images that's you can blit them to the screen
        :param button_imgs_path: dictionary with name of image and it's path
        :type button_imgs_path: Tuple[int]
        :return: dictionary of button images that's you can blit them to the screen
        :rtype: Dict[str, pygame.Surface]
        '''
        imgs: Dict[str, pg.Surface] = {}
        for name, path in button_imgs_path.items():
            imgs[name] = pg.image.load(path)
        return imgs
    
    def button_clicked(self) -> Tuple[bool, Union[ButtonAction, None]]:
        for b, b_obj in zip(self.buttons, self.buttons_obj):
            if b.clicked:
                return True, b_obj
        return False, None
        # return True if (b.clicked for b in self.buttons) else False
        
    def _load_background(self, menu_images: Dict[str, str]) -> pg.Surface:
        '''this method load the background image of main menu
        :param self: self instance of the Parser class
        :return: image that's you can blit into pygame screen
        :rtype: pygame.Surface
        '''
        background = pg.image.load(menu_images['background']).convert()
        # let image comptiable with screen size
        background = pg.transform.scale(background, self._screen.get_size())
        return background
        
    def _get_button_imgs_size(self) -> Tuple[int]:
        '''return the size of the button images'''
        return self._button_imgs['start'].get_size()
    
    def _creat_buttons(self, x: int, y: int, width: int, height: int, img: pg.Surface) -> Button:
        return Button(self._screen, x, y, width, height, image=img)
     
    def hide_buttons(self) -> None:
        for but in self.buttons:
            but.hide()
        
    
    def create_menu_screen(self) -> None:
        self._screen.blit(self._background)
        self.start_button: Button = self._creat_buttons(self._start_game_position[0],
                                                      self._start_game_position[1],
                                                      self._button_imgs_w,
                                                      self._button_imgs_h,
                                                      self._button_imgs['start'])
        self.scores_button: Button = self._creat_buttons(self._heighscores_position[0],
                                                      self._heighscores_position[1],
                                                      self._button_imgs_w,
                                                      self._button_imgs_h,
                                                      self._button_imgs['scores'])
        self.instraction_button: Button = self._creat_buttons(self._instrcuction_position[0],
                                                      self._instrcuction_position[1],
                                                      self._button_imgs_w,
                                                      self._button_imgs_h,
                                                      self._button_imgs['instructions'])
        self.exit_button: Button = self._creat_buttons(self._exit_position[0],
                                                      self._exit_position[1],
                                                      self._button_imgs_w,
                                                      self._button_imgs_h,
                                                      self._button_imgs['exit'])

        self.buttons.extend([self.start_button, self.scores_button,
                        self.instraction_button, self.exit_button])
        self.buttons_obj.extend([self.start_game, self.heighscores, self.instraction, self.exit])
    


        
        
        
    
        



class PacmanGui:
    def __init__(self, maze: List[List[int]]):
        self.maze: List[List[int]] = maze
        pg.init()
        info: Any = pg.display.Info()
        self.screen_w = info.current_w
        self.screen_h = info.current_h
        self.font1 = pg.font.SysFont(None, 15)
        self.center: Tuple[int] = (self.screen_w / 2, self.screen_h / 2)
        self.scale = 12
        self.screen = self.creat_window()
    
    def creat_window(self) -> pg.Surface:
        
        screen: pg.Surface = pg.display.set_mode((self.screen_w, self.screen_h))
        pg.display.set_caption("Pac-Man yousenna && aessabri")
        icon_img = pg.image.load('assets/pacman_icon.png')
        pg.display.set_icon(icon_img)
        return screen
    

 
    def _get_menu_imgs(self) -> Dict[str, str]:
        return {
            'start': 'assets/buttons/start_game.png',
            'scores': 'assets/buttons/high_scores.png',
            'instructions': 'assets/buttons/instructions.png',
            'exit': 'assets/buttons/exit.png',
            'background': 'assets/backgrounds/background1.png'
        }
        
    def run(self):
        screen = self.screen
        menu_button: Dict[str, str] = self._get_menu_imgs()
        game_menu = GameMenu(screen, screen.get_size(), menu_button, self.center, self.maze)
        game_menu.create_menu_screen()

        run_game = True
        while run_game:
            events = pg.event.get()
            

            pygame_widgets.update(events)
            clicked, obj_action = game_menu.button_clicked()
            if clicked:
                game_menu.hide_buttons()
                obj_action.set_background_color()
                obj_action.run(events)

            for event in events:
                if event.type == pg.QUIT:
                    run_game = False
            pg.display.update()
        pg.quit()
    