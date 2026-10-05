SCI-FI PAC-MAN ASSET PACK  (animated, Pygame-ready)
===================================================
All animations are 16 frames, frame_000.png ... frame_015.png, played in order and looped.
Recommended speed: 12 FPS (8-15 FPS all look fine). Every frame in a folder has identical
size and alignment, with a transparent background. Loops are seamless (frame_015 -> frame_000).

FOLDERS
-------
maze/                     128 px tiles (master quality)
maze_small_48px/          same structure pre-scaled to 48 px tiles (close to your 45 px grid)
menu_buttons/             one folder per button from your button sheet
layouts/maze_layout.json  wall graph extracted from your reference screenshot (Image 5)
tools/                    asset_loader.py, maze_demo.py (run it!), resize_pack.py
preview_maze.gif          animated preview of the maze assembled from these tiles

MAZE: WALLS  (maze/walls/)
--------------------------
Pipes are the maze walls. Each pipe tile is centred on a maze VERTEX (a grid corner) and
connects to the neighbouring vertices, exactly like the thin lines in your screenshot.
Tile = 128 px, pipe thickness = 34 px. The neon pulse is phase-aligned across tile borders,
so neighbouring tiles join into one continuous tube.

  wall_horizontal / wall_vertical          straight pipe  (E-W, N-S)
  corners/wall_top_left_corner             pipe goes East + South   (glyph  ┌)
  corners/wall_top_right_corner            pipe goes West + South   (glyph  ┐)
  corners/wall_bottom_left_corner          pipe goes East + North   (glyph  └)
  corners/wall_bottom_right_corner         pipe goes West + North   (glyph  ┘)
  junctions/wall_t_up    ┴  (W,E,N)    junctions/wall_t_down  ┬  (W,E,S)
  junctions/wall_t_left  ┤  (N,S,W)    junctions/wall_t_right ├  (N,S,E)
  junctions/wall_cross   ┼  (all four)
  ends/wall_end_up|right|down|left         dead end with round cap; the pipe leaves the
                                           tile in the named direction
  wall_single_post                         isolated post (no neighbours)
  wall_top / wall_right / wall_bottom / wall_left
                                           solid hull panels. The name says which edge has
                                           the hazard stripe. For an outer frame around the
                                           maze use: top row -> wall_bottom, bottom row ->
                                           wall_top, left column -> wall_right,
                                           right column -> wall_left (stripe faces inward).

Autotiling: for each vertex build a mask  N=1, E=2, S=4, W=8  from the edges that touch it,
then look it up in AUTOTILE (tools/asset_loader.py). maze_demo.py shows the full loop.

MAZE: CLOSED CELLS  (maze/closed_cells/)
----------------------------------------
Sealed energy chambers (violet core, expanding rings, runner light around the hazard frame,
one bigger glow pulse per loop) so they never look like normal walls. Frame size is
94 x 94 px (= 128 - pipe thickness): it is the interior of a cell between its four pipes.
Draw it FIRST (under the pipes) at  vertex_center(i,j) + 17 px  in both axes.
In the layout file a cell is closed when all four of its sides have a wall (that is the
block of enclosed cells in the middle of your reference maze).

LAYOUT FILE  (layouts/maze_layout.json)
---------------------------------------
15 x 15 cells -> 16 x 16 vertices.
  H[j][i] = 1 : wall between vertex (i,j) and (i+1,j)      (j = 0..15, i = 0..14)
  V[j][i] = 1 : wall between vertex (i,j) and (i,j+1)      (j = 0..14, i = 0..15)
Pixel centre of vertex (i,j) = (origin_x + i*TILE, origin_y + j*TILE); Pac-Man/ghosts walk
through cell centres  (origin + (i+0.5)*TILE, origin + (j+0.5)*TILE).
NOTE: the layout was read from the screenshot automatically - eyeball it against your
own maze data if a wall looks off.

MENU BUTTONS  (menu_buttons/<name>/)
------------------------------------
start_game  high_scores  instructions  exit  pause  resume  back  new_game
Original artwork (mascots included) cut out from your sheet and animated: pulsing neon
text/icons, light running around the frame, glass reflection sweeping over the screen,
chasing amber LEDs, crackling energy. Native size ~480 x 300-350 px (scale in Pygame with
pygame.transform.smoothscale). Tip: play at 24 FPS while hovered for an "active" feel
(see run_menu in tools/maze_demo.py).

PYGAME QUICK START
------------------
    from tools.asset_loader import load_frames, Animation
    pygame.display.set_mode(...)                     # before convert_alpha()
    start = Animation(load_frames("menu_buttons/start_game"), fps=12)
    ...  start.update(dt);  screen.blit(start.image, pos)

    python tools/maze_demo.py          # animated maze
    python tools/maze_demo.py menu     # animated menu (hover for faster pulse)
Need another tile size? python tools/resize_pack.py maze maze_64 0.5

PREVIEW GIFs
------------
Every animation folder contains preview.gif (transparent background) showing how its frames
look when played at 12 FPS. main_menu_preview.gif / .png (pack root) show the main menu:
your menu background with the four animated buttons placed over the doors.
All PNG frames have real transparent backgrounds (alpha channel).
