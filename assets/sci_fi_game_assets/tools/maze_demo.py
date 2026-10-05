"""Minimal demo: draws the animated maze (layout extracted from your reference
screenshot) plus the animated menu buttons.  Run from the pack root:
    python tools/maze_demo.py            # maze  (ESC / close window to quit)
    python tools/maze_demo.py menu       # menu buttons (hover with mouse)
Use SIZE = "maze" (128px tiles) or "maze_small_48px" (48px tiles)."""
import os, sys, pygame
sys.path.insert(0, os.path.dirname(__file__))
from asset_loader import *

ROOT = os.path.join(os.path.dirname(__file__), "..")
SIZE = "maze_small_48px"
TILE = 48 if "48" in SIZE else 128
FPS_ANIM = 12

def run_maze():
    pygame.init()
    cols, rows, H, V = load_layout(os.path.join(ROOT, "layouts", "maze_layout.json"))
    side = (cols + 3) * TILE                    # maze tiles + 1 hull-panel ring each side
    screen = pygame.display.set_mode((side, side))   # set the video mode BEFORE convert_alpha()
    walls = load_tree(os.path.join(ROOT, SIZE, "walls"))
    cells = load_frames(os.path.join(ROOT, SIZE, "closed_cells"))
    n = len(cells)                              # every animation has the same frame count
    clock, t = pygame.time.Clock(), 0.0
    ox = oy = TILE * 3 // 2                     # pixel centre of vertex (0, 0)
    inset = (TILE - cells[0].get_width()) // 2  # closed cell = interior between two pipes
    while True:
        t += clock.tick(60) / 1000
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE): return
        f = int(t * FPS_ANIM) % n
        screen.fill((8, 6, 24))
        # 1) closed cells first (they sit *under* the pipes)
        for j in range(rows):
            for i in range(cols):
                if H[j][i] and H[j+1][i] and V[j][i] and V[j][i+1]:
                    screen.blit(cells[f], (ox + i * TILE + inset, oy + j * TILE + inset))
        # 2) one pipe tile per maze vertex, chosen by its neighbours
        for j in range(rows + 1):
            for i in range(cols + 1):
                m = vertex_mask(H, V, cols, rows, i, j)
                if m: screen.blit(walls[AUTOTILE[m]][f], (ox + i * TILE - TILE // 2, oy + j * TILE - TILE // 2))
        # 3) outer hull panels (hazard stripe faces the maze)
        x0, x1 = 0, (cols + 2) * TILE
        y0, y1 = 0, (cols + 2) * TILE
        for k in range(cols + 3):
            screen.blit(walls["wall_bottom"][f], (k * TILE, y0))
            screen.blit(walls["wall_top"][f],    (k * TILE, y1))
        for k in range(1, rows + 2):
            screen.blit(walls["wall_right"][f], (x0, k * TILE))
            screen.blit(walls["wall_left"][f],  (x1, k * TILE))
        pygame.display.flip()

def run_menu():
    pygame.init()
    screen = pygame.display.set_mode((1500, 1000))
    btns = load_tree(os.path.join(ROOT, "menu_buttons"))
    names = list(btns)
    rects = {}
    for n, k in enumerate(names):
        w, h = btns[k][0].get_size()
        rects[k] = pygame.Rect(30 + (n % 3) * 490, 30 + (n // 3) * 330, w, h)
    clock, t = pygame.time.Clock(), 0.0
    while True:
        dt = clock.tick(60) / 1000; t += dt
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE): return
        screen.fill((10, 8, 30))
        mouse = pygame.mouse.get_pos()
        for k in names:
            speed = 24 if rects[k].collidepoint(mouse) else 12      # faster pulse on hover
            fr = btns[k]; screen.blit(fr[int(t * speed) % len(fr)], rects[k])
        pygame.display.flip()

if __name__ == "__main__":
    run_menu() if "menu" in sys.argv else run_maze()
