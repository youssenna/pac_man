from typing import Tuple
import glob

import pygame as pg
        
class DrawImgsFrames:
    def __init__(self, folder: str, screen: pg.Surface, animation_speed: int,
                 expected_image_size: Tuple[int, int], backround: bool = True, start_pos: Tuple[int, int] = (0, 0),
                 end_pos: Tuple[int, int] = (0, 0), mov_speed: int = 50, button: bool = True):
        self.screen = screen
        self.animation_speed = animation_speed
        self.mov_speed = mov_speed
        self.img_w, self.img_h = expected_image_size
        self.x, self.y = start_pos
        self.target_x, self.target_y = end_pos
        self._background = backround
        self.frames = self._load_frames(folder)
        self.current_frame = 0
        self.anim_last_update = pg.time.get_ticks()
        self.pos_last_update = pg.time.get_ticks()
        self.frame_rect = self.frames[self.current_frame].get_rect(topleft=(self.x, self.y))
        self.current_img: pg.Surface = self.frames[self.current_frame]
        self.img_original_size = self.current_img.get_size()
        self.button: bool = button
        self.scale: float = 1.0
        
        
        
    def _load_frames(self, folder_name: str):
        return [
            pg.transform.scale(pg.image.load(img).convert_alpha(), (self.img_h, self.img_w))
            if not self._background else pg.transform.scale(pg.image.load(img).convert(), (self.img_h, self.img_w))
            for img in sorted(glob.glob(folder_name + '/*.png'))
        ]
        
    def _update_frame(self):
        now = pg.time.get_ticks()
        if now - self.anim_last_update > self.animation_speed:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.anim_last_update = pg.time.get_ticks()
            # self.x +=10
            
    def _frame_target_distance(self) -> Tuple[int, int]:
        target_x = 10 if self.x < self.target_x else -10
        target_y = 5 if self.y < self.target_y else -5
        return target_x, target_y

    def _update_position(self):
        now = pg.time.get_ticks()
        if now - self.pos_last_update > self.mov_speed:
            x_dist, y_dist = self._frame_target_distance()
            if self.x != self.target_x:
                self.x += x_dist
            if self.y != self.target_y:
                self.y += y_dist
            self.pos_last_update = pg.time.get_ticks()
    
    def update_and_draw_frame(self):
        self._update_frame()
        if self.button:
            self._update_position()
        img_w = self.img_w * self.scale
        img_h = self.img_h * self.scale
        self.current_img = pg.transform.scale(self.frames[self.current_frame], (img_w, img_h))
        
        self.screen.blit(self.current_img, (self.x, self.y))
        self.frame_rect = self.current_img.get_rect(topleft=(self.x, self.y))
        
    def update_and_draw_frame_at_pos(self, x: int, y: int):
        self._update_frame()
        self.screen.blit(self.frames[self.current_frame], (x, y))
