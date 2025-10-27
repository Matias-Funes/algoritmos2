# src/aircraft.py
import math

class Vehicle:
    def __init__(self, id, x, y, base_position, vehicle_type, max_trips, allowed_cargo, color):
        self.id = id
        self.x = x
        self.y = y
        self.vehicle_type = vehicle_type
        self.base_position = base_position
        self.trips_left = max_trips
        self.allowed_cargo = allowed_cargo  # e.g. ["person", "ropa", "alimentos", ...]
        self.cargo = []
        self.color = color
        self.alive = True
        self.target = None
        self.strategy = None  # se asigna desde player1_strategies o player2_strategies
        self.speed = 2  # velocidad base (puede variar)
        self.score = 0

    def distance_to(self, obj):
        return math.hypot(self.x - obj.x, self.y - obj.y)

    def move_towards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.x += self.speed * (dx / dist)
            self.y += self.speed * (dy / dist)

    def update(self, world):
        if not self.alive:
            return
        
        if self.strategy:
            action = self.strategy.decide(self, world)
            self.execute_action(action, world)

    def execute_action(self, action, world):
        if action["type"] == "move":
            tx, ty = action["target"]
            self.move_towards(tx, ty)
        elif action["type"] == "collect":
            resource = action["target"]
            self.collect(resource, world)
        elif action["type"] == "return_to_base":
            bx, by = self.base_position
            self.move_towards(bx, by)

    def collect(self, resource, world):
        if resource.type in self.allowed_cargo:
            self.cargo.append(resource)
            self.score += resource.value
            world.remove_resource(resource)
            # Si el vehículo debe volver al recoger algo
            if self.vehicle_type in ["moto", "auto"]:
                self.trips_left -= 1
                self.target = self.base_position

    def die(self):
        self.alive = False
        self.cargo.clear()

class Jeep(Vehicle):
    def __init__(self, id, x, y, base_position, color):
        super().__init__(id, x, y, base_position, "jeep", 2,
                         ["person", "ropa", "alimentos", "medicamentos", "armamentos"], color)
        self.speed = 2.5


class Moto(Vehicle):
    def __init__(self, id, x, y, base_position, color):
        super().__init__(id, x, y, base_position, "moto", 1, ["person"], color)
        self.speed = 3.5


class Camion(Vehicle):
    def __init__(self, id, x, y, base_position, color):
        super().__init__(id, x, y, base_position, "camion", 3,
                         ["person", "ropa", "alimentos", "medicamentos", "armamentos"], color)
        self.speed = 1.8


class Auto(Vehicle):
    def __init__(self, id, x, y, base_position, color):
        super().__init__(id, x, y, base_position, "auto", 1,
                         ["person", "ropa", "alimentos", "medicamentos"], color)
        self.speed = 2.2

