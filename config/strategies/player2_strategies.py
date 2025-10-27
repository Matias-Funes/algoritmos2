# config/strategies/player2_strategies.py
from .base_strategy import BaseStrategy
import math
import random

# -------------------------------
# Estrategia para JEEP - Agresiva (ataca enemigos)
# -------------------------------
class AggressiveJeepStrategy(BaseStrategy):
    def decide(self, vehicle, world):
        # PRIORIDAD 1: Evasión de minas
        escape = self.evade_mines(vehicle, world)
        if escape:
            return {"type": "move", "target": escape}

        # PRIORIDAD 2: Buscar y atacar enemigos cercanos
        enemy = world.find_nearest_enemy(vehicle)
        if enemy and enemy.alive:
            dist_to_enemy = vehicle.distance_to(enemy)
            
            # Si está muy cerca, interceptar
            if dist_to_enemy < 60:
                return {"type": "move", "target": (enemy.x, enemy.y)}

        # PRIORIDAD 3: Regresar si tiene suficiente carga
        if len(vehicle.cargo) >= 3 or vehicle.trips_left == 0:
            return {"type": "return_to_base", "target": vehicle.base_position}

        # PRIORIDAD 4: Buscar recursos valiosos (arriesgado)
        resource = self.find_high_value_resource(
            vehicle, world,
            vehicle.allowed_cargo,
            min_value=20  # Solo los más valiosos
        )
        
        if resource:
            return {"type": "collect", "target": resource}

        # PRIORIDAD 5: Buscar cualquier recurso
        resource = self.find_nearest_resource(vehicle, world, vehicle.allowed_cargo)
        if resource:
            return {"type": "collect", "target": resource}

        # PRIORIDAD 6: Exploración agresiva
        return {"type": "move", "target": self.random_exploration(world)}


# -------------------------------
# Estrategia para MOTO - Rápida y cautelosa
# -------------------------------
class FastMotoStrategy(BaseStrategy):
    def decide(self, vehicle, world):
        # PRIORIDAD 1: Evasión de minas (más sensible)
        escape = self.evade_mines(vehicle, world)
        if escape:
            return {"type": "move", "target": escape}

        # PRIORIDAD 2: Si tiene carga, regresar rápido
        if len(vehicle.cargo) > 0:
            return {"type": "return_to_base", "target": vehicle.base_position}

        # PRIORIDAD 3: Evitar enemigos cercanos
        enemy = world.find_nearest_enemy(vehicle)
        if enemy and enemy.alive:
            dist_to_enemy = vehicle.distance_to(enemy)
            if dist_to_enemy < 40:
                # Escapar del enemigo
                dx = vehicle.x - enemy.x
                dy = vehicle.y - enemy.y
                dist = math.hypot(dx, dy)
                if dist > 0:
                    escape_x = vehicle.x + (dx / dist) * 50
                    escape_y = vehicle.y + (dy / dist) * 50
                    return {"type": "move", "target": (escape_x, escape_y)}

        # PRIORIDAD 4: Buscar persona más cercana en zona segura
        safe_people = []
        for res in world.resources:
            if res.type == "person":
                # Verificar distancia a minas
                safe = True
                for mine in world.mines:
                    if mine.active:
                        mine_cx = mine.x + mine.size / 2
                        mine_cy = mine.y + mine.size / 2
                        if math.hypot(res.x - mine_cx, res.y - mine_cy) < mine.radius + 25:
                            safe = False
                            break
                if safe:
                    safe_people.append(res)
        
        if safe_people:
            nearest = min(safe_people, key=lambda r: math.hypot(vehicle.x - r.x, vehicle.y - r.y))
            return {"type": "collect", "target": nearest}

        # PRIORIDAD 5: Exploración rápida
        return {"type": "move", "target": self.random_exploration(world)}


# -------------------------------
# Estrategia para CAMIÓN - Apoyo (recolección masiva)
# -------------------------------
class SupportCamionStrategy(BaseStrategy):
    def decide(self, vehicle, world):
        # PRIORIDAD 1: Evasión de minas
        escape = self.evade_mines(vehicle, world)
        if escape:
            return {"type": "move", "target": escape}

        # PRIORIDAD 2: Regresar cuando esté lleno
        if len(vehicle.cargo) >= 6 or vehicle.trips_left == 0:
            return {"type": "return_to_base", "target": vehicle.base_position}

        # PRIORIDAD 3: Priorizar recursos de valor medio-alto
        resource = self.find_high_value_resource(
            vehicle, world,
            vehicle.allowed_cargo,
            min_value=10
        )
        
        if resource:
            # Verificar que no esté muy cerca de minas
            dist_to_mine = self.nearest_mine_distance(vehicle, world)
            if dist_to_mine > 20:
                return {"type": "collect", "target": resource}

        # PRIORIDAD 4: Recolectar recursos seguros
        safe_resources = []
        for res in world.resources:
            if res.type in vehicle.allowed_cargo:
                dist_to_mine = float("inf")
                for mine in world.mines:
                    if mine.active:
                        mine_cx = mine.x + mine.size / 2
                        mine_cy = mine.y + mine.size / 2
                        d = math.hypot(res.x - mine_cx, res.y - mine_cy)
                        dist_to_mine = min(dist_to_mine, d)
                
                if dist_to_mine > 25:
                    safe_resources.append(res)
        
        if safe_resources:
            nearest = min(safe_resources, key=lambda r: math.hypot(vehicle.x - r.x, vehicle.y - r.y))
            return {"type": "collect", "target": nearest}

        # PRIORIDAD 5: Exploración
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
            return {"type": "return_to_base", "target": vehicle.base_position}

        # PRIORIDAD 3: Evitar enemigos cercanos
        enemy = world.find_nearest_enemy(vehicle)
        if enemy and enemy.alive:
            dist_to_enemy = vehicle.distance_to(enemy)
            if dist_to_enemy < 30:
                # Movimiento evasivo
                dx = vehicle.x - enemy.x
                dy = vehicle.y - enemy.y
                dist = math.hypot(dx, dy)
                if dist > 0:
                    escape_x = vehicle.x + (dx / dist) * 25
                    escape_y = vehicle.y + (dy / dist) * 25
                    # Mantener en límites
                    escape_x = max(30, min(escape_x, world.width - 30))
                    escape_y = max(30, min(escape_y, world.height - 30))
                    return {"type": "move", "target": (escape_x, escape_y)}

        # PRIORIDAD 4: Buscar personas (alto valor)
        person = self.find_nearest_resource(vehicle, world, ["person"])
        if person:
            dist_to_person = math.hypot(vehicle.x - person.x, vehicle.y - person.y)
            if dist_to_person < 150:
                return {"type": "collect", "target": person}

        # PRIORIDAD 5: Buscar medicamentos
        medicine = self.find_nearest_resource(vehicle, world, ["medicine"])
        if medicine:
            dist_to_med = math.hypot(vehicle.x - medicine.x, vehicle.y - medicine.y)
            if dist_to_med < 120:
                return {"type": "collect", "target": medicine}

        # PRIORIDAD 6: Buscar cualquier recurso permitido
        resource = self.find_nearest_resource(vehicle, world, vehicle.allowed_cargo)
        if resource:
            return {"type": "collect", "target": resource}

        # PRIORIDAD 7: Exploración cautelosa
        return {"type": "move", "target": self.random_exploration(world)}