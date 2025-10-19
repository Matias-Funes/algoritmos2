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