import pygame
from . import constants

class Vehicle:
    """Clase base para todos los vehículos del simulador."""
    def __init__(self, x, y, image_name, allowed_cargo, max_trips):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.image_name = image_name
        self.allowed_cargo = allowed_cargo  # ["person", "clothes", "food", "medicine", "weapons"]
        self.max_trips = max_trips
        self.trips_done = 0

        # Estado
        self.cargo = []              # lista de ítems recogidos
        self.destroyed = False
        self.active = True
        self.returning = False       # si está volviendo a base
        self.in_base = True          # empieza en base
        self.points = 0

        # Cargar imagen
        try:
            self.image = pygame.image.load(f"assets/images/characters/{image_name}").convert_alpha()
            self.image = pygame.transform.scale(self.image, (constants.TILE, constants.TILE))
        except Exception:
            self.image = pygame.Surface((constants.TILE, constants.TILE))
            self.image.fill((100, 100, 255))  # color de fallback

    def draw(self, screen):
        if not self.destroyed:
            screen.blit(self.image, (self.x, self.y))
            
class Jeep(Vehicle):
    def __init__(self, x, y):
        super().__init__(x, y, "jeep.png",
                         allowed_cargo=["person", "clothes", "food", "medicine", "weapons"],
                         max_trips=2)

class Moto(Vehicle):
    def __init__(self, x, y):
        super().__init__(x, y, "moto.png",
                         allowed_cargo=["person"],
                         max_trips=1)

class Camion(Vehicle):
    def __init__(self, x, y):
        super().__init__(x, y, "camion.png",
                         allowed_cargo=["person", "clothes", "food", "medicine", "weapons"],
                         max_trips=3)
class Auto(Vehicle):
    def __init__(self, x, y):
        super().__init__(x, y, "auto.png",
                         allowed_cargo=["person", "clothes", "food", "medicine"],
                         max_trips=1)

