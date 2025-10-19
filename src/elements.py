from . import constants
import pygame
import os


class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.points= 5  # cantidad de madera que el árbol puede proporcionar
        tree_path = os.path.join("assets","images","objects", "Tree.png")
        self.image = pygame.image.load(tree_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (constants.TREE, constants.TREE))
        self.size = self.image.get_width()


    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class Person:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.points = 50
        person_path = os.path.join("assets","images","objects", "persona.png")
        self.image = pygame.image.load(person_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (constants.PERSON, constants.PERSON))
        self.size = self.image.get_width()


    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


# Merchandise (única definición)
class Merchandise:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind  # 'clothes' | 'food' | 'medicine'
        # puntos según tipo y nombre de archivo (fallback a rect)
        if kind == "clothes":
            self.points = constants.POINTS_CLOTH
            filename = "remera.png"
        elif kind == "food":
            self.points = constants.POINTS_FOOD
            filename = "pizza.png"
        else:
            self.points = constants.POINTS_MED
            filename = "health.png"

        img_path = os.path.join("assets","images","objects", filename)
        try:
            self.image = pygame.image.load(img_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (constants.MERCH_SIZE, constants.MERCH_SIZE))
        except Exception:
            # fallback si no existe la imagen
            self.image = None
        self.size = constants.MERCH_SIZE

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            # rectángulo de color según tipo
            color = (200,200,200)
            if self.kind == "food":
                color = (255,180,0)
            elif self.kind == "medicine":
                color = (200,0,0)
            pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size))

