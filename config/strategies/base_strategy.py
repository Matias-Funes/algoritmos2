# config/strategies/base_strategy.py
import math
import random

class BaseStrategy:
    """
    Clase base para todas las estrategias de vehículos.
    Define métodos comunes de búsqueda y evasión.
    """

    def decide(self, vehicle, world):
        """
        Debe ser implementado por cada subclase.
        Retorna una acción: {"type": str, "target": (x, y) o recurso}
        """
        raise NotImplementedError("Implementar en subclases")

    # -------------------------------
    # Métodos de apoyo
    # -------------------------------

    def find_nearest_resource(self, vehicle, world, allowed_types):
        """
        Retorna el recurso más cercano que el vehículo puede recoger.
        """
        min_dist = float("inf")
        best_resource = None
        for res in world.resources:
            if res.type in allowed_types:
                dist = math.hypot(vehicle.x - res.x, vehicle.y - res.y)
                if dist < min_dist:
                    min_dist = dist
                    best_resource = res
        return best_resource

    def find_high_value_resource(self, vehicle, world, allowed_types, min_value=20):
        """
        Retorna el recurso de mayor valor cercano, filtrando por tipo y valor.
        """
        best_resource = None
        best_score = -float("inf")
        for res in world.resources:
            if res.type in allowed_types:
                value = res.value
                dist = math.hypot(vehicle.x - res.x, vehicle.y - res.y)
                # puntuación combinada: valor/riesgo (menor distancia = mejor)
                score = value / (1 + dist)
                if score > best_score:
                    best_score = score
                    best_resource = res
        return best_resource

    def nearest_mine_distance(self, vehicle, world):
        """
        Retorna la distancia a la mina más cercana.
        """
        min_dist = float("inf")
        for mine in world.mines:
            dist = math.hypot(vehicle.x - mine.x, vehicle.y - mine.y)
            if dist < min_dist:
                min_dist = dist
        return min_dist

    def evade_mines(self, vehicle, world):
        """
        Calcula una dirección aleatoria para alejarse de la mina más cercana.
        """
        if not world.mines:
            return None

        nearest = min(world.mines, key=lambda m: math.hypot(vehicle.x - m.x, vehicle.y - m.y))
        dx = vehicle.x - nearest.x
        dy = vehicle.y - nearest.y
        dist = math.hypot(dx, dy)

        if dist < nearest.radius + 5:  # margen de seguridad
            # Alejarse de la mina
            escape_x = vehicle.x + (dx / (dist + 1e-5)) * 20
            escape_y = vehicle.y + (dy / (dist + 1e-5)) * 20
            return (escape_x, escape_y)
        return None

    def random_exploration(self, world):
        """
        Devuelve una coordenada aleatoria válida para exploración.
        """
        return world.random_position()
