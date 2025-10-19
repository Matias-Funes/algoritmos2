from . import constants
from .pathfinding import a_star
import pygame
import os
import math

# personaje controlado por el jugador
class Character:
    def __init__(self, x, y):
        # alinear posición a la grid
        self.x = (x // constants.TILE) * constants.TILE
        self.y = (y // constants.TILE) * constants.TILE
        self.inventory = {"points": 0, "clothes": 0, "food": 0, "medicine": 0, "rescued": 0}

        image_path = os.path.join("assets", "images", "characters", "autoRojo.png")
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (constants.PLAYER, constants.PLAYER))
        except Exception:
            self.image = pygame.Surface((constants.PLAYER, constants.PLAYER), pygame.SRCALPHA)
            self.image.fill((200, 0, 0))
        self.size = self.image.get_width()
        self.path = []  # lista de celdas (gx,gy) para seguir
        self._move_speed = 4  # pixels por frame para interpolación

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move_to_cell(self, gx, gy, world):
        # calcula ruta A*
        start = world.pixel_to_cell(self.x, self.y)
        goal = (gx, gy)
        path = a_star(start, goal, world)
        if path:
            # almacenar path (excluyendo la celda actual)
            self.path = path[1:]

    def update(self, world):
        # Primero actualizar movimiento
        if self.path:
            next_cell = self.path[0]
            target_x, target_y = world.cell_to_pixel(*next_cell)
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)
            
            if dist <= self._move_speed:
                self.x, self.y = target_x, target_y
                self.path.pop(0)
            else:
                self.x += (dx / dist) * self._move_speed
                self.y += (dy / dist) * self._move_speed

        # Revisar colisiones/recolección
        current_cell = world.pixel_to_cell(self.x, self.y)
        
        # Revisar mercancías
        for merch in world.merch[:]:
            merch_cell = world.pixel_to_cell(merch.x, merch.y)
            if current_cell == merch_cell:
                # Añadir al inventario
                self.inventory[merch.kind] += 1
                # Sumar puntos según tipo
                self.inventory["points"] += constants.MERCH_POINTS[merch.kind]
                # Remover mercancía
                world.merch.remove(merch)
                # Actualizar grid
                world.grid[merch_cell[1]][merch_cell[0]] = 0
        
        # Revisar personas
        for person in world.people[:]:
            person_cell = world.pixel_to_cell(person.x, person.y)
            if current_cell == person_cell:
                # Verificar si tenemos recursos suficientes
                if (self.inventory["clothes"] >= 1 and 
                    self.inventory["food"] >= 1 and 
                    self.inventory["medicine"] >= 1):
                    # Consumir recursos
                    self.inventory["clothes"] -= 1
                    self.inventory["food"] -= 1
                    self.inventory["medicine"] -= 1
                    # Sumar puntos y contador de rescatados
                    self.inventory["points"] += constants.POINTS_PERSON
                    self.inventory["rescued"] += 1
                    # Remover persona y actualizar grid
                    world.people.remove(person)
                    world.grid[person_cell[1]][person_cell[0]] = 0
                    print(f"¡Persona rescatada! Puntos: {self.inventory['points']}")  # Debug




