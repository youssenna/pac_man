
from gui import PacmanGui, GameInfo
from backend import GameEngine, LoadConfig
from mazegenerator import MazeGenerator

def main():
    config = LoadConfig().load_config('config.json')
    engine = GameEngine(config)
    game_info = GameInfo(config, (1280, 720))
    
    
    
    maze = MazeGenerator()
    gui = PacmanGui(maze.maze, engine, (1280, 650))
    gui.run()


if __name__ == "__main__":
    main()
