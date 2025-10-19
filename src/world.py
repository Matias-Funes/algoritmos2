from . import constants
import pygame
from .elements import Tree, Person, Merchandise
import random 
import os


class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # grid: 0 libre, 1 árbol/obstáculo, 2 persona, 3 merch
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
            while attempts < 200:
                gx = random.randint(0, constants.GRID_WIDTH - 1)
                gy = random.randint(0, constants.GRID_HEIGHT - 1)
                attempts += 1
                if self.grid[gy][gx] == 0:
                    self.grid[gy][gx] = 1
                    px, py = self.cell_to_pixel(gx, gy)
                    self.trees.append(Tree(px, py))
                    break

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

    # convert pixel coords to grid coords
    def pixel_to_cell(self, x, y):
        return int(x) // constants.TILE, int(y) // constants.TILE

    # convert grid coords (gx,gy) to top-left pixel of that cell
    def cell_to_pixel(self, gx, gy):
        return gx * constants.TILE, gy * constants.TILE

    def is_walkable(self, gx, gy):
        if gx < 0 or gy < 0 or gx >= constants.GRID_WIDTH or gy >= constants.GRID_HEIGHT:
            return False
        # 0=libre, 2=persona, 3=merch son caminables
        return self.grid[gy][gx] in (0, 2, 3)

    def get_neighbors(self, gx, gy):
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in dirs:
            nx, ny = gx + dx, gy + dy
            if 0 <= nx < constants.GRID_WIDTH and 0 <= ny < constants.GRID_HEIGHT and self.is_walkable(nx, ny):
                yield nx, ny

    def draw(self, screen):
        # dibujar background tiled
        for gy in range(constants.GRID_HEIGHT):
            for gx in range(constants.GRID_WIDTH):
                px, py = self.cell_to_pixel(gx, gy)
                screen.blit(self.grass_image, (px, py))

        # dibujar elementos
        for tree in self.trees:
            tree.draw(screen)

        for person in self.people:
            person.draw(screen)

        for m in self.merch:
            m.draw(screen)

    def draw_inventory(self, screen, character):
        font = pygame.font.SysFont(None, 24)
        y = 10
        x = 10
        inv = character.inventory
        
        # Dibuja cada ítem del inventario
        items = [
            f"Puntos: {inv['points']}",
            f"Rescatados: {inv['rescued']}",
            f"Ropa: {inv['clothes']}",
            f"Comida: {inv['food']}",
            f"Medicina: {inv['medicine']}"
        ]
        
        for text in items:
            surf = font.render(text, True, constants.WHITE)
            screen.blit(surf, (x, y))
            y += 25