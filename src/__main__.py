from .user_interface import PacmanGui
from mazegenerator import MazeGenerator


def main():
    maze = MazeGenerator()
    gui = PacmanGui(maze.maze)
    gui.run()   

if __name__ == "__main__":
    main()