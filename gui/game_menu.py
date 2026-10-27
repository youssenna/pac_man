from typing import Dict, List, Self


import pygame as pg

from .animated_png_frames import DrawImgsFrames
from .bottons import ButtonAction


class GameMenu:
    def __init__(self, screen: pg.Surface, tools: Dict[str, DrawImgsFrames], actions: Dict[str, ButtonAction]):
        self._screen = screen
        self._tools = tools
        self.actions = actions
        self.button_clicked: bool = False
        
        
    
    def _render_background(self):
        self._tools['menu_background'].update_and_draw_frame()
        
    def _handel_mouse_event(self, events: List[pg.Event], img: DrawImgsFrames, action: ButtonAction):
        for event in events:
            mouse_pos = pg.mouse.get_pos()
            img.scale = 1.3 if img.frame_rect.collidepoint(mouse_pos) else 1.0
                
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if img.frame_rect.collidepoint(event.pos):
                        self.action: ButtonAction = action
                        self.button_clicked = True
    
    def _create_buttons(self, events: List[pg.Event]):
        self._tools['start_game'].update_and_draw_frame()
        self._tools['instructions'].update_and_draw_frame()
        self._tools['high_scores'].update_and_draw_frame()
        self._tools['exit'].update_and_draw_frame()
        self._handel_mouse_event(events, self._tools['start_game'], self.actions['start_game'])
        self._handel_mouse_event(events, self._tools['instructions'], self.actions['instructions'])
        self._handel_mouse_event(events, self._tools['high_scores'], self.actions['high_scores'])
        self._handel_mouse_event(events, self._tools['exit'], self.actions['exit'])
    
    def create_menu_screen(self, events: List[pg.Event], clicked):
        if not clicked:
            # self._render_background()
            # self._screen.blit(gif.blit_ready(), (0, 0))
            self._screen.blit(pg.transform.scale(self._tools['gif_background'].blit_ready(), (1280, 800)))
            # self._tools['gif_background'].render(self._screen, (0, 0))
            self._create_buttons(events)
        else:
            self.action.run(events)

