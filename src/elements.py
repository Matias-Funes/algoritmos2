from . import constants
import pygame
import os


class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.points = 5  # cantidad de madera que el árbol puede proporcionar
        tree_path = os.path.join("assets", "images", "objects", "Tree.png")
        try:
            self.image = pygame.image.load(tree_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (constants.TREE, constants.TREE))
        except Exception:
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
            self.image = pygame.image.load(person_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (constants.PERSON, constants.PERSON))
        except Exception:
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

