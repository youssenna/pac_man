Pac-Man sprite pack (glossy 3D style, derived from the supplied reference image)
Every PNG is 65x65 RGBA with a transparent background (pellets are drawn centred in a 65x65 tile).
Pac-Man: 4 frames per direction; play 1,2,3,4 and loop (closed -> half -> open -> half).
Ghosts + frightened: 3 frames per direction; play 1,2,3,2 and loop.
frightened_ghost_warning/: white/red flash variant; alternate with frightened_ghost/ when the power pellet is nearly over.
pellets/power_pellet_frame_01/02.png: optional 2-frame pulse (same 65x65 canvas).

pellets/power_pellet.png = red 8-point star (default super pellet). power_pellet_round.png = the original round one.
pellets/power_star/<red|pink|yellow>/frame_01.png, frame_02.png = 2-frame pulse for each colour. power_pellet_star_<colour>.png = single frame.
food/*.png = bonus fruit (cherry, strawberry, orange, lemon, apple, banana, grapes, watermelon), 65x65.
