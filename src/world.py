from . import constants
import pygame
from .elements import Tree, Person, Merchandise
import random 
import os


class World:
    def __init__(self,width, height):
        self.width = width
        self.height = height
        self.trees = [Tree(random.randint(0, width-constants.TREE), random.randint(0, height-constants.TREE)) for _ in range(10)]
        self.people = [Person(random.randint(0, width-constants.PERSON), random.randint(0, height-constants.PERSON)) for _ in range(10)]
        self.merch = []
        for kind, cnt in constants.MERCH_COUNTS.items():
            for _ in range(cnt):
                x = random.randint(0, width - constants.MERCH_SIZE)
                y = random.randint(0, height - constants.MERCH_SIZE)
                self.merch.append(Merchandise(x, y, kind))

        grass_path = os.path.join("assets","images","objects", "Grass.png")
        self.grass_image = pygame.image.load(grass_path).convert()
        self.grass_image = pygame.transform.scale(self.grass_image, (constants.GRASS, constants.GRASS))
        
    
    


    def draw(self, screen):
        for y in range(0, self.height, constants.GRASS):
            for x in range(0, self.width, constants.GRASS):
                screen.blit(self.grass_image, (x, y))

        for tree in self.trees:
            tree.draw(screen)

        for person in self.people:
            person.draw(screen)
        
        for m in self.merch:
            m.draw(screen)
        
    def draw_inventory(self, screen, character):
        font = pygame.font.SysFont(None,36)
        points_text = font.render(f"Points: {character.inventory['points']}", True, constants.WHITE)
        screen.blit(points_text, (10,10))