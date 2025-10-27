# config/strategies/player1_strategies.py
from .base_strategy import BaseStrategy
import math

# -------------------------------
# Estrategia para JEEP
# -------------------------------
class JeepStrategy(BaseStrategy):
    def decide(self, vehicle, world):
        # Evasión de minas
        escape = self.evade_mines(vehicle, world)
        if escape:
            return {"type": "move", "target": escape}

        # Si ya tiene carga y puede seguir viajando
        if len(vehicle.cargo) > 0 and vehicle.trips_left > 0:
            resource = self.find_high_value_resource(vehicle, world, vehicle.allowed_cargo)
            if resource:
                return {"type": "move", "target": (resource.x, resource.y)}

        # Si ya completó viajes o está lleno, volver
        if vehicle.trips_left == 0 or len(vehicle.cargo) > 3:
            return {"type": "return_to_base", "target": vehicle.base_position}

        # Buscar recurso cercano de alto valor
        resource = self.find_high_value_resource(vehicle, world, vehicle.allowed_cargo)
        if resource:
            return {"type": "move", "target": (resource.x, resource.y)}

        # Si no hay recursos cercanos, explorar
        return {"type": "move", "target": self.random_exploration(world)}


# -------------------------------
# Estrategia para MOTO
# -------------------------------
class MotoStrategy(BaseStrategy):
    def decide(self, vehicle, world):
        escape = self.evade_mines(vehicle, world)
        if escape:
            return {"type": "move", "target": escape}

        if len(vehicle.cargo) > 0:
            return {"type": "return_to_base", "target": vehicle.base_position}

        # Buscar persona más cercana
        resource = self.find_nearest_resource(vehicle, world, ["person"])
        if resource:
            return {"type": "move", "target": (resource.x, resource.y)}

        # Exploración si no hay personas
        return {"type": "move", "target": self.random_exploration(world)}


# -------------------------------
# Estrategia para CAMIÓN
# -------------------------------
class CamionStrategy(BaseStrategy):
    def decide(self, vehicle, world):
        escape = self.evade_mines(vehicle, world)
        if escape:
            return {"type": "move", "target": escape}

        # Cargar hasta 3 viajes
        if len(vehicle.cargo) > 4 or vehicle.trips_left == 0:
            return {"type": "return_to_base", "target": vehicle.base_position}

        resource = self.find_high_value_resource(vehicle, world, vehicle.allowed_cargo)
        if resource:
            return {"type": "move", "target": (resource.x, resource.y)}

        return {"type": "move", "target": self.random_exploration(world)}


# -------------------------------
# Estrategia para AUTO
# -------------------------------
class AutoStrategy(BaseStrategy):
    def decide(self, vehicle, world):
        escape = self.evade_mines(vehicle, world)
        if escape:
            return {"type": "move", "target": escape}

        if len(vehicle.cargo) > 0:
            return {"type": "return_to_base", "target": vehicle.base_position}

        resource = self.find_high_value_resource(vehicle, world, ["person", "ropa", "alimentos", "medicamentos"])
        if resource:
            return {"type": "move", "target": (resource.x, resource.y)}

        return {"type": "move", "target": self.random_exploration(world)}
