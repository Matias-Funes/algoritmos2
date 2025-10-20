from . import constants
import pygame
from .elements import Tree, Person, Merchandise
import random 
import os


class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # grid: 0 libre, 1 árbol/obstáculo, 2 persona, 3 Mercancía
        self.grid = [[0 for _ in range(constants.GRID_WIDTH)] for _ in range(constants.GRID_HEIGHT)]

        # cargar imagen de césped una sola vez
        grass_path = os.path.join("assets", "images", "objects", "Grass.png")
        try:
            self.grass_image = pygame.image.load(grass_path).convert()
            self.grass_image = pygame.transform.scale(self.grass_image, (constants.TILE, constants.TILE))
        except Exception:
            self.grass_image = pygame.Surface((constants.TILE, constants.TILE))
            self.grass_image.fill((50, 150, 50))

        # crear árboles y marcar grid como bloqueada (comprobando celda libre)
        self.trees = []
        for _ in range(constants.NUM_TREES):
            attempts = 0
            while attempts < 200:  # Máximo 200 intentos por árbol.Limita los intentos para evitar bucles infinitos.Si no encuentra espacio en 200 intentos, pasa al siguiente árbol
                #Generación de posición aleatoria:
                gx = random.randint(0, constants.GRID_WIDTH - 1)
                gy = random.randint(0, constants.GRID_HEIGHT - 1)
                attempts += 1
                if self.grid[gy][gx] == 0:# Si la celda está vacía (0 = libre)
                    self.grid[gy][gx] = 1# Marca la celda como ocupada (1 = árbol)
                    px, py = self.cell_to_pixel(gx, gy)# Convierte coordenadas de grid a píxeles
                    self.trees.append(Tree(px, py)) # Crea y añade el árbol a la lista
                    break  # Sale del bucle while y pasa al siguiente árbol

        # generar personas en celdas libres
        self.people = []
        for _ in range(constants.NUM_PEOPLE):
            attempts = 0
            while attempts < 200:
                gx = random.randint(0, constants.GRID_WIDTH - 1)
                gy = random.randint(0, constants.GRID_HEIGHT - 1)
                attempts += 1
                if self.grid[gy][gx] == 0:
                    self.grid[gy][gx] = 2
                    px, py = self.cell_to_pixel(gx, gy)
                    self.people.append(Person(px, py))
                    break

        # mercancías usando MERCH_COUNTS
        self.merch = []
        for kind, cnt in constants.MERCH_COUNTS.items():
            for _ in range(cnt):
                attempts = 0
                while attempts < 200:
                    gx = random.randint(0, constants.GRID_WIDTH - 1)
                    gy = random.randint(0, constants.GRID_HEIGHT - 1)
                    attempts += 1
                    if self.grid[gy][gx] == 0:
                        self.grid[gy][gx] = 3
                        px, py = self.cell_to_pixel(gx, gy)
                        self.merch.append(Merchandise(px, py, kind))
                        break




    # Esta función convierte coordenadas en píxeles a coordenadas de la cuadrícula (celda) del mapa.
    def pixel_to_cell(self, x, y):
        return int(x) // constants.TILE, int(y) // constants.TILE



    # convert grid coords (gx,gy) to top-left pixel of that cell
    def cell_to_pixel(self, gx, gy):
        return gx * constants.TILE, gy * constants.TILE
    




    #determina si una celda en la cuadrícula es transitable (caminable) o no
    def is_walkable(self, gx, gy):
        #Verifica si las coordenadas (gx, gy) están fuera de los límites de la cuadrícula.
        if gx < 0 or gy < 0 or gx >= constants.GRID_WIDTH or gy >= constants.GRID_HEIGHT:
            return False
        # 0=libre, 2=persona, 3=merch son caminables
        return self.grid[gy][gx] in (0, 2, 3)
    


    #se utiliza para obtener las celdas adyacentes a una celda específica en la cuadrícula.
    def get_neighbors(self, gx, gy):
        # es una lista de tuplas que representan las direcciones en las que se puede mover desde la celda actual:
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # direcciones posibles: derecha,izquierda,abajo,arriba
        for dx, dy in dirs:
            nx, ny = gx + dx, gy + dy
            #Verifica si las nuevas coordenadas nx y ny están dentro de los límites de la cuadrícula. Usa self.is_walkable(nx, ny) para comprobar si la celda es caminable.
            if 0 <= nx < constants.GRID_WIDTH and 0 <= ny < constants.GRID_HEIGHT and self.is_walkable(nx, ny):
            #utiliza yield para devolver las coordenadas adyacentes (nx, ny).
                yield nx, ny

    #screen: la superficie de Pygame donde se dibuja todo (la ventana).
    def draw(self, screen):
        # dibujar background tiled
        #Paso 1 — dibujar el fondo en mosaico:
        for gy in range(constants.GRID_HEIGHT):
            #Recorre todas las celdas de la grid por fila y columna.
            for gx in range(constants.GRID_WIDTH):
                #Convierte las coordenadas de celda (gx,gy) a píxeles (esquina superior izquierda).
                px, py = self.cell_to_pixel(gx, gy)
                #Pega la imagen del césped en esa posición. Así se forma un fondo "tiled" (mosaico) que cubre toda la pantalla.
                screen.blit(self.grass_image, (px, py))

        # Paso 2 — dibujar los objetos encima del fondo:
        for tree in self.trees:
            tree.draw(screen)
        #Recorre las listas de objetos y llama a su método draw. Esos métodos deben usar las coordenadas en píxeles (x,y) del objeto para blitear su sprite.
        for person in self.people:
            person.draw(screen)
        #El orden importa: primero fondo, luego árboles/personas/mercancías para que se vean por encima.
        for m in self.merch:
            m.draw(screen)

    #Propósito: dibujar en pantalla el texto del inventario del personaje (puntos, rescatados y cantidades de recursos)
    #screen: Surface de Pygame donde se dibuja.character: objeto Character que contiene .inventory (diccionario).
    def draw_inventory(self, screen, character):
        #Paso 1 — preparar fuente y posición inicial:crea una fuente del sistema tamaño 24 (None = fuente por defecto).
        font = pygame.font.SysFont(None, 24)
        y = 10
        x = 10
        #Paso 2 — obtener inventario:
        inv = character.inventory
        
        # Paso 3 — preparar líneas de texto:
        items = [
            f"Puntos: {inv['points']}",
            f"Rescatados: {inv['rescued']}",
            f"Ropa: {inv['clothes']}",
            f"Comida: {inv['food']}",
            f"Medicina: {inv['medicine']}"
        ]
        #Paso 4 — renderizar y blitear cada línea:
        for text in items:
            surf = font.render(text, True, constants.WHITE)
            screen.blit(surf, (x, y))
            y += 25