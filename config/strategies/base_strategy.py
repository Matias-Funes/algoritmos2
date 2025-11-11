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
        Calcula una celda (gx, gy) para alejarse de la mina más cercana.
        Retorna una tupla (gx, gy) o None si está seguro.
        """
        if not world.mines:
            return None

        # Encontrar la mina activa más cercana (en píxeles, para el radio)
        nearest_mine = None
        min_dist_pixels = float("inf")
        
        # Usamos la posición visual (x, y) del vehículo SÓLO para esta
        # comprobación de seguridad de "píxel" en tiempo real.
        for mine in world.mines:
            if not mine.active:
                continue
            
            # Usamos el centro de la mina en píxeles
            mine_center_x = mine.x + constants.TILE // 2 
            mine_center_y = mine.y + constants.TILE // 2
            dist_px = math.hypot(vehicle.x - mine_center_x, vehicle.y - mine_center_y)
            
            if dist_px < min_dist_pixels:
                min_dist_pixels = dist_px
                nearest_mine = mine

        if not nearest_mine:
            return None

        # Si está muy cerca (en píxeles), escapar
        danger_threshold = nearest_mine.radius + 20 # margen de seguridad
        mine_center_x = nearest_mine.x + constants.TILE // 2
        mine_center_y = nearest_mine.y + constants.TILE // 2

        if min_dist_pixels < danger_threshold:
            # Vector de escape (en píxeles)
            dx = vehicle.x - mine_center_x
            dy = vehicle.y - mine_center_y
            dist_px = math.hypot(dx, dy)
            
            if dist_px < 1: 
                dx, dy = random.uniform(-1, 1), random.uniform(-1, 1)
                dist_px = math.hypot(dx, dy)
            
            # Punto de escape en píxeles (a 4 celdas de distancia)
            escape_dist = constants.TILE * 4
            escape_x = vehicle.x + (dx / dist_px) * escape_dist
            escape_y = vehicle.y + (dy / dist_px) * escape_dist
            
            # Convertir el punto de escape de píxeles a CELDA
            escape_gx, escape_gy = world.pixel_to_cell(escape_x, escape_y)
            
            # Asegurar que la celda esté dentro de los límites
            grid_h = len(world.grid)
            grid_w = len(world.grid[0])
            escape_gx = max(0, min(escape_gx, grid_w - 1))
            escape_gy = max(0, min(escape_gy, grid_h - 1))
            
            return (escape_gx, escape_gy) # Devolvemos una celda (gx, gy)
        
        return None

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