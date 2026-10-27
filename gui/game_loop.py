from typing import List, Tuple, Self, Dict

import pygame as pg
import gif_pygame as gif_pg

from .game_info import GameInfo
from .animated_png_frames import DrawImgsFrames
from .bottons import ButtonAction, StartGame, Heighscores, Instractions, Exit
from .game_menu import GameMenu


class PacmanGui:
    def __init__(self, maze: List[List[int]], game_info: GameInfo) -> Self:
        self.maze: List[List[int]] = maze
        self.game_info: GameInfo = game_info
        pg.init()
        self.font1 = pg.font.SysFont(None, 100)
        self.screen = self.creat_window()
        
    def creat_window(self) -> pg.Surface:
        screen: pg.Surface = pg.display.set_mode((self.game_info.screen_w, self.game_info.screen_h))
        pg.display.set_caption("Pac-Man yousenna && aessabri")
        icon_img = pg.image.load('assets/pacman_icon.png')
        pg.display.set_icon(icon_img)
        return screen
    
    def _get_imgs_tools(self, screen: pg.Surface) -> Dict[str, DrawImgsFrames]:
        return {
            # 'menu_background': DrawImgsFrames('assets/backgrounds/tst', screen, 10, (self.game_info.screen_w, self.game_info.screen_h)),
            'maze_background': DrawImgsFrames('assets/backgrounds/maze_background', screen, 200, (self.game_info.screen_w, self.game_info.screen_h)),
            'start_game': DrawImgsFrames('assets/buttons/start_game', screen,  150, (300, 200), False, (0, 0), (300, 140), 10),
            'instructions': DrawImgsFrames('assets/buttons/instructions', screen, 150, (300, 200), False, (self.game_info.screen_w - 300, 0), (650, 140), 10),
            'high_scores': DrawImgsFrames('assets/buttons/high_scores', screen, 150, (300, 200), False, (0, self.game_info.screen_h - 200),(300, 370), 10),
            'exit': DrawImgsFrames('assets/buttons/exit', screen, 150, (300, 200), False, (self.game_info.screen_w - 300, self.game_info.screen_h - 200), (650, 370), 10),
            'gif_background': gif_pg.load("assets/background2.gif")

            # 'back': DrawImgsFrames('assets/buttons/back', screen, 150, (150, 70), False, (,)),
            # 'new_game': DrawImgsFrames('assets/buttons/new_game', screen, 150, (150, 70), False, (,)),
            # 'pause': DrawImgsFrames('assets/buttons/pause', screen, 150, (150, 70), False, (,)),
            # 'resume': DrawImgsFrames('assets/buttons/resume', screen, 150, (150, 70), False, (,)),
        }

    def _get_buttons_action(self, tools: Dict[str, DrawImgsFrames]):
        return {
            'start_game': StartGame(self.screen, tools['maze_background'], self.maze),
            'instructions': Instractions(self.screen, tools['maze_background']),
            'high_scores': Heighscores(self.screen, tools['maze_background']),
            'exit': Exit(self.screen, tools['maze_background']),
        }  
    def _welcome_message(self, screen):
        screen.fill('yellow')
        text = self.font1.render("welcome back", True, "white", 2)
        screen.blit(text, (400, 300))
        pg.display.update()

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
    
