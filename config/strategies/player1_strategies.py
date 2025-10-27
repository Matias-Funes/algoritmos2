# config/strategies/player1_strategies.py
from .base_strategy import BaseStrategy
import math

# -------------------------------
# Estrategia para JEEP - Recolector versátil
# -------------------------------
class JeepStrategy(BaseStrategy):
    def decide(self, vehicle, world):
        # PRIORIDAD 1: Evasión de minas
        escape = self.evade_mines(vehicle, world)
        if escape:
            return {"type": "move", "target": escape}

        # PRIORIDAD 2: Regresar a base si es necesario
        if self.should_return_to_base(vehicle):
            return {"type": "return_to_base", "target": vehicle.base_position}

        # PRIORIDAD 3: Buscar recursos de alto valor
        resource = self.find_high_value_resource(
            vehicle, world, 
            vehicle.allowed_cargo,
            min_value=15  # Prioriza medicamentos y armas
        )
        
        if resource:
            return {"type": "collect", "target": resource}

        # PRIORIDAD 4: Buscar cualquier recurso permitido
        resource = self.find_nearest_resource(vehicle, world, vehicle.allowed_cargo)
        if resource:
            return {"type": "collect", "target": resource}

        # PRIORIDAD 5: Explorar
        return {"type": "move", "target": self.random_exploration(world)}


# -------------------------------
# Estrategia para MOTO - Rescate rápido de personas
# -------------------------------
class MotoStrategy(BaseStrategy):
    def decide(self, vehicle, world):
        # PRIORIDAD 1: Evasión de minas
        escape = self.evade_mines(vehicle, world)
        if escape:
            return {"type": "move", "target": escape}

        # PRIORIDAD 2: Si tiene persona, regresar inmediatamente
        if len(vehicle.cargo) > 0:
            return {"type": "return_to_base", "target": vehicle.base_position}

        # PRIORIDAD 3: Buscar persona más cercana
        resource = self.find_nearest_resource(vehicle, world, ["person"])
        if resource:
            # Verificar que no esté cerca de minas
            if not self.is_near_mine(vehicle, world, safety_margin=25):
                return {"type": "collect", "target": resource}
            else:
                # Buscar otra persona más segura
                safe_resources = []
                for res in world.resources:
                    if res.type == "person":
                        # Simular si es seguro ir allí
                        dist_to_mine = float("inf")
                        for mine in world.mines:
                            if mine.active:
                                mine_cx = mine.x + mine.size / 2
                                mine_cy = mine.y + mine.size / 2
                                d = math.hypot(res.x - mine_cx, res.y - mine_cy)
                                dist_to_mine = min(dist_to_mine, d)
                        
                        if dist_to_mine > 30:  # Zona segura
                            safe_resources.append(res)
                
                if safe_resources:
                    nearest = min(safe_resources, key=lambda r: math.hypot(vehicle.x - r.x, vehicle.y - r.y))
                    return {"type": "collect", "target": nearest}

        # PRIORIDAD 4: Exploración rápida
        return {"type": "move", "target": self.random_exploration(world)}


# -------------------------------
# Estrategia para CAMIÓN - Recolector masivo
# -------------------------------
class CamionStrategy(BaseStrategy):
    def decide(self, vehicle, world):
        # PRIORIDAD 1: Evasión de minas
        escape = self.evade_mines(vehicle, world)
        if escape:
            return {"type": "move", "target": escape}

        # PRIORIDAD 2: Regresar si está lleno o sin viajes
        if len(vehicle.cargo) >= 5 or vehicle.trips_left == 0:
            return {"type": "return_to_base", "target": vehicle.base_position}

        # PRIORIDAD 3: Buscar recursos valiosos
        resource = self.find_high_value_resource(
            vehicle, world,
            vehicle.allowed_cargo,
            min_value=10
        )
        
        if resource:
            return {"type": "collect", "target": resource}

        # PRIORIDAD 4: Buscar cualquier recurso
        resource = self.find_nearest_resource(vehicle, world, vehicle.allowed_cargo)
        if resource:
            return {"type": "collect", "target": resource}

        # PRIORIDAD 5: Explorar zonas nuevas
        return {"type": "move", "target": self.random_exploration(world)}


# -------------------------------
# Estrategia para AUTO - Equilibrado
# -------------------------------
class AutoStrategy(BaseStrategy):
    def decide(self, vehicle, world):
        # PRIORIDAD 1: Evasión de minas
        escape = self.evade_mines(vehicle, world)
        if escape:
            return {"type": "move", "target": escape}

        # PRIORIDAD 2: Si tiene carga, regresar
        if len(vehicle.cargo) > 0:
            return {"type": "return_to_base", "target": vehicle.base_position}

        # PRIORIDAD 3: Buscar personas primero (alto valor)
        person = self.find_nearest_resource(vehicle, world, ["person"])
        if person and math.hypot(vehicle.x - person.x, vehicle.y - person.y) < 150:
            return {"type": "collect", "target": person}

        # PRIORIDAD 4: Buscar medicamentos
        medicine = self.find_nearest_resource(vehicle, world, ["medicine"])
        if medicine and math.hypot(vehicle.x - medicine.x, vehicle.y - medicine.y) < 120:
            return {"type": "collect", "target": medicine}

        # PRIORIDAD 5: Buscar cualquier recurso permitido cercano
        resource = self.find_nearest_resource(vehicle, world, vehicle.allowed_cargo)
        if resource:
            return {"type": "collect", "target": resource}

        # PRIORIDAD 6: Explorar
        return {"type": "move", "target": self.random_exploration(world)}