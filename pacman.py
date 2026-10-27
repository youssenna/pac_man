
from gui import PacmanGui, GameInfo
from backend import load_config
from mazegenerator import MazeGenerator

def main():
    conf = load_config("config.json")
    game_info = GameInfo(conf, (1280, 720))
    maze = MazeGenerator()
    gui = PacmanGui(maze.maze, game_info)
    gui.run()


if __name__ == "__main__":
    main()
