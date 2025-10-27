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

    def find_high_value_resource(self, vehicle, world, allowed_types, min_value=10):
        """
        Retorna el recurso de mayor valor cercano, filtrando por tipo y valor.
        Usa una puntuación que combina valor y distancia.
        """
        best_resource = None
        best_score = -float("inf")
        for res in world.resources:
            if res.type in allowed_types and res.value >= min_value:
                value = res.value
                dist = math.hypot(vehicle.x - res.x, vehicle.y - res.y)
                # Puntuación: valor/(distancia+1) - mayor es mejor
                score = value / (1 + dist * 0.1)
                if score > best_score:
                    best_score = score
                    best_resource = res
        return best_resource

    def nearest_mine_distance(self, vehicle, world):
        """
        Retorna la distancia a la mina activa más cercana.
        """
        min_dist = float("inf")
        for mine in world.mines:
            if not mine.active:
                continue
            mine_center_x = mine.x + mine.size / 2
            mine_center_y = mine.y + mine.size / 2
            dist = math.hypot(vehicle.x - mine_center_x, vehicle.y - mine_center_y)
            if dist < min_dist:
                min_dist = dist
        return min_dist

    def is_near_mine(self, vehicle, world, safety_margin=15):
        """
        Verifica si el vehículo está peligrosamente cerca de alguna mina.
        """
        for mine in world.mines:
            if not mine.active:
                continue
            mine_center_x = mine.x + mine.size / 2
            mine_center_y = mine.y + mine.size / 2
            dist = math.hypot(vehicle.x - mine_center_x, vehicle.y - mine_center_y)
            if dist < mine.radius + safety_margin:
                return True
        return False

    def evade_mines(self, vehicle, world):
        """
        Calcula una dirección para alejarse de la mina más cercana.
        Retorna coordenadas de escape o None si está seguro.
        """
        if not world.mines:
            return None

        # Encontrar la mina activa más cercana
        nearest_mine = None
        min_dist = float("inf")
        
        for mine in world.mines:
            if not mine.active:
                continue
            mine_center_x = mine.x + mine.size / 2
            mine_center_y = mine.y + mine.size / 2
            dist = math.hypot(vehicle.x - mine_center_x, vehicle.y - mine_center_y)
            
            if dist < min_dist:
                min_dist = dist
                nearest_mine = mine

        if not nearest_mine:
            return None

        # Si está muy cerca, escapar
        mine_center_x = nearest_mine.x + nearest_mine.size / 2
        mine_center_y = nearest_mine.y + nearest_mine.size / 2
        danger_threshold = nearest_mine.radius + 20  # margen de seguridad

        if min_dist < danger_threshold:
            # Vector de escape: alejarse de la mina
            dx = vehicle.x - mine_center_x
            dy = vehicle.y - mine_center_y
            dist = math.hypot(dx, dy)
            
            if dist < 1:  # evitar división por cero
                dx, dy = random.uniform(-1, 1), random.uniform(-1, 1)
                dist = math.hypot(dx, dy)
            
            # Punto de escape a 40 unidades de distancia
            escape_x = vehicle.x + (dx / dist) * 40
            escape_y = vehicle.y + (dy / dist) * 40
            
            # Mantener dentro de los límites
            escape_x = max(30, min(escape_x, world.width - 30))
            escape_y = max(30, min(escape_y, world.height - 30))
            
            return (escape_x, escape_y)
        
        return None

    def random_exploration(self, world):
        """
        Devuelve una coordenada aleatoria válida para exploración.
        """
        return world.random_position()

    def should_return_to_base(self, vehicle):
        """
        Determina si el vehículo debe regresar a la base.
        """
        # Si no tiene viajes disponibles
        if vehicle.trips_left <= 0:
            return True
        
        # Si tiene mucha carga
        cargo_limit = {
            "jeep": 3,
            "moto": 1,
            "camion": 5,
            "auto": 2
        }
        
        max_cargo = cargo_limit.get(vehicle.vehicle_type, 2)
        if len(vehicle.cargo) >= max_cargo:
            return True
        
        return False