# config/strategies/player2_strategies.py
from .base_strategy import BaseStrategy
import math
import random

# -------------------------------
# Estrategia para JEEP (agresiva)
# -------------------------------
class AggressiveJeepStrategy(BaseStrategy):
    def decide(self, vehicle, world):
        # Buscar enemigo cercano
        enemy = world.find_nearest_enemy(vehicle)
        if enemy and vehicle.distance_to(enemy) < 40:
            return {"type": "move", "target": (enemy.x, enemy.y)}

        # Si lleva carga suficiente → volver
        if len(vehicle.cargo) >= 3:
            return {"type": "return_to_base", "target": vehicle.base_position}

        # Buscar recurso valioso incluso si está cerca de una mina
        resource = self.find_high_value_resource(vehicle, world, vehicle.allowed_cargo)
        if resource:
            dist_mine = self.nearest_mine_distance(vehicle, world)
            if dist_mine > 10 or resource.value >= 20:
                return {"type": "move", "target": (resource.x, resource.y)}

        return {"type": "move", "target": self.random_exploration(world)}


# -------------------------------
# Estrategia para MOTO (rápida)
# -------------------------------
class FastMotoStrategy(BaseStrategy):
    def decide(self, vehicle, world):
        if len(vehicle.cargo) > 0:
            return {"type": "return_to_base", "target": vehicle.base_position}

        # Buscar persona más cercana
        resource = self.find_nearest_resource(vehicle, world, ["person"])
        if resource:
            return {"type": "move", "target": (resource.x, resource.y)}

        # Exploración rápida
        return {"type": "move", "target": self.random_exploration(world)}


# -------------------------------
# Estrategia para CAMIÓN (de apoyo)
# -------------------------------
class SupportCamionStrategy(BaseStrategy):
    def decide(self, vehicle, world):
        if len(vehicle.cargo) > 5 or vehicle.trips_left == 0:
            return {"type": "return_to_base", "target": vehicle.base_position}

        # Prioriza recursos de alto valor
        resource = self.find_high_value_resource(vehicle, world, vehicle.allowed_cargo, min_value=10)
        if resource:
            return {"type": "move", "target": (resource.x, resource.y)}

        return {"type": "move", "target": self.random_exploration(world)}


# -------------------------------
# Estrategia para AUTO (equilibrada)
# -------------------------------
class BalancedAutoStrategy(BaseStrategy):
    def decide(self, vehicle, world):
        # Si tiene carga → volver
        if len(vehicle.cargo) > 0:
            return {"type": "return_to_base", "target": vehicle.base_position}

        # Si hay enemigo cerca, esquivar
        enemy = world.find_nearest_enemy(vehicle)
        if enemy and vehicle.distance_to(enemy) < 25:
            # Moverse en dirección opuesta
            dx = vehicle.x - enemy.x
            dy = vehicle.y - enemy.y
            dist = math.hypot(dx, dy)
            return {"type": "move", "target": (vehicle.x + dx / dist * 15, vehicle.y + dy / dist * 15)}

        # Buscar recurso balanceado (persona o medicamento)
        resource = self.find_high_value_resource(vehicle, world, ["person", "medicamentos"])
        if resource:
            return {"type": "move", "target": (resource.x, resource.y)}

        # Exploración
        return {"type": "move", "target": self.random_exploration(world)}
