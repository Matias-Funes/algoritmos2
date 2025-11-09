# config/strategies/player2_strategies.py
from .base_strategy import BaseStrategy
import math
import random
from src import constants


# -------------------------------
# Estrategia para JEEP - Agresiva (ataca enemigos)
# -------------------------------
class AggressiveJeepStrategy(BaseStrategy):
    def decide(self, vehicle, world):
        # PRIORIDAD 1: Evasión de minas (Ya usa celdas)
        escape = self.evade_mines(vehicle, world)
        if escape:
            return {"type": "move", "target": escape}

        # PRIORIDAD 2: Buscar y atacar enemigos cercanos
        enemy = world.find_nearest_enemy(vehicle)
        if enemy and enemy.alive:
            # Usamos la distancia en celdas (Manhattan)
            dist_to_enemy = vehicle.distance_to(enemy) 
            
            # Si está a 15 celdas o menos, interceptar
            if dist_to_enemy < 15:
                # Devolvemos la CELDA (gx, gy) del enemigo
                return {"type": "move", "target": (enemy.gx, enemy.gy)}

        # PRIORIDAD 3: Regresar si tiene suficiente carga
        if len(vehicle.cargo) >= 3 or vehicle.trips_left == 0:
            return {"type": "return_to_base"} # No necesita target

        # PRIORIDAD 4: Buscar recursos valiosos (Ya usa celdas)
        resource = self.find_high_value_resource(
            vehicle, world,
            vehicle.allowed_cargo,
            min_value=20
        )
        
        if resource:
            return {"type": "collect", "target": resource}

        # PRIORIDAD 5: Buscar cualquier recurso (Ya usa celdas)
        resource = self.find_nearest_resource(vehicle, world, vehicle.allowed_cargo)
        if resource:
            return {"type": "collect", "target": resource}

        # PRIORIDAD 6: Exploración (Ya usa celdas)
        return {"type": "move", "target": self.random_exploration(world)}


# -------------------------------
# Estrategia para MOTO - Rápida y cautelosa
# -------------------------------
class FastMotoStrategy(BaseStrategy):
    def decide(self, vehicle, world):
        # PRIORIDAD 1: Evasión de minas (Ya usa celdas)
        escape = self.evade_mines(vehicle, world)
        if escape:
            return {"type": "move", "target": escape}

        # PRIORIDAD 2: Si tiene carga, regresar rápido
        if len(vehicle.cargo) > 0:
            return {"type": "return_to_base"} # No necesita target

        # PRIORIDAD 3: Evitar enemigos cercanos
        enemy = world.find_nearest_enemy(vehicle)
        if enemy and enemy.alive:
            dist_to_enemy = vehicle.distance_to(enemy) # Distancia en celdas

            if dist_to_enemy < 8: # 8 celdas de distancia
                # Escapar del enemigo (convertido a celdas)
                dx = vehicle.x - enemy.x # Usamos píxeles solo para el vector
                dy = vehicle.y - enemy.y
                dist_px = math.hypot(dx, dy)
                if dist_px > 0:
                    # CORRECCIÓN: Usamos constants.TILE
                    escape_dist = 5 * constants.TILE # Escapar 5 celdas 
                    escape_x = vehicle.x + (dx / dist_px) * escape_dist
                    escape_y = vehicle.y + (dy / dist_px) * escape_dist

                    # Convertir a celda y devolver
                    escape_gx, escape_gy = world.pixel_to_cell(escape_x, escape_y)
                    # CORRECCIÓN: Usamos constants.GRID_WIDTH y HEIGHT
                    escape_gx = max(0, min(escape_gx, constants.GRID_WIDTH - 1)) 
                    escape_gy = max(0, min(escape_gy, constants.GRID_HEIGHT - 1))
                    return {"type": "move", "target": (escape_gx, escape_gy)}

        # PRIORIDAD 4: Buscar persona más cercana en zona segura (lógica de celdas)
        safe_people = []
        for res in world.resources:
            if res.type == "person":
                safe = True
                res_gx, res_gy = world.pixel_to_cell(res.x, res.y)
                for mine in world.mines:
                    if mine.active:
                        mine_gx, mine_gy = world.pixel_to_cell(mine.x, mine.y)
                        dist_m = abs(res_gx - mine_gx) + abs(res_gy - mine_gy)
                        # Si está a 2 celdas o menos de una mina, no es seguro
                        if dist_m <= 2: 
                            safe = False
                            break
                if safe:
                    safe_people.append(res)
        
        if safe_people:
            # Encontrar más cercano usando distancia de celdas
            nearest = min(safe_people, key=lambda r: 
                          abs(vehicle.gx - world.pixel_to_cell(r.x, r.y)[0]) + 
                          abs(vehicle.gy - world.pixel_to_cell(r.x, r.y)[1]))
            return {"type": "collect", "target": nearest}

        # PRIORIDAD 5: Exploración rápida (Ya usa celdas)
        return {"type": "move", "target": self.random_exploration(world)}
    
