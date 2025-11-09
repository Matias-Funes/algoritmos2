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
        # PRIORIDAD 1: Evasión de minas (Ya usa celdas)
        escape = self.evade_mines(vehicle, world)
        if escape:
            return {"type": "move", "target": escape}

        # PRIORIDAD 2: Si tiene persona, regresar inmediatamente
        if len(vehicle.cargo) > 0:
            return {"type": "return_to_base"}

        # PRIORIDAD 3: Buscar persona más cercana
        resource = self.find_nearest_resource(vehicle, world, ["person"])
        if resource:
            # Comprobación de seguridad (ahora usa píxeles solo para 'is_near_mine')
            if not self.is_near_mine(vehicle, world, safety_margin=25):
                return {"type": "collect", "target": resource}
            else:
                # Buscar otra persona más segura (lógica convertida a celdas)
                safe_resources = []
                for res in world.resources:
                    if res.type == "person":
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
                    # Buscar la más cercana usando distancia de celdas
                    nearest = min(safe_resources, key=lambda r: 
                                  abs(vehicle.gx - world.pixel_to_cell(r.x, r.y)[0]) + 
                                  abs(vehicle.gy - world.pixel_to_cell(r.x, r.y)[1]))
                    return {"type": "collect", "target": nearest}

        # PRIORIDAD 4: Exploración rápida (Ya usa celdas)
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
        # PRIORIDAD 1: Evasión de minas (Ya usa celdas)
        escape = self.evade_mines(vehicle, world)
        if escape:
            return {"type": "move", "target": escape}

        # PRIORIDAD 2: Si tiene carga, regresar
        if len(vehicle.cargo) > 0:
            return {"type": "return_to_base"}

        # PRIORIDAD 3: Buscar personas primero (convertido a celdas)
        person = self.find_nearest_resource(vehicle, world, ["person"])
        if person:
            person_gx, person_gy = world.pixel_to_cell(person.x, person.y)
            dist = abs(vehicle.gx - person_gx) + abs(vehicle.gy - person_gy)
            
            # (150 píxeles son aprox. 4-5 celdas)
            if dist < 5: 
                return {"type": "collect", "target": person}

        # PRIORIDAD 4: Buscar medicamentos (convertido a celdas)
        medicine = self.find_nearest_resource(vehicle, world, ["medicine"])
        if medicine:
            med_gx, med_gy = world.pixel_to_cell(medicine.x, medicine.y)
            dist = abs(vehicle.gx - med_gx) + abs(vehicle.gy - med_gy)
            
            # (120 píxeles son aprox. 3-4 celdas)
            if dist < 4: 
                return {"type": "collect", "target": medicine}

        # PRIORIDAD 5: Buscar cualquier recurso permitido cercano (Ya usa celdas)
        resource = self.find_nearest_resource(vehicle, world, vehicle.allowed_cargo)
        if resource:
            return {"type": "collect", "target": resource}

        # PRIORIDAD 6: Explorar (Ya usa celdas)
        return {"type": "move", "target": self.random_exploration(world)}