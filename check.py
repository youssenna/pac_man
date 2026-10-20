from maze import Maze
from characters import Player, Blinky, Pinky, Inky, Clyde
from pacgums import (
    get_reserved_cells,
    place_super_pacgums,
    place_pacgums,
)
from parsing import Config


WIDTH = 21
HEIGHT = 21
SEED = 42


def print_maze(maze, player, ghosts, pacgums, super_pacgums):
    width = len(maze.maze[0])
    height = len(maze.maze)

    ghost_positions = {
        (ghost.x, ghost.y): "G"
        for ghost in ghosts
    }

    for y in range(height):
        # Top walls
        for x in range(width):
            print("+", end="")

            if maze.maze[y][x] & Maze.BITS["N"]:
                print("---", end="")
            else:
                print("   ", end="")

        print("+")

        # Cells and vertical walls
        for x in range(width):
            # Left wall
            if maze.maze[y][x] & Maze.BITS["W"]:
                print("|", end="")
            else:
                print(" ", end="")

            position = (x, y)

            # Cell content
            if position == (player.x, player.y):
                symbol = "P"
            elif position in ghost_positions:
                symbol = ghost_positions[position]
            elif position in super_pacgums:
                symbol = "O"
            elif position in pacgums:
                symbol = "."
            else:
                symbol = " "

            print(f" {symbol} ", end="")

        # Right wall
        if maze.maze[y][width - 1] & Maze.BITS["E"]:
            print("|")
        else:
            print(" ")

    # Bottom walls
    for x in range(width):
        print("+", end="")

        if maze.maze[height - 1][x] & Maze.BITS["S"]:
            print("---", end="")
        else:
            print("   ", end="")

    print("+")


def main():
    # --------------------------------------------------
    # 1. Create the maze
    # --------------------------------------------------
    maze = Maze(
        width=WIDTH,
        height=HEIGHT,
        seed=SEED,
    )

    # --------------------------------------------------
    # 2. Create the player in the middle
    # --------------------------------------------------
    player = Player(
        x=WIDTH // 2,
        y=HEIGHT // 2,
        direction="N",
        lives=3
    )

    # --------------------------------------------------
    # 3. Create the four ghosts in the corners
    # --------------------------------------------------
    ghosts = [
        Blinky(0, 0, "N"),
        Pinky(WIDTH - 1, 0, "S"),
        Inky(0, HEIGHT - 1, "E"),
        Clyde(WIDTH - 1, HEIGHT - 1, "W"),
    ]

    # --------------------------------------------------
    # 4. Get reserved cells
    # --------------------------------------------------
    reserved = get_reserved_cells(
        player=player,
        ghosts=ghosts,
        width=WIDTH,
        height=HEIGHT,
    )

    print("Reserved:", reserved)
    print("Reserved count:", len(reserved))

    # --------------------------------------------------
    # 5. Place super pacgums
    # --------------------------------------------------
    super_pacgums = place_super_pacgums(
        width=WIDTH,
        height=HEIGHT,
    )

    print("Super pacgums:", super_pacgums)

    # --------------------------------------------------
    # 6. Load config
    # --------------------------------------------------
    config = Config()

    # --------------------------------------------------
    # 7. Place normal pacgums
    # --------------------------------------------------
    pacgums = place_pacgums(
        width=WIDTH,
        height=HEIGHT,
        reserved=reserved,
        config=config,
    )

    print("Pacgums count:", len(pacgums))
    print("Expected:", config.pacgum)

    # --------------------------------------------------
    # 8. Verify that super pacgums are reserved
    # --------------------------------------------------
    assert super_pacgums <= reserved, (
        "Some super pacgums are not reserved!"
    )

    # --------------------------------------------------
    # 9. Verify pacgums don't overlap reserved cells
    # --------------------------------------------------
    assert not (pacgums & reserved), (
        "Pacgums overlap with reserved cells!"
    )

    # --------------------------------------------------
    # 10. Verify pacgums don't overlap super pacgums
    # --------------------------------------------------
    assert not (pacgums & super_pacgums), (
        "Pacgums overlap with super pacgums!"
    )

    # --------------------------------------------------
    # 11. Verify pacgum count
    # --------------------------------------------------
    expected_count = min(
        config.pacgum,
        WIDTH * HEIGHT - len(reserved),
    )

    assert len(pacgums) == expected_count, (
        f"Expected {expected_count} pacgums, "
        f"got {len(pacgums)}"
    )

    print()
    print("All checks passed!")
    print()

    # --------------------------------------------------
    # 12. Print the maze
    # --------------------------------------------------
    print_maze(
        maze=maze,
        player=player,
        ghosts=ghosts,
        pacgums=pacgums,
        super_pacgums=super_pacgums,
    )


if __name__ == "__main__":
    main()
