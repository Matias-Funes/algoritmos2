#tamaños
WIDTH, HEIGHT = 900, 600
PLAYER = 20
GRASS = 30
TREE = 25
PERSON = 25
MERCH_SIZE = 20

# tamaño de celda (tile) usado por la grid
TILE = GRASS
GRID_WIDTH = WIDTH // TILE
GRID_HEIGHT = HEIGHT // TILE

#colores
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)

# cantidades


NUM_TREES = 10
NUM_PEOPLE = 10
NUM_MERCH = 50

# puntos
POINTS_PERSON = 50
MERCH_POINTS = {
    "clothes": 5,
    "food": 10,
    "medicine": 20
}

# distribución de mercancías (la suma debe ser NUM_MERCH)
MERCH_COUNTS = {
    "clothes": 20,
    "food": 15,
    "medicine": 15
}

# Tipos de minas y sus radios
MINE_TYPES = {
    "O1": {"radius": 10, "type": "circular", "static": True},
    "O2": {"radius": 5, "type": "circular", "static": True},
    "T1": {"radius": 10, "type": "horizontal", "static": True},
    "T2": {"radius": 5, "type": "vertical", "static": True},
    "G1": {"radius": 7, "type": "circular", "static": False}
}

# Cantidad de minas por tipo
MINES_COUNT = {
    "O1": 3,
    "O2": 3,
    "T1": 3,
    "T2": 3,
    "G1": 3
}

# Tiempo para minas móviles (frames)
G1_TOGGLE_TIME = 300  # 5 segundos a 60fps

# Colores para debug/visualización
MINE_COLORS = {
    "O1": (255, 0, 0, 128),  # Rojo semi-transparente
    "O2": (255, 100, 0, 128),  # Naranja semi-transparente
    "T1": (255, 200, 0, 128),  # Amarillo semi-transparente
    "T2": (255, 0, 100, 128),  # Rosa semi-transparente
    "G1": (255, 0, 255, 128)   # Magenta semi-transparente
}

# Modo de depuración
DEBUG_MODE = True  # Cambia a False para desactivar el modo de depuración