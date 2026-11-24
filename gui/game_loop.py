from typing import List, Tuple, Self, Dict

import pygame as pg
import gif_pygame as gif_pg

from .game_info import GameInfo
from .animated_png_frames import DrawImgsFrames
from .bottons import ButtonAction, StartGame, Heighscores, Instractions, Exit
from .game_menu import GameMenu
from backend import GameEngine


class PacmanGui:
    def __init__(self, engine: GameEngine, screen_size: Tuple[int, int]) -> None:
        self._engine: GameEngine  = engine
        self._screen_w, self._screen_h = screen_size
        pg.init()
        self._font1 = pg.font.SysFont(None, 100)
        self._screen = self._creat_window()
        
    def _creat_window(self) -> pg.Surface:
        screen: pg.Surface = pg.display.set_mode((self._screen_w, self._screen_h))
        pg.display.set_caption("Pac-Man yousenna && aessabri")
        icon_img = pg.image.load('assets/pacman_icon.png')
        pg.display.set_icon(icon_img)
        return screen
    
    def _get_imgs_tools(self, screen: pg.Surface) -> Dict[str, DrawImgsFrames]:
        return {
            # 'menu_background': DrawImgsFrames('assets/backgrounds/tst', screen, 10, (self.game_info._screen_w, self.game_info._screen_h)),
            'maze_background': DrawImgsFrames('assets/backgrounds/maze_background', screen, 200, (self._screen_w, self._screen_h)),
            'start_game': DrawImgsFrames('assets/buttons/start_game', screen,  150, (300, 200), False, (0, 0), (300, 140), 10),
            'instructions': DrawImgsFrames('assets/buttons/instructions', screen, 150, (300, 200), False, (self._screen_w - 300, 0), (650, 140), 10),
            'high_scores': DrawImgsFrames('assets/buttons/high_scores', screen, 150, (300, 200), False, (0, self._screen_h - 200),(300, 370), 10),
            'exit': DrawImgsFrames('assets/buttons/exit', screen, 150, (300, 200), False, (self._screen_w - 300, self._screen_h - 200), (650, 370), 10),
            'gif_background': gif_pg.load("assets/background2.gif")

            # 'back': DrawImgsFrames('assets/buttons/back', screen, 150, (150, 70), False, (,)),
            # 'new_game': DrawImgsFrames('assets/buttons/new_game', screen, 150, (150, 70), False, (,)),
            # 'pause': DrawImgsFrames('assets/buttons/pause', screen, 150, (150, 70), False, (,)),
            # 'resume': DrawImgsFrames('assets/buttons/resume', screen, 150, (150, 70), False, (,)),
        }

    def _get_buttons_action(self, tools: Dict[str, DrawImgsFrames]):
        return {
            'start_game': StartGame(self._screen, tools['maze_background'], self._engine),
            'instructions': Instractions(self._screen, tools['maze_background']),
            'high_scores': Heighscores(self._screen, tools['maze_background']),
            'exit': Exit(self._screen, tools['maze_background']),
        }  
    def _welcome_message(self, screen):
        screen.fill('yellow')
        text = self._font1.render("welcome back", True, "white", 2)
        screen.blit(text, (400, 300))
        pg.display.update()

    def run(self):
        screen = self._screen
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
    
