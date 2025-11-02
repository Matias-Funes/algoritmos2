# Cantidades (TOTAL 60 elementos según PDF)
NUM_TREES = 10
NUM_PEOPLE = 10  # 10 personas según PDF
NUM_MERCH = 50   # 50 mercancías según PDF

# Puntos (según PDF)
POINTS_PERSON = 50
MERCH_POINTS = {
    "clothes": 5,
    "food": 10,
    "medicine": 20,
    "weapons": 50  # Armamentos según PDF
}

# Distribución de mercancías (total debe ser 50 según PDF)
MERCH_COUNTS = {
    "clothes": 15,    # Ropa
    "food": 15,       # Alimentos
    "medicine": 10,   # Medicamentos
    "weapons": 10     # Armamentos
}# Tamaños
WIDTH, HEIGHT = 900, 600
# Panel de Control Fijo (UI)
UI_PANEL_HEIGHT = 80  # Altura de la barra de botones (puedes ajustarla)
UI_PANEL_Y = HEIGHT - UI_PANEL_HEIGHT # Posición Y donde empieza el panel
# Mundo del Juego (Área de simulación)
GAME_WORLD_HEIGHT = HEIGHT - UI_PANEL_HEIGHT # El mapa ahora es más bajo
PLAYER = 20
GRASS = 30
TREE = 25
PERSON = 25
MERCH_SIZE = 20

# Tamaño de celda (tile) usado por la grid
TILE = GRASS
GRID_WIDTH = WIDTH // TILE
GRID_HEIGHT = GAME_WORLD_HEIGHT // TILE

# Colores
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
RED = (255, 0, 0)

# Cantidades
NUM_TREES = 10
NUM_PEOPLE = 10
NUM_MERCH = 50

# Puntos
POINTS_PERSON = 50
MERCH_POINTS = {
    "clothes": 5,
    "food": 10,
    "medicine": 20,
    "weapons": 50
}

# Distribución de mercancías (total debe ser NUM_MERCH)
MERCH_COUNTS = {
    "clothes": 15,
    "food": 15,
    "medicine": 10,
    "weapons": 10
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

# Colores para visualización de minas
MINE_COLORS = {
    "O1": (255, 0, 0, 128),
    "O2": (255, 100, 0, 128),
    "T1": (255, 200, 0, 128),
    "T2": (255, 0, 100, 128),
    "G1": (255, 0, 255, 128)
}

# Modo de depuración
DEBUG_MODE = True  # Cambia a False para desactivar visualización de áreas de minas