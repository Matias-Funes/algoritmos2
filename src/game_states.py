from enum import Enum

# Definición de los estados del juego
class GameState(Enum):
    MENU = 1
    PLAYING = 2  
    PAUSED = 3
    GAME_OVER = 4