# -------------------------------
# Estrategia para CAMIÓN - Apoyo (recolección masiva)
# -------------------------------
class SupportCamionStrategy(BaseStrategy):
    def decide(self, vehicle, world):
        # PRIORIDAD 1: Evasión de minas (Ya usa celdas)
        escape = self.evade_mines(vehicle, world)
        if escape:
            return {"type": "move", "target": escape}

        # PRIORIDAD 2: Regresar cuando esté lleno
        if len(vehicle.cargo) >= 6 or vehicle.trips_left == 0:
            return {"type": "return_to_base"} # No necesita target

        # PRIORIDAD 3: Priorizar recursos de valor medio-alto
        resource = self.find_high_value_resource(
            vehicle, world,
            vehicle.allowed_cargo,
            min_value=10
        )
        
        if resource:
            # nearest_mine_distance ya usa celdas (lo corregimos en base_strategy)
            dist_to_mine = self.nearest_mine_distance(vehicle, world)
            # 20 celdas es muy seguro, lo bajamos a 4
            if dist_to_mine > 4: 
                return {"type": "collect", "target": resource}

        # PRIORIDAD 4: Recolectar recursos seguros (lógica de celdas)
        safe_resources = []
        for res in world.resources:
            if res.type in vehicle.allowed_cargo:
                dist_to_mine = float("inf")
                res_gx, res_gy = world.pixel_to_cell(res.x, res.y)
                for mine in world.mines:
                    if mine.active:
                        mine_gx, mine_gy = world.pixel_to_cell(mine.x, mine.y)
                        d = abs(res_gx - mine_gx) + abs(res_gy - mine_gy)
                        dist_to_mine = min(dist_to_mine, d)
                
                # Si está a más de 2 celdas de cualquier mina
                if dist_to_mine > 2: 
                    safe_resources.append(res)
        
        if safe_resources:
            # Encontrar más cercano usando distancia de celdas
            nearest = min(safe_resources, key=lambda r: 
                          abs(vehicle.gx - world.pixel_to_cell(r.x, r.y)[0]) + 
                          abs(vehicle.gy - world.pixel_to_cell(r.x, r.y)[1]))
            return {"type": "collect", "target": nearest}

        # PRIORIDAD 5: Exploración (Ya usa celdas)
        return {"type": "move", "target": self.random_exploration(world)}
    
# -------------------------------
# Estrategia para AUTO - Equilibrada y defensiva
# -------------------------------
class BalancedAutoStrategy(BaseStrategy):
    def decide(self, vehicle, world):
        # PRIORIDAD 1: Evasión de minas
        escape = self.evade_mines(vehicle, world)
        if escape:
            return {"type": "move", "target": escape}

        # PRIORIDAD 2: Si tiene carga, regresar
        if len(vehicle.cargo) > 0:
            return {"type": "return_to_base"}

        # PRIORIDAD 3: Evitar enemigos cercanos
        enemy = world.find_nearest_enemy(vehicle)
        if enemy and enemy.alive:
            dist_to_enemy = vehicle.distance_to(enemy)

            if dist_to_enemy < 6: 
                dx = vehicle.x - enemy.x
                dy = vehicle.y - enemy.y
                dist_px = math.hypot(dx, dy)
                if dist_px > 0:
                    # CORRECCIÓN: Usamos constants.TILE
                    escape_dist = 4 * constants.TILE 
                    escape_x = vehicle.x + (dx / dist_px) * escape_dist
                    escape_y = vehicle.y + (dy / dist_px) * escape_dist

                    escape_gx, escape_gy = world.pixel_to_cell(escape_x, escape_y)
                    # CORRECCIÓN: Usamos constants.GRID_WIDTH y HEIGHT
                    escape_gx = max(0, min(escape_gx, constants.GRID_WIDTH - 1))
                    escape_gy = max(0, min(escape_gy, constants.GRID_HEIGHT - 1))
                    return {"type": "move", "target": (escape_gx, escape_gy)}

        # PRIORIDAD 4: Buscar personas (lógica de celdas)
        person = self.find_nearest_resource(vehicle, world, ["person"])
        if person:
            person_gx, person_gy = world.pixel_to_cell(person.x, person.y)
            dist_to_person = abs(vehicle.gx - person_gx) + abs(vehicle.gy - person_gy)
            if dist_to_person < 5: # 5 celdas
                return {"type": "collect", "target": person}

        # PRIORIDAD 5: Buscar medicamentos (lógica de celdas)
        medicine = self.find_nearest_resource(vehicle, world, ["medicine"])
        if medicine:
            med_gx, med_gy = world.pixel_to_cell(medicine.x, medicine.y)
            dist_to_med = abs(vehicle.gx - med_gx) + abs(vehicle.gy - med_gy)
            if dist_to_med < 4: # 4 celdas
                return {"type": "collect", "target": medicine}

        # PRIORIDAD 6: Buscar cualquier recurso (Ya usa celdas)
        resource = self.find_nearest_resource(vehicle, world, vehicle.allowed_cargo)
        if resource:
            return {"type": "collect", "target": resource}

        # PRIORIDAD 7: Exploración (Ya usa celdas)
        return {"type": "move", "target": self.random_exploration(world)}