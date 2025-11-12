# config/strategies/base_strategy.py
import math
import random
from src import constants


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
        Retorna el recurso más cercano (en celdas) que el vehículo puede recoger.
        Usa distancia Manhattan (grid).
        """
        min_dist = float("inf")
        best_resource = None
        for res in world.resources:
            if res.type in allowed_types:
                # Convertir la posición de píxeles del recurso a celda
                res_gx, res_gy = world.pixel_to_cell(res.x, res.y)
                
                # Calcular distancia Manhattan (en celdas)
                dist = abs(vehicle.gx - res_gx) + abs(vehicle.gy - res_gy)
                
                if dist < min_dist:
                    min_dist = dist
                    best_resource = res
        return best_resource

    def find_high_value_resource(self, vehicle, world, allowed_types, min_value=10):
        """
        Retorna el recurso de mayor valor cercano, filtrando por tipo y valor.
        Usa una puntuación que combina valor y distancia (Manhattan).
        """
        best_resource = None
        best_score = -float("inf")
        for res in world.resources:
            if res.type in allowed_types and res.value >= min_value:
                value = res.value
                
                res_gx, res_gy = world.pixel_to_cell(res.x, res.y)
                dist = abs(vehicle.gx - res_gx) + abs(vehicle.gy - res_gy)
                
                # Puntuación: valor/(distancia_celdas+1)
                score = value / (1 + dist * 0.5) # Ajustamos el peso de la distancia
                
                if score > best_score:
                    best_score = score
                    best_resource = res
        return best_resource

    def nearest_mine_distance(self, vehicle, world):
        """
        Retorna la distancia (en celdas) a la mina activa más cercana.
        """
        min_dist = float("inf")
        for mine in world.mines:
            if not mine.active:
                continue
            
            mine_gx, mine_gy = world.pixel_to_cell(mine.x, mine.y)
            dist = abs(vehicle.gx - mine_gx) + abs(vehicle.gy - mine_gy)
            
            if dist < min_dist:
                min_dist = dist
        return min_dist

    def is_near_mine(self, vehicle, world, safety_margin=15):

        return False

    def evade_mines(self, vehicle, world):

        
        return None

    def find_nearest_mine(self, vehicle, world):
        """
        Retorna la mina activa más cercana.
        """
        min_dist = float("inf")
        best_mine = None
        for mine in world.mines:
            if mine.active:
                mine_gx, mine_gy = world.pixel_to_cell(mine.x, mine.y)
                dist = abs(vehicle.gx - mine_gx) + abs(vehicle.gy - mine_gy)
                if dist < min_dist:
                    min_dist = dist
                    best_mine = mine
        return best_mine

    def random_exploration(self, world):
        """
        Devuelve una coordenada de CELDA (gx, gy) aleatoria válida para exploración.
        """
        grid_height = len(world.grid)
        grid_width = len(world.grid[0])
        
        for _ in range(100): # Intentar 100 veces
            gx = random.randint(0, grid_width - 1)
            gy = random.randint(0, grid_height - 1)
            
            # Usamos el is_walkable del A* y comprobamos que no sea base
            if world.is_walkable(gx, gy) and not world.is_in_base_area(gx, gy):
                return (gx, gy)
                
        # Fallback: celda central
        return (grid_width // 2, grid_height // 2)

    def should_return_to_base(self, vehicle):
        """
        Determina si el vehículo debe regresar a la base.
        """
        # Si no tiene viajes disponibles
        if vehicle.trips_left <= 0:
            return True
        
        # Si tiene mucha carga (usa la configuración de constants.py)
        max_cargo = constants.VEHICLE_CARGO_LIMITS.get(vehicle.vehicle_type, 2)
        if len(vehicle.cargo) >= max_cargo:
            return True
        
        return False