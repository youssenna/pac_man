from typing import Tuple, List, Dict, Any
from enum import Enum


class Character(Enum):
    PLAYER = "player"
    GHOST = "ghost"


class PacmanItems:
    def __init__(self, item_type: Character, pos: Tuple[int]):
        self.item_type: Character = item_type
        self.pos: Tuple[int] = pos
        
    def 
    