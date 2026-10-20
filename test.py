"""Temporary tester for the Pac-Man logic (engine, level, ghosts, highscores).

DELETE BEFORE SUBMISSION.

Usage:
    python3 test.py config.json            # headless checks, then the window
    python3 test.py config.json --no-gui    # headless checks only

Assumed module names: engine, level, parsing, pacgums, ghost_ai, pathfinding,
characters, highscores. Rename the imports below if yours differ.
"""
import json
import os
import sys
import tempfile
from collections import deque

from characters import Blinky
from engine import GameEngine
from ghost_ai import decide_ghost_move
from highscores import (
    add_highscore,
    is_highscore,
    is_valid_name,
    load_highscores,
    save_highscores,
)
from pacgums import scare_ghosts
from parsing import load_config
from pathfinding import find_path

VEC = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
DIRS = ("N", "E", "S", "W")

RESULTS: list[tuple[bool, str]] = []


def check(condition: object, label: str) -> None:
    ok = bool(condition)
    RESULTS.append((ok, label))
    print(("  PASS  " if ok else "  FAIL  ") + label)


def time_left(engine: GameEngine) -> float:
    t = engine.level.timer
    total = getattr(t, "level_max_time", getattr(t, "duration", 0.0))
    return float(total - t.passed)


def timer_total(engine: GameEngine) -> float:
    t = engine.level.timer
    return float(getattr(t, "level_max_time", getattr(t, "duration", 0.0)))


# --------------------------------------------------------------------------
# Headless checks
# --------------------------------------------------------------------------

def test_parsing(config):
    print("\n[parsing]")
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "c.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(
                '{\n'
                '  # a comment\n'
                '  "lives": "abc",   # invalid -> default\n'
                '  "pacgum": 5,\n'
                '  "unknown_key": 1,\n'
                '  "levels": [{"width": 11, "height": 11,'
                ' "level_max_time": 30}]\n'
                '}\n'
            )
        c = load_config(path)
        check(c.lives == 3, "invalid 'lives' falls back to default (3)")
        check(c.pacgum == 5, "valid 'pacgum' is read")
        check(len(c.levels) >= 10, "at least 10 levels are built")
        check(c.levels[0].width == 11 and c.levels[0].level_max_time == 30,
              "level 0 values are read from the file")
        check(c.levels[1].width > 0, "missing levels get defaults")

        bad = os.path.join(tmp, "bad.json")
        with open(bad, "w", encoding="utf-8") as f:
            f.write("[1, 2, 3]")
        check(load_config(bad).lives == 3, "non-dict JSON -> defaults")
        with open(bad, "w", encoding="utf-8") as f:
            f.write("{ broken")
        check(load_config(bad).lives == 3, "broken JSON -> defaults")
        check(load_config(os.path.join(tmp, "nope.json")).lives == 3,
              "missing file -> defaults")


def test_setup(config):
    print("\n[level setup]")
    e = GameEngine(config)
    lvl = e.level
    w, h = lvl.level_config.width, lvl.level_config.height
    corners = {(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)}
    check(e.state == "playing", "engine starts in 'playing'")
    check((e.player.x, e.player.y) == (w // 2, h // 2),
          "player starts in the middle")
    check(len(lvl.ghosts) == 4, "4 ghosts")
    check({(g.x, g.y) for g in lvl.ghosts} == corners,
          "ghosts start one per corner")
    check(set(lvl.super_pacgums) == corners, "super-pacgums in the 4 corners")
    reachable = lvl.maze.get_reachable_cells((e.player.x, e.player.y))
    check(corners <= set(reachable),
          "all 4 corners are reachable (else the level can't be completed)")
    check(all(p in reachable for p in lvl.pacgums),
          "every pacgum is reachable")
    check(0 < len(lvl.pacgums) <= config.pacgum,
          "pacgum count is within config.pacgum")
    check((e.player.x, e.player.y) not in lvl.pacgums
          and not (set(lvl.pacgums) & corners),
          "no pacgum on the player cell or on corners")
    check(e.player.lives == config.lives, "lives come from config")


def test_input_and_movement(config):
    print("\n[input / movement]")
    e = GameEngine(config)
    before = e.player.next_direction
    e.handle_input("X")
    check(e.player.next_direction == before, "invalid direction ignored")
    e.handle_input("N")
    check(e.player.next_direction == "N", "valid direction stored")
    e.state = "paused"
    e.handle_input("S")
    check(e.player.next_direction == "N", "input ignored while paused")

    e = GameEngine(config)
    p, maze = e.player, e.level.maze
    opened = [d for d in DIRS if maze.can_move(p.x, p.y, d)]
    blocked = [d for d in DIRS if not maze.can_move(p.x, p.y, d)]
    check(bool(opened), "centre cell has an open direction")
    if opened:
        d = opened[0]
        p.direction = p.next_direction = d
        start = (p.x, p.y)
        for _ in range(4):
            e.update(0.05)
        moved = abs(p.x - start[0]) + abs(p.y - start[1])
        check(moved == 1, "player moves exactly 1 cell in 0.2 s")
    if blocked:
        e = GameEngine(config)
        p = e.player
        p.direction = p.next_direction = blocked[0]
        start = (p.x, p.y)
        for _ in range(8):
            e.update(0.05)
        check((p.x, p.y) == start, "player stops at a wall")
    else:
        print("  (skip) centre cell has no wall to test against")

    e = GameEngine(config)
    start = (e.player.x, e.player.y)
    e.update(3.0)
    moved = abs(e.player.x - start[0]) + abs(e.player.y - start[1])
    check(moved <= 1, "lag spike (dt=3.0) is clamped: at most 1 step")

    e = GameEngine(config)
    vx, vy = e.get_visual_position()
    check((vx, vy) == (e.player.x, e.player.y),
          "visual position == logical position at start")


def test_pause(config):
    print("\n[pause]")
    e = GameEngine(config)
    e.update(0.05)
    t = e.level.timer.passed
    e.toggle_pause()
    check(e.state == "paused", "toggle_pause -> paused")
    e.update(0.05)
    check(e.level.timer.passed == t, "level timer frozen while paused")
    e.toggle_pause()
    check(e.state == "playing", "toggle_pause again -> playing")
    e.state = "game_over"
    e.toggle_pause()
    check(e.state == "game_over", "toggle_pause ignored in game_over")


def test_pacgums(config):
    print("\n[pacgums]")
    e = GameEngine(config)
    lvl, p = e.level, e.player
    pos = next(iter(lvl.pacgums))
    n, score = len(lvl.pacgums), p.score
    p.x, p.y = pos
    lvl.handle_pacgums()
    check(len(lvl.pacgums) == n - 1, "normal pacgum removed")
    check(p.score == score + config.points_per_pacgum,
          "normal pacgum gives points_per_pacgum")

    corner = next(iter(lvl.super_pacgums))
    score = p.score
    p.x, p.y = corner
    lvl.handle_pacgums()
    check(corner not in lvl.super_pacgums, "super-pacgum removed")
    check(p.score == score + config.points_per_super_pacgum,
          "super-pacgum gives points_per_super_pacgum")
    check(all(g.state == "scared" for g in lvl.ghosts)
          and lvl.ghosts_scared, "super-pacgum scares all ghosts")


def test_scared(config):
    print("\n[scared state]")
    e = GameEngine(config)
    g0, g1 = e.level.ghosts[0], e.level.ghosts[1]
    g1.state = "eaten"
    scare_ghosts(e.level.ghosts)
    check(g0.state == "scared", "chasing ghost becomes scared")
    check(g1.state == "eaten", "eaten ghost is NOT turned scared")
    e.level.ghosts_scared = True
    e.level.scared_timer = 0.1
    e.level.update(0.2)
    check(g0.state == "chasing", "scared ghost returns to chasing")
    check(g1.state == "eaten", "eaten ghost untouched by the timeout")


def test_collisions(config):
    print("\n[collisions]")
    e = GameEngine(config)
    p, g = e.player, e.level.ghosts[0]
    w, h = e.level.level_config.width, e.level.level_config.height
    p.x, p.y = 1, 1
    g.x, g.y = 1, 1
    g.state = "chasing"
    lives = p.lives
    e.check_collisions()
    check(p.lives == lives - 1, "chasing ghost costs one life")
    check((p.x, p.y) == (w // 2, h // 2), "player respawns in the middle")
    check(e.previous_position == (p.x, p.y),
          "previous_position reset after losing a life")

    e = GameEngine(config)
    p, g = e.player, e.level.ghosts[0]
    p.x, p.y = 1, 1
    g.x, g.y = 1, 1
    g.state = "scared"
    score = p.score
    e.check_collisions()
    check(g.state == "eaten" and p.score == score + config.points_per_ghost,
          "scared ghost is eaten and gives points_per_ghost")

    lives = p.lives
    e.check_collisions()
    check(p.lives == lives, "eaten ghost on player's cell is harmless")

    e = GameEngine(config)
    p, g = e.player, e.level.ghosts[0]
    p.lives = 1
    p.x, p.y = 1, 1
    g.x, g.y = 1, 1
    g.state = "chasing"
    e.check_collisions()
    check(e.state == "game_over", "last life lost -> game_over")


def test_level_flow(config):
    print("\n[level flow]")
    total = len(config.levels)
    e = GameEngine(config)
    e.level.pacgums.clear()
    e.level.super_pacgums.clear()
    for _ in range(10):
        e.update(0.05)
    check(e.state == ("level_complete" if total > 1 else "victory"),
          "all pacgums eaten -> level_complete")
    e.update(0.05)
    check(e.state in ("level_complete", "victory"),
          "no progress after a terminal state")

    e.player.score, e.player.lives = 123, 2
    e.next_level()
    check(e.state == "playing" and e.level_index == 1,
          "next_level -> playing, index 1")
    check(e.player.score == 123 and e.player.lives == 2,
          "score and lives carried over")
    w, h = e.level.level_config.width, e.level.level_config.height
    check((e.player.x, e.player.y) == (w // 2, h // 2),
          "player back in the middle")
    check(len(e.level.pacgums) > 0 and e.level.timer.passed == 0,
          "new level has fresh pacgums and timer")

    e = GameEngine(config, total - 1)
    e.level.pacgums.clear()
    e.level.super_pacgums.clear()
    for _ in range(10):
        e.update(0.05)
    check(e.state == "victory", "last level completed -> victory")
    e.next_level()
    check(e.state == "victory", "next_level ignored after victory")

    e = GameEngine(config)
    e.level.timer.passed = timer_total(e)
    e.update(0.01)
    check(e.state == "game_over", "time expired -> game_over")


def test_ghosts(config):
    print("\n[ghosts / pathfinding]")
    e = GameEngine(config)
    lvl = e.level
    w, h = lvl.level_config.width, lvl.level_config.height
    cells = sorted(lvl.maze.get_reachable_cells((e.player.x, e.player.y)))
    sample = cells[::max(1, len(cells) // 15)]
    bad = []
    for g in lvl.ghosts:
        for state in ("chasing", "scared", "eaten"):
            for (x, y) in sample:
                g.x, g.y, g.state = x, y, state
                d = decide_ghost_move(g, e.player, lvl.maze, w, h)
                if d != "" and not (d in DIRS and lvl.maze.can_move(x, y, d)):
                    bad.append((g.name, state, (x, y), d))
    check(not bad, f"every ghost decision is '' or a legal move {bad[:2]}")

    target = (w // 2, h // 2)
    path = find_path(lvl.maze, (0, 0), target)
    x, y, ok = 0, 0, bool(path)
    for d in path:
        ok = ok and lvl.maze.can_move(x, y, d)
        x, y = x + VEC[d][0], y + VEC[d][1]
    check(ok and (x, y) == target, "find_path walks from corner to centre")
    check(find_path(lvl.maze, target, target) == [],
          "find_path start == target -> []")

    e = GameEngine(config)
    g = e.level.ghosts[0]
    g.x, g.y, g.state = w // 2, h // 2, "eaten"
    for _ in range(w * h * 2):
        e.move_ghosts()
        if g.state == "chasing":
            break
    check(g.state == "chasing" and (g.x, g.y) == (g.start_x, g.start_y),
          "eaten ghost walks home, then returns to chasing")

    e = GameEngine(config)
    g = e.level.ghosts[0]
    g.x, g.y = g.start_x, g.start_y
    g.state = "eaten"
    e.move_ghosts()
    check(g.state == "chasing", "ghost eaten ON its corner returns at once")

    e = GameEngine(config)
    g = e.level.ghosts[0]
    e.move_ghosts()
    e.ghost_move_elapsed = e.ghost_move_interval / 2
    vx, vy = e.get_ghost_visual_position(g)
    lo_x, hi_x = sorted((g.previous_x, g.x))
    lo_y, hi_y = sorted((g.previous_y, g.y))
    check(lo_x <= vx <= hi_x and lo_y <= vy <= hi_y,
          "ghost visual position lies between previous and current cell")


def test_highscores(config):
    print("\n[highscores]")
    check(is_valid_name("Alice 01"), "valid name accepted")
    check(not is_valid_name(""), "empty name rejected")
    check(not is_valid_name("   "), "spaces-only name rejected")
    check(not is_valid_name("a" * 11), "name longer than 10 rejected")
    check(not is_valid_name("bad@name"), "symbol in name rejected")
    check(not is_valid_name(123), "non-str name rejected")

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "hs.json")
        check(load_highscores(path) == [], "missing file -> []")
        check(is_highscore([], 0), "empty list: any score qualifies")
        check(add_highscore(path, "Alice", 100), "add_highscore succeeds")
        check(not add_highscore(path, "bad@name", 5), "bad name refused")
        check(not add_highscore(path, "Bob", -1), "negative score refused")
        check(not add_highscore(path, "Bob", True), "bool score refused")
        for i in range(12):
            add_highscore(path, f"P{i}", i * 10)
        scores = load_highscores(path)
        values = [s for _, s in scores]
        check(len(scores) == 10, "only the top 10 are kept")
        check(values == sorted(values, reverse=True), "sorted descending")
        check(scores[1][0] == "Alice" and scores[2][0] == "P10",
              "tie: the older entry stays higher")
        check(not is_highscore(scores, values[-1]),
              "full list: tie with the lowest is refused")
        check(is_highscore(scores, values[-1] + 1),
              "full list: better than the lowest is accepted")

        with open(path, "w", encoding="utf-8") as f:
            f.write("{ not json")
        check(load_highscores(path) == [], "corrupt file -> []")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"a": 1}, f)
        check(load_highscores(path) == [], "non-list JSON -> []")
        with open(path, "w", encoding="utf-8") as f:
            json.dump([
                {"name": "Ok", "score": 5},
                {"name": "x" * 20, "score": 9},
                {"name": "Neg", "score": -3},
                {"name": "B", "score": True},
                "junk",
                {"name": "Good", "score": 7},
            ], f)
        check([n for n, _ in load_highscores(path)] == ["Good", "Ok"],
              "bad entries skipped, good ones kept")
        check(not save_highscores(
            os.path.join(tmp, "nodir", "x.json"), []),
            "save to an impossible path -> False, no crash")


def run_headless(config) -> int:
    tests = [
        test_parsing, test_setup, test_input_and_movement, test_pause,
        test_pacgums, test_scared, test_collisions, test_level_flow,
        test_ghosts, test_highscores,
    ]
    for t in tests:
        try:
            t(config)
        except Exception as exc:  # a crash is a failed check, not a stop
            check(False, f"{t.__name__} crashed: "
                         f"{type(exc).__name__}: {exc}")
    failed = [label for ok, label in RESULTS if not ok]
    print(f"\n=== {len(RESULTS) - len(failed)}/{len(RESULTS)} passed ===")
    for label in failed:
        print("  FAILED:", label)
    return len(failed)


# --------------------------------------------------------------------------
# Visual tester
# --------------------------------------------------------------------------

WIN_W, WIN_H = 900, 820
HUD_H, LOG_H = 70, 110
GHOST_COLORS = {
    "Blinky": (255, 0, 0),
    "Pinky": (255, 184, 255),
    "Inky": (0, 255, 255),
    "Clyde": (255, 184, 82),
}


def snapshot(e: GameEngine) -> dict:
    return {
        "state": e.state,
        "score": e.player.score,
        "lives": e.player.lives,
        "level": e.level_index,
        "ghosts": [g.state for g in e.level.ghosts],
        "left": len(e.level.pacgums) + len(e.level.super_pacgums),
    }


def log_changes(e: GameEngine, old: dict, log: deque) -> dict:
    new = snapshot(e)
    if new["level"] != old["level"]:
        log.append(f"level {old['level'] + 1} -> {new['level'] + 1}")
        return new
    if new["state"] != old["state"]:
        log.append(f"state: {old['state']} -> {new['state']}")
    if new["score"] != old["score"]:
        log.append(f"score {new['score'] - old['score']:+d}")
    if new["lives"] != old["lives"]:
        log.append(f"lives {new['lives'] - old['lives']:+d}")
    for g, a, b in zip(e.level.ghosts, old["ghosts"], new["ghosts"]):
        if a != b:
            log.append(f"{getattr(g, 'name', 'ghost')}: {a} -> {b}")
    return new


def run_visual(config) -> None:
    import pygame as pg

    pg.init()
    screen = pg.display.set_mode((WIN_W, WIN_H))
    pg.display.set_caption("Pac-Man logic tester")
    font = pg.font.SysFont(None, 24)
    small = pg.font.SysFont(None, 20)
    big = pg.font.SysFont(None, 60)
    clock = pg.time.Clock()

    engine = GameEngine(config)
    log: deque = deque(maxlen=6)
    snap = snapshot(engine)
    show_logic = False
    keymap = {
        pg.K_UP: "N", pg.K_w: "N", pg.K_RIGHT: "E", pg.K_d: "E",
        pg.K_DOWN: "S", pg.K_s: "S", pg.K_LEFT: "W", pg.K_a: "W",
    }
    help_lines = (
        "Arrows/WASD move | P pause | N next level | R restart | "
        "V logical cells",
        "K scare ghosts | L force collision (Blinky) | C clear pacgums | "
        "X time almost up | J lag spike (dt=3s)",
    )

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                k = event.key
                if k in keymap:
                    engine.handle_input(keymap[k])
                elif k in (pg.K_p, pg.K_ESCAPE):
                    engine.toggle_pause()
                elif k == pg.K_n:
                    engine.next_level()
                elif k == pg.K_r:
                    engine = GameEngine(config)
                    snap = snapshot(engine)
                    log.append("restarted")
                elif k == pg.K_v:
                    show_logic = not show_logic
                elif k == pg.K_k:
                    scare_ghosts(engine.level.ghosts)
                    engine.level.ghosts_scared = True
                    engine.level.scared_timer = 7.0
                    log.append("(test) ghosts scared")
                elif k == pg.K_l:
                    g = engine.level.ghosts[0]
                    g.x, g.y = engine.player.x, engine.player.y
                    engine.check_collisions()
                    log.append("(test) forced collision with ghost 0")
                elif k == pg.K_c:
                    engine.level.pacgums.clear()
                    engine.level.super_pacgums.clear()
                    log.append("(test) pacgums cleared")
                elif k == pg.K_x:
                    engine.level.timer.passed = max(
                        0.0, timer_total(engine) - 3.0)
                    log.append("(test) 3 s left")
                elif k == pg.K_j:
                    engine.update(3.0)
                    log.append("(test) lag spike dt=3.0")

        engine.update(dt)
        snap = log_changes(engine, snap, log)

        lvl = engine.level
        w, h = lvl.level_config.width, lvl.level_config.height
        area_h = WIN_H - HUD_H - LOG_H
        cell = max(4, min(WIN_W // w, area_h // h))
        ox = (WIN_W - w * cell) // 2
        oy = HUD_H + (area_h - h * cell) // 2

        screen.fill((0, 0, 0))

        # maze
        grid = lvl.maze.maze
        for y, row in enumerate(grid):
            for x, v in enumerate(row):
                px, py = ox + x * cell, oy + y * cell
                if v == 15:
                    pg.draw.rect(screen, (45, 45, 45), (px, py, cell, cell))
                c = (40, 70, 255)
                if v & 1:
                    pg.draw.line(screen, c, (px, py), (px + cell, py), 2)
                if v & 2:
                    pg.draw.line(screen, c, (px + cell, py),
                                 (px + cell, py + cell), 2)
                if v & 4:
                    pg.draw.line(screen, c, (px, py + cell),
                                 (px + cell, py + cell), 2)
                if v & 8:
                    pg.draw.line(screen, c, (px, py), (px, py + cell), 2)

        def centre(cx: float, cy: float) -> tuple[int, int]:
            return (int(ox + (cx + 0.5) * cell), int(oy + (cy + 0.5) * cell))

        for (x, y) in lvl.pacgums:
            pg.draw.circle(screen, (255, 220, 160), centre(x, y),
                           max(2, cell // 8))
        for (x, y) in lvl.super_pacgums:
            pg.draw.circle(screen, (255, 120, 200), centre(x, y),
                           max(4, cell // 3))

        # ghosts
        for g in lvl.ghosts:
            gx, gy = engine.get_ghost_visual_position(g)
            pos = centre(gx, gy)
            if g.state == "eaten":
                pg.draw.circle(screen, (230, 230, 230), pos,
                               max(3, cell // 6), 1)
            else:
                colour = GHOST_COLORS.get(getattr(g, "name", ""), (200, 0, 0))
                if g.state == "scared":
                    blink = lvl.scared_timer < 2 and int(
                        lvl.scared_timer * 5) % 2 == 0
                    colour = (240, 240, 240) if blink else (30, 30, 255)
                pg.draw.circle(screen, colour, pos, int(cell * 0.4))
            if show_logic:
                pg.draw.rect(screen, (255, 255, 255),
                             (ox + g.x * cell, oy + g.y * cell, cell, cell), 1)

        # player
        vx, vy = engine.get_visual_position()
        pg.draw.circle(screen, (255, 255, 0), centre(vx, vy),
                       int(cell * 0.4))
        if show_logic:
            pg.draw.rect(screen, (255, 255, 0),
                         (ox + engine.player.x * cell,
                          oy + engine.player.y * cell, cell, cell), 1)

        # HUD
        p = engine.player
        screen.blit(font.render(
            f"Score {p.score}   Lives {p.lives}   "
            f"Level {engine.level_index + 1}/{len(config.levels)}   "
            f"Time left {max(0.0, time_left(engine)):.1f}s   "
            f"State: {engine.state}", True, (255, 255, 255)), (10, 8))
        scared = (f"scared {lvl.scared_timer:.1f}s"
                  if lvl.ghosts_scared else "not scared")
        screen.blit(font.render(
            f"Pacgums left {len(lvl.pacgums)} + {len(lvl.super_pacgums)} "
            f"super   {scared}   dir={p.direction!r} "
            f"next={p.next_direction!r}", True, (180, 180, 180)), (10, 38))

        # log + help
        ly = WIN_H - LOG_H + 4
        for i, line in enumerate(help_lines):
            screen.blit(small.render(line, True, (120, 200, 120)),
                        (10, ly + i * 18))
        for i, line in enumerate(log):
            screen.blit(small.render(line, True, (230, 200, 120)),
                        (10, ly + 42 + i * 14))

        # overlays
        messages = {
            "paused": "PAUSED (P)",
            "level_complete": "LEVEL COMPLETE - N",
            "victory": "VICTORY - R",
            "game_over": "GAME OVER - R",
        }
        if engine.state in messages:
            text = big.render(messages[engine.state], True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=(WIN_W // 2, WIN_H // 2)))

        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    cfg = load_config(args[0] if args else "config.json")
    failures = run_headless(cfg)
    if "--no-gui" not in sys.argv:
        run_visual(cfg)
    sys.exit(1 if failures else 0)
