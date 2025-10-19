from . import constants
import pygame
import os

class Character:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.inventory = {"points": 0, "clothes":0, "food":0, "medicine":0}
        image_path = os.path.join("assets","images","characters", "autoRojo.png")
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (constants.PLAYER, constants.PLAYER))
        self.size = self.image.get_width()

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
    def move(self, dx, dy, world):

        new_x = self.x + dx
        new_y = self.y + dy

        for tree in world.trees:
            if self.check_collision(new_x, new_y, tree):
                return  # Colisión con un árbol, no mover
            

        self.x = new_x
        self.y = new_y
        self.x = max(0, min(constants.WIDTH - self.size, self.x))
        self.y = max(0, min(constants.HEIGHT - self.size, self.y))

                # comprobar colisión con personas (rescatar)
        for person in world.people[:]:
            if self.check_collision(self.x, self.y, person):
                world.people.remove(person)
                self.inventory["points"] += constants.POINTS_PERSON

        # comprobar colisión con mercancías (recolectar)
        for m in world.merch[:]:
            if self.check_collision(self.x, self.y, m):
                world.merch.remove(m)
                self.inventory["points"] += m.points
                # contador por tipo
                if m.kind in self.inventory:
                    self.inventory[m.kind] += 1
                else:
                    self.inventory[m.kind] = 1
            

    def check_collision(self, x, y, obj):
        return (x < obj.x + obj.size and
                x + self.size > obj.x and
                y < obj.y + obj.size and
                y + self.size > obj.y)

    def is_near(self, obj):
        return (abs(self.x - obj.x) < self.size) and (abs(self.y - obj.y) < self.size)

    def interact(self, world):
        # interacción con personas
        for person in world.people:
            if self.is_near(person):
                world.people.remove(person)
                self.inventory["points"] += constants.POINTS_PERSON


