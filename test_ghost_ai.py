import random
import pygame

from maze import Maze
from characters import Player, Blinky, Pinky, Inky, Clyde
from ghost_ai import decide_ghost_move
from move import move_character


# ---------- SETTINGS ----------

CELL_SIZE = 28
WIDTH = 21
HEIGHT = 21

HUD_HEIGHT = 100
WINDOW_WIDTH = WIDTH * CELL_SIZE
WINDOW_HEIGHT = HEIGHT * CELL_SIZE + HUD_HEIGHT

FPS = 60

BLACK = (10, 10, 20)
WHITE = (240, 240, 240)
BLUE = (40, 80, 220)
YELLOW = (255, 220, 0)
RED = (240, 50, 50)
PINK = (255, 130, 200)
CYAN = (50, 230, 230)
ORANGE = (255, 165, 50)
GREEN = (80, 220, 100)

GHOST_COLORS = {
    "Blinky": RED,
    "Pinky": PINK,
    "Inky": CYAN,
    "Clyde": ORANGE,
}

DIRECTIONS = {
    pygame.K_UP: "N",
    pygame.K_RIGHT: "E",
    pygame.K_DOWN: "S",
    pygame.K_LEFT: "W",
}

OPPOSITES = {
    "N": "S",
    "S": "N",
    "E": "W",
    "W": "E",
}


# ---------- GAME SETUP ----------

def create_game():
    random.seed(42)

    maze = Maze(WIDTH, HEIGHT, seed=42)

    player = Player(1, 1, "E", 3)

    ghosts = [
        Blinky(19, 19, "N"),
        Pinky(19, 1, "W"),
        Inky(1, 19, "N"),
        Clyde(10, 1, "W"),
    ]

    return maze, player, ghosts


# ---------- DRAWING ----------

def draw_maze(screen, maze):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            rect = pygame.Rect(
                x * CELL_SIZE,
                y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )

            pygame.draw.rect(screen, BLACK, rect)

            walls = {
                "N": (
                    (rect.left, rect.top),
                    (rect.right, rect.top),
                ),
                "E": (
                    (rect.right, rect.top),
                    (rect.right, rect.bottom),
                ),
                "S": (
                    (rect.left, rect.bottom),
                    (rect.right, rect.bottom),
                ),
                "W": (
                    (rect.left, rect.top),
                    (rect.left, rect.bottom),
                ),
            }

            for direction, points in walls.items():
                if not maze.can_move(x, y, direction):
                    pygame.draw.line(
                        screen,
                        BLUE,
                        points[0],
                        points[1],
                        2,
                    )


def draw_character(screen, character, color):
    center = (
        character.x * CELL_SIZE + CELL_SIZE // 2,
        character.y * CELL_SIZE + CELL_SIZE // 2,
    )

    pygame.draw.circle(
        screen,
        color,
        center,
        CELL_SIZE // 2 - 3,
    )


def draw_game(
    screen,
    font,
    small_font,
    maze,
    player,
    ghosts,
    message,
):
    screen.fill(BLACK)

    draw_maze(screen, maze)

    # Draw player.
    draw_character(screen, player, YELLOW)

    # Draw ghosts.
    for ghost in ghosts:
        color = GHOST_COLORS[ghost.name]

        if ghost.state == "scared":
            color = BLUE
        elif ghost.state == "eaten":
            color = WHITE

        draw_character(screen, ghost, color)

    # HUD.
    hud_y = HEIGHT * CELL_SIZE

    pygame.draw.rect(
        screen,
        (25, 25, 35),
        (0, hud_y, WINDOW_WIDTH, HUD_HEIGHT),
    )

    controls = (
        "Arrows: Move | SPACE: Step | "
        "C: Chase | S: Scared | E: Eaten | R: Reset"
    )

    screen.blit(
        font.render(controls, True, WHITE),
        (8, hud_y + 8),
    )

    state_text = " | ".join(
        f"{ghost.name}: {ghost.state}"
        for ghost in ghosts
    )

    screen.blit(
        small_font.render(state_text, True, GREEN),
        (8, hud_y + 38),
    )

    screen.blit(
        small_font.render(message, True, YELLOW),
        (8, hud_y + 62),
    )

    pygame.display.flip()


# ---------- AI TESTS ----------

def check_ghost_move(ghost, move, maze):
    """Return whether a ghost's chosen move is legal."""
    if move == "":
        return True

    if move not in ("N", "E", "S", "W"):
        return False

    return maze.can_move(ghost.x, ghost.y, move)


def check_scared_move(ghost, move, maze):
    """Check the no-reversal rule for scared ghosts."""
    available_moves = [
        direction
        for direction in ("N", "E", "S", "W")
        if maze.can_move(ghost.x, ghost.y, direction)
    ]

    if not available_moves:
        assert move == "", (
            f"{ghost.name}: expected no move, got {move!r}"
        )
        return

    opposite = OPPOSITES[ghost.direction]

    non_reverse_moves = [
        direction
        for direction in available_moves
        if direction != opposite
    ]

    if non_reverse_moves:
        assert move in non_reverse_moves, (
            f"{ghost.name}: reversed direction even though "
            f"other moves were available. Move: {move}"
        )
    else:
        assert move == opposite, (
            f"{ghost.name}: should reverse at a dead end; "
            f"expected {opposite}, got {move!r}"
        )


# ---------- MAIN LOOP ----------

def main():
    pygame.init()

    screen = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT)
    )

    pygame.display.set_caption("Ghost AI Visual Tester")

    font = pygame.font.SysFont(None, 19)
    small_font = pygame.font.SysFont(None, 20)
    clock = pygame.time.Clock()

    maze, player, ghosts = create_game()

    message = "Press SPACE to test ghost decisions."

    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_r:
                    maze, player, ghosts = create_game()
                    message = "Game reset. Seed = 42."
                    print("\n--- GAME RESET ---")

                elif event.key == pygame.K_c:
                    for ghost in ghosts:
                        ghost.state = "chasing"

                    message = "All ghosts are chasing."
                    print("\n--- CHASING MODE ---")

                elif event.key == pygame.K_s:
                    for ghost in ghosts:
                        ghost.state = "scared"

                    message = "All ghosts are scared."
                    print("\n--- SCARED MODE ---")

                elif event.key == pygame.K_e:
                    for ghost in ghosts:
                        ghost.state = "eaten"

                    message = "All ghosts are eaten."
                    print("\n--- EATEN MODE ---")

                elif event.key in DIRECTIONS:
                    direction = DIRECTIONS[event.key]

                    move_character(player, maze, direction)

                    print(
                        f"Player: direction={direction}, "
                        f"position=({player.x}, {player.y})"
                    )

                elif event.key == pygame.K_SPACE:
                    results = []

                    print("\n--- GHOST AI STEP ---")
                    print(
                        f"Player position: "
                        f"({player.x}, {player.y})"
                    )

                    for ghost in ghosts:
                        old_position = (ghost.x, ghost.y)
                        old_state = ghost.state
                        old_direction = ghost.direction

                        move = decide_ghost_move(
                            ghost,
                            player,
                            maze,
                            WIDTH,
                            HEIGHT,
                        )

                        # Verify that the AI selected a legal move.
                        if not check_ghost_move(ghost, move, maze):
                            message = (
                                f"FAIL: {ghost.name} selected "
                                f"invalid move {move!r}"
                            )
                            print(message)
                            break

                        # Test the actual scared movement rule.
                        if old_state == "scared":
                            try:
                                check_scared_move(
                                    ghost, move, maze
                                )
                            except AssertionError as error:
                                message = f"FAIL: {error}"
                                print(message)
                                break

                        print(
                            f"[{old_state.upper()}] {ghost.name}: "
                            f"position={old_position}, "
                            f"direction={old_direction}, "
                            f"move={move or 'STAY'}"
                        )

                        # Execute the chosen move.
                        move_character(ghost, maze, move)

                        new_position = (ghost.x, ghost.y)

                        if old_state == "scared":
                            print(
                                f"    New position: {new_position}, "
                                f"new direction={ghost.direction}"
                            )

                            print(
                                f"    PASS: {ghost.name} obeys "
                                f"the no-reversal rule"
                            )

                        results.append(
                            f"{ghost.name}: {move or 'STAY'} "
                            f"{old_position}->{new_position}"
                        )

                    else:
                        message = " | ".join(results)

        draw_game(
            screen,
            font,
            small_font,
            maze,
            player,
            ghosts,
            message,
        )

    pygame.quit()


if __name__ == "__main__":
    main()
