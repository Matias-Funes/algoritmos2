from . import constants
import pygame
import os
import math

#estructuras del mundo del juego: árboles, personas, mercancías
class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.points = 5  # cantidad de madera que el árbol puede proporcionar
        tree_path = os.path.join("assets", "images", "objects", "Tree.png")
        try:
            # cargar imagen del árbol
            self.image = pygame.image.load(tree_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (constants.TREE, constants.TREE))
        except Exception:
            # imagen de respaldo si falla la carga
            self.image = pygame.Surface((constants.TREE, constants.TREE), pygame.SRCALPHA)
            self.image.fill((34, 139, 34))
        self.size = self.image.get_width()

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class Person:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.points = 50
        person_path = os.path.join("assets", "images", "objects", "persona.png")
        try:
            # cargar imagen de la persona
            self.image = pygame.image.load(person_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (constants.PERSON, constants.PERSON))
        except Exception:
            # imagen de respaldo si falla la carga
            self.image = pygame.Surface((constants.PERSON, constants.PERSON), pygame.SRCALPHA)
            self.image.fill((255, 220, 180))
        self.size = self.image.get_width()

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


# Merchandise (única definición)
class Merchandise:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.size = constants.MERCH_SIZE
        # elegir imagen según tipo
        filename = {
            "clothes": "remera.png",
            "food": "pizza.png",
            "medicine": "health.png"
        }.get(kind, "merch.png")
        path = os.path.join("assets", "images", "objects", filename)
        try:
            self.image = pygame.image.load(path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
        except Exception:
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            # color según tipo
            colors = {"clothes": (200, 100, 200), "food": (200, 150, 50), "medicine": (150, 200, 150)}
            self.image.fill(colors.get(kind, (180, 180, 180)))

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Mine:
    def __init__(self, x, y, mine_type):
        self.x = x
        self.y = y
        self.type = mine_type
        self.active = True  # Para minas G1
        self.toggle_timer = 0  # Para minas G1
        self.size = 10  # Tamaño visual de la mina
        
        # NUEVO: guardar el radio directamente en la instancia
        self.radius = constants.MINE_TYPES[self.type]["radius"]
        
        # Cargar imagen según tipo
        mine_path = os.path.join("assets", "images", "objects", f"mine_{mine_type}.png")
        try:
            self.image = pygame.image.load(mine_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
        except Exception:
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            self.image.fill(constants.MINE_COLORS[mine_type])

    def update(self):
        # Solo para minas G1
        if self.type == "G1":
            self.toggle_timer += 1
            if self.toggle_timer >= constants.G1_TOGGLE_TIME:
                self.active = not self.active
                self.toggle_timer = 0

    def draw(self, screen):
        if not self.active:
            return
            
        # Dibujar la mina
        screen.blit(self.image, (self.x, self.y))
        
        # Debug: visualizar área de efecto
        if constants.DEBUG_MODE:
            radius = constants.MINE_TYPES[self.type]["radius"]
            cx = self.x + self.size/2
            cy = self.y + self.size/2
            if self.type in ["O1", "O2", "G1"]:
                pygame.draw.circle(screen, constants.MINE_COLORS[self.type], (int(cx), int(cy)), radius, 1)
            elif self.type == "T1":
                pygame.draw.rect(screen, constants.MINE_COLORS[self.type],
                             (cx - radius, cy - 2, radius * 2, 4), 1)
            elif self.type == "T2":
                pygame.draw.rect(screen, constants.MINE_COLORS[self.type],
                                 (cx - 2, cy - radius, 4, radius * 2), 1)


    def check_collision(self, px, py):
        if not self.active:
            return False
            
        radius = constants.MINE_TYPES[self.type]["radius"]
        cx = self.x + self.size/2
        cy = self.y + self.size/2
        if self.type in ["O1", "O2", "G1"]:
            return math.hypot(px - cx, py - cy) <= radius
        elif self.type == "T1":
            return abs(py - self.y) <= 2 and abs(px - self.x) <= radius
        elif self.type == "T2":
            return abs(px - self.x) <= 2 and abs(py - self.y) <= radius
        return False
