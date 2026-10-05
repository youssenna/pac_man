"""Helpers to load the animated sci-fi asset pack in Pygame."""
import os, json, pygame

def load_frames(folder, convert=True):
    """Return the list of frame surfaces of one animation folder, in order."""
    names = sorted(f for f in os.listdir(folder) if f.endswith(".png"))
    frames = [pygame.image.load(os.path.join(folder, n)) for n in names]
    return [f.convert_alpha() for f in frames] if convert else frames

def load_tree(root):
    """Load every animation below `root` -> {relative_folder_name: [frames]}.
    e.g. load_tree('maze/walls')['wall_horizontal'], ['corners/wall_top_left_corner'] ..."""
    out = {}
    for dp, _, files in os.walk(root):
        if any(f.endswith(".png") for f in files):
            out[os.path.relpath(dp, root).replace(os.sep, "/")] = load_frames(dp)
    return out

class Animation:
    """Tiny frame player. Call update(dt_seconds) every frame, then .image."""
    def __init__(self, frames, fps=12):
        self.frames, self.fps, self.t = frames, fps, 0.0
    def update(self, dt): self.t += dt
    @property
    def image(self): return self.frames[int(self.t * self.fps) % len(self.frames)]

# 4-bit neighbour mask (N=1, E=2, S=4, W=8) -> wall folder under maze/walls/
AUTOTILE = {
    0: "wall_single_post",
    1: "ends/wall_end_up",    2: "ends/wall_end_right",
    4: "ends/wall_end_down",  8: "ends/wall_end_left",
    5: "wall_vertical",       10: "wall_horizontal",
    3: "corners/wall_bottom_left_corner",  6: "corners/wall_top_left_corner",
    12: "corners/wall_top_right_corner",   9: "corners/wall_bottom_right_corner",
    11: "junctions/wall_t_up",   14: "junctions/wall_t_down",
    7: "junctions/wall_t_right", 13: "junctions/wall_t_left",
    15: "junctions/wall_cross",
}

def load_layout(path):
    d = json.load(open(path))
    return d["cols"], d["rows"], d["H"], d["V"]

def vertex_mask(H, V, cols, rows, i, j):
    m = 0
    if j > 0    and V[j-1][i]: m |= 1
    if i < cols and H[j][i]:   m |= 2
    if j < rows and V[j][i]:   m |= 4
    if i > 0    and H[j][i-1]: m |= 8
    return m
