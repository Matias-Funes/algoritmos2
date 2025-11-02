from . import constants
import pygame
import os
import math

class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.points = 5
        tree_path = os.path.join("assets", "images", "objects", "Tree.png")
        try:
            self.image = pygame.image.load(tree_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (constants.TREE, constants.TREE))
        except Exception:
            # Árbol mejorado
            self.image = pygame.Surface((constants.TREE, constants.TREE), pygame.SRCALPHA)
            # Copa del árbol
            pygame.draw.circle(self.image, (34, 139, 34), (constants.TREE//2, constants.TREE//2-2), 10)
            pygame.draw.circle(self.image, (50, 180, 50), (constants.TREE//2-3, constants.TREE//2-5), 7)
            pygame.draw.circle(self.image, (50, 180, 50), (constants.TREE//2+3, constants.TREE//2-5), 7)
            # Tronco
            pygame.draw.rect(self.image, (101, 67, 33), (constants.TREE//2-2, constants.TREE//2+5, 4, 8))
        self.size = self.image.get_width()

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class Person:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.points = 50
        self.type = "person"  # Para compatibilidad con estrategias
        self.value = 50
        person_path = os.path.join("assets", "images", "objects", "persona.png")
        try:
            self.image = pygame.image.load(person_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (constants.PERSON, constants.PERSON))
        except Exception:
            # Persona mejorada
            self.image = pygame.Surface((constants.PERSON, constants.PERSON), pygame.SRCALPHA)
            # Cabeza
            pygame.draw.circle(self.image, (255, 220, 180), (constants.PERSON//2, 8), 5)
            # Cuerpo
            pygame.draw.rect(self.image, (100, 100, 200), (constants.PERSON//2-3, 13, 6, 8))
            # Brazos
            pygame.draw.line(self.image, (255, 220, 180), (constants.PERSON//2, 15), (constants.PERSON//2-5, 18), 2)
            pygame.draw.line(self.image, (255, 220, 180), (constants.PERSON//2, 15), (constants.PERSON//2+5, 18), 2)
            # Piernas
            pygame.draw.line(self.image, (50, 50, 150), (constants.PERSON//2, 21), (constants.PERSON//2-3, 25), 2)
            pygame.draw.line(self.image, (50, 50, 150), (constants.PERSON//2, 21), (constants.PERSON//2+3, 25), 2)
        self.size = self.image.get_width()

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def get_state(self):
        """Devuelve un diccionario simple para guardar."""
        return {
            "type": self.type,
            "x": self.x,
            "y": self.y,
            "value": self.value
        }


class Merchandise:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.type = kind  # Para compatibilidad con estrategias
        self.value = constants.MERCH_POINTS.get(kind, 10)
        self.size = constants.MERCH_SIZE
        
        # Cargar o crear imagen según tipo
        filename = {
            "clothes": "remera.png",
            "food": "pizza.png",
            "medicine": "health.png",
            "weapons": "weapon.png"
        }.get(kind, "merch.png")
        path = os.path.join("assets", "images", "objects", filename)
        
        try:
            self.image = pygame.image.load(path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
        except Exception:
            # Crear sprites mejorados si no hay imagen
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            
            if kind == "clothes":
                # Camiseta
                pygame.draw.rect(self.image, (200, 100, 200), (4, 6, 12, 10))
                pygame.draw.rect(self.image, (200, 100, 200), (2, 6, 4, 4))  # Manga izq
                pygame.draw.rect(self.image, (200, 100, 200), (14, 6, 4, 4))  # Manga der
                pygame.draw.circle(self.image, (220, 120, 220), (10, 4), 2)  # Cuello
                
            elif kind == "food":
                # Pizza
                pygame.draw.circle(self.image, (255, 200, 100), (10, 10), 8)
                pygame.draw.circle(self.image, (255, 220, 120), (10, 10), 7)
                # Pepperoni
                pygame.draw.circle(self.image, (200, 50, 50), (7, 8), 2)
                pygame.draw.circle(self.image, (200, 50, 50), (13, 8), 2)
                pygame.draw.circle(self.image, (200, 50, 50), (10, 12), 2)
                
            elif kind == "medicine":
                # Cruz médica
                pygame.draw.rect(self.image, (255, 255, 255), (4, 4, 12, 12))
                pygame.draw.rect(self.image, (255, 50, 50), (8, 6, 4, 8))
                pygame.draw.rect(self.image, (255, 50, 50), (6, 8, 8, 4))
                
            elif kind == "weapons":
                # Arma/munición
                pygame.draw.rect(self.image, (80, 80, 80), (4, 8, 12, 4))
                pygame.draw.circle(self.image, (50, 50, 50), (4, 10), 2)
                pygame.draw.rect(self.image, (100, 100, 100), (6, 6, 6, 2))
                pygame.draw.polygon(self.image, (60, 60, 60), [(16, 10), (18, 8), (18, 12)])

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def get_state(self):
        """Devuelve un diccionario simple para guardar."""
        return {
            "type": self.type,
            "kind": self.kind,
            "x": self.x,
            "y": self.y,
            "value": self.value
        }

class Mine:
    def __init__(self, x, y, mine_type):
        self.x = x
        self.y = y
        self.type = mine_type
        self.active = True
        self.toggle_timer = 0
        self.size = 10
        self.radius = constants.MINE_TYPES[self.type]["radius"]
        
        # Cargar o crear imagen
        mine_path = os.path.join("assets", "images", "objects", f"mine_{mine_type}.png")
        try:
            self.image = pygame.image.load(mine_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
        except Exception:
            # Crear sprite de mina mejorado
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            
            if mine_type in ["O1", "O2"]:
                # Mina circular
                pygame.draw.circle(self.image, (200, 0, 0), (self.size//2, self.size//2), self.size//2)
                pygame.draw.circle(self.image, (150, 0, 0), (self.size//2, self.size//2), self.size//2-1, 1)
                pygame.draw.circle(self.image, (255, 200, 0), (self.size//2, self.size//2), 2)
                
            elif mine_type in ["T1", "T2"]:
                # Mina rectangular
                pygame.draw.rect(self.image, (200, 100, 0), (1, 1, self.size-2, self.size-2))
                pygame.draw.rect(self.image, (150, 50, 0), (1, 1, self.size-2, self.size-2), 1)
                pygame.draw.rect(self.image, (255, 200, 0), (3, 3, 4, 4))
                
            elif mine_type == "G1":
                # Mina móvil (destella)
                pygame.draw.circle(self.image, (255, 0, 255), (self.size//2, self.size//2), self.size//2)
                pygame.draw.circle(self.image, (200, 0, 200), (self.size//2, self.size//2), self.size//2-1, 1)
                pygame.draw.circle(self.image, (255, 255, 0), (self.size//2, self.size//2), 2)

    def update(self):
        """Actualiza el estado de la mina (solo G1)"""
        if self.type == "G1":
            self.toggle_timer += 1
            if self.toggle_timer >= constants.G1_TOGGLE_TIME:
                self.active = not self.active
                self.toggle_timer = 0

    def draw(self, screen):
        """Dibuja la mina y su área de efecto"""
        if not self.active:
            return
            
        # Dibujar la mina
        screen.blit(self.image, (self.x, self.y))
        
        # Debug: visualizar área de efecto
        if constants.DEBUG_MODE:
            radius = self.radius
            cx = self.x + self.size/2
            cy = self.y + self.size/2
            
            # Color semi-transparente según tipo
            color = constants.MINE_COLORS[self.type]
            
            if self.type in ["O1", "O2", "G1"]:
                # Área circular
                pygame.draw.circle(screen, color[:3], (int(cx), int(cy)), radius, 1)
                
            elif self.type == "T1":
                # Área horizontal
                pygame.draw.rect(screen, color[:3],
                               (cx - radius, cy - 2, radius * 2, 4), 1)
                
            elif self.type == "T2":
                # Área vertical
                pygame.draw.rect(screen, color[:3],
                               (cx - 2, cy - radius, 4, radius * 2), 1)

    def check_collision(self, px, py):
        """Verifica si un punto está dentro del área de la mina"""
        if not self.active:
            return False
            
        cx = self.x + self.size/2
        cy = self.y + self.size/2
        
        if self.type in ["O1", "O2", "G1"]:
            return math.hypot(px - cx, py - cy) <= self.radius
        elif self.type == "T1":
            return abs(py - cy) <= 2 and abs(px - cx) <= self.radius
        elif self.type == "T2":
            return abs(px - cx) <= 2 and abs(py - cy) <= self.radius
        
        return False
    
    def get_state(self):
        """Devuelve un diccionario simple para guardar."""
        return {
            "type": self.type,
            "x": self.x,
            "y": self.y,
            "active": self.active,
            "toggle_timer": self.toggle_timer,
            "radius": self.radius
        }