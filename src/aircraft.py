import math
import pygame
from . import constants
from . import pathfinding


class Vehicle:
    def __init__(self, id, gx, gy, base_position, vehicle_type, max_trips, allowed_cargo, color):
        self.id = id
        self.gx = gx
        self.gy = gy
        self.x = self.gx * constants.TILE + constants.TILE // 2
        self.y = self.gy * constants.TILE + constants.TILE // 2

        self.target_pixel_x = self.x
        self.target_pixel_y = self.y
        self.speed_pixels_per_update = 1.5  # Velocidad de animación
        
        self.current_target_cell = None # La celda (gx, gy) a la que nos movemos
        
        self.vehicle_type = vehicle_type
        
        self.base_pixel_pos = (float(base_position[0]), float(base_position[1]))
        self.base_gx = int(base_position[0]) // constants.TILE
        self.base_gy = int(base_position[1]) // constants.TILE
        self.base_target_cell = (self.base_gx, self.base_gy) # Celda objetivo para A*
        self.base_radius_grid = constants.BASE_RADIUS_PIXELS // constants.TILE
        
        self.trips_left = max_trips
        self.max_trips = max_trips
        self.allowed_cargo = allowed_cargo
        self.cargo = []
        self.color = color
        self.alive = True
        self.target = None # El objetivo será un (gx, gy) o un objeo
        self.strategy = None
        self.path = [] 
        self.score = 0
        self.returning_to_base = False
        self.at_base = True # Empieza en la base
        self.forced_return = False
        
        self.wait_timer = 0 # Temporizador para esperar si el camino está bloqueado
        self.evasion_timer = 0 # Temporizador para forzar un estado de evasión
        
        self.size = self._get_vehicle_size()
        self.image = self._create_beautiful_sprite()
           
    def _get_vehicle_size(self):
        """Tamaño según tipo de vehículo (en píxeles, basado en TILE)"""
        return int(constants.VEHICLE_SIZES.get(self.vehicle_type, 0.85 * constants.TILE))
    
    def _create_beautiful_sprite(self):
        """Crea sprites hermosos estilo vista superior"""
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2
        
        if self.vehicle_type == "jeep":
            # JEEP 4x4 estilo isométrico superior
            
            # Sombra suave
            shadow = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 60), (3, self.size-10, self.size-6, 8))
            surface.blit(shadow, (0, 0))
            
            # Carrocería principal con degradado
            body_color = self.color
            lighter = tuple(min(c + 60, 255) for c in body_color[:3])
            darker = tuple(max(c - 30, 0) for c in body_color[:3])
            
            # Parte trasera (más oscura)
            pygame.draw.rect(surface, darker, (5, 14, self.size-10, 10), border_radius=2)
            # Parte delantera (más clara)
            pygame.draw.rect(surface, body_color, (5, 8, self.size-10, 12), border_radius=3)
            # Capó brillante
            pygame.draw.rect(surface, lighter, (7, 8, self.size-14, 5), border_radius=2)
            
            # Parabrisas azul brillante
            pygame.draw.rect(surface, (120, 180, 230), (8, 10, self.size-16, 6))
            pygame.draw.rect(surface, (180, 220, 255), (8, 10, self.size-16, 2))
            
            # Ruedas negras con llantas grises
            wheel_positions = [(4, 10), (self.size-8, 10), (4, 18), (self.size-8, 18)]
            for wx, wy in wheel_positions:
                pygame.draw.circle(surface, (30, 30, 30), (wx, wy), 4)
                pygame.draw.circle(surface, (100, 100, 100), (wx, wy), 2)
            
            # Faros amarillos
            pygame.draw.circle(surface, (255, 255, 150), (8, 8), 2)
            pygame.draw.circle(surface, (255, 255, 150), (self.size-8, 8), 2)
            
            # Espejos retrovisores
            pygame.draw.rect(surface, (80, 80, 80), (3, 12, 2, 3))
            pygame.draw.rect(surface, (80, 80, 80), (self.size-5, 12, 2, 3))
            
        elif self.vehicle_type == "moto":
            # MOTO deportiva estilo superior
            
            # Sombra
            shadow = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 60), (4, self.size-8, self.size-8, 6))
            surface.blit(shadow, (0, 0))
            
            body_color = self.color
            lighter = tuple(min(c + 60, 255) for c in body_color[:3])
            darker = tuple(max(c - 30, 0) for c in body_color[:3])
            
            # Cuerpo alargado
            pygame.draw.ellipse(surface, body_color, (7, 6, self.size-14, self.size-12))
            pygame.draw.ellipse(surface, lighter, (7, 6, self.size-14, 6))
            
            # Tanque de combustible
            pygame.draw.ellipse(surface, darker, (9, center-3, self.size-18, 8))
            
            # Asiento
            pygame.draw.rect(surface, (50, 50, 50), (8, center, self.size-16, 4), border_radius=2)
            
            # Ruedas grandes
            pygame.draw.circle(surface, (30, 30, 30), (center, 8), 4)
            pygame.draw.circle(surface, (80, 80, 80), (center, 8), 2)
            pygame.draw.circle(surface, (30, 30, 30), (center, self.size-8), 4)
            pygame.draw.circle(surface, (80, 80, 80), (center, self.size-8), 2)
            
            # Manillar
            pygame.draw.line(surface, (150, 150, 150), (center-4, 7), (center+4, 7), 2)
            
            # Faro delantero brillante
            pygame.draw.circle(surface, (255, 255, 200), (center, 5), 2)
            pygame.draw.circle(surface, (255, 255, 255), (center, 4), 1)
            
        elif self.vehicle_type == "camion":
            # CAMIÓN de carga pesado
            
            # Sombra
            shadow = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 70), (2, self.size-11, self.size-4, 9))
            surface.blit(shadow, (0, 0))
            
            body_color = self.color
            lighter = tuple(min(c + 60, 255) for c in body_color[:3])
            darker = tuple(max(c - 30, 0) for c in body_color[:3])
            
            # Contenedor de carga (parte trasera)
            pygame.draw.rect(surface, darker, (4, 12, self.size-8, self.size-16), border_radius=2)
            pygame.draw.rect(surface, body_color, (5, 13, self.size-10, 4))
            
            # Líneas del contenedor
            for i in range(2):
                y = 16 + i * 4
                pygame.draw.line(surface, (0, 0, 0, 80), (6, y), (self.size-6, y), 1)
            
            # Cabina del conductor (adelante)
            pygame.draw.rect(surface, body_color, (7, 5, self.size-14, 10), border_radius=2)
            pygame.draw.rect(surface, lighter, (7, 5, self.size-14, 4), border_radius=2)
            
            # Parabrisas
            pygame.draw.rect(surface, (120, 180, 230), (9, 7, self.size-18, 5))
            pygame.draw.rect(surface, (180, 220, 255), (9, 7, self.size-18, 2))
            
            # Ruedas traseras dobles
            wheel_y = self.size - 5
            pygame.draw.circle(surface, (30, 30, 30), (8, wheel_y), 5)
            pygame.draw.circle(surface, (80, 80, 80), (8, wheel_y), 3)
            pygame.draw.circle(surface, (30, 30, 30), (center, wheel_y), 5)
            pygame.draw.circle(surface, (80, 80, 80), (center, wheel_y), 3)
            pygame.draw.circle(surface, (30, 30, 30), (self.size-8, wheel_y), 5)
            pygame.draw.circle(surface, (80, 80, 80), (self.size-8, wheel_y), 3)
            
            # Faros
            pygame.draw.circle(surface, (255, 255, 150), (9, 6), 2)
            pygame.draw.circle(surface, (255, 255, 150), (self.size-9, 6), 2)
            
            # Parachoques
            pygame.draw.rect(surface, (100, 100, 100), (6, 4, self.size-12, 2))
            
        elif self.vehicle_type == "auto":
            # AUTO sedan elegante - VISTA SUPERIOR VERTICAL (no tumbado)
            
            # Sombra
            shadow = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 60), (3, self.size-9, self.size-6, 7))
            surface.blit(shadow, (0, 0))
            
            body_color = self.color
            lighter = tuple(min(c + 60, 255) for c in body_color[:3])
            darker = tuple(max(c - 30, 0) for c in body_color[:3])
            
            # Carrocería principal (cuerpo vertical del auto)
            # Parte trasera del auto
            pygame.draw.rect(surface, darker, (6, self.size-14, self.size-12, 8), border_radius=3)
            
            # Parte central del auto
            pygame.draw.rect(surface, body_color, (5, 8, self.size-10, self.size-16), border_radius=3)
            
            # Capó brillante (parte delantera)
            pygame.draw.rect(surface, lighter, (6, 6, self.size-12, 6), border_radius=3)
            
            # Techo/cabina (ventanas)
            pygame.draw.rect(surface, (100, 150, 200), (7, 10, self.size-14, 8), border_radius=2)
            
            # Ventanas laterales con efecto de profundidad
            # Ventana izquierda
            pygame.draw.rect(surface, (80, 130, 180), (7, 11, 3, 6))
            # Ventana derecha
            pygame.draw.rect(surface, (80, 130, 180), (self.size-10, 11, 3, 6))
            
            # Brillo en el parabrisas delantero
            pygame.draw.rect(surface, (180, 220, 255), (8, 10, self.size-16, 2))
            
            # Ruedas (vista superior - círculos a los lados)
            # Ruedas delanteras
            pygame.draw.circle(surface, (30, 30, 30), (5, 8), 3)
            pygame.draw.circle(surface, (100, 100, 100), (5, 8), 2)
            pygame.draw.circle(surface, (30, 30, 30), (self.size-5, 8), 3)
            pygame.draw.circle(surface, (100, 100, 100), (self.size-5, 8), 2)
            
            # Ruedas traseras
            pygame.draw.circle(surface, (30, 30, 30), (5, self.size-8), 3)
            pygame.draw.circle(surface, (100, 100, 100), (5, self.size-8), 2)
            pygame.draw.circle(surface, (30, 30, 30), (self.size-5, self.size-8), 3)
            pygame.draw.circle(surface, (100, 100, 100), (self.size-5, self.size-8), 2)
            
            # Faros delanteros
            pygame.draw.circle(surface, (255, 255, 200), (7, 5), 2)
            pygame.draw.circle(surface, (255, 255, 200), (self.size-7, 5), 2)
            pygame.draw.circle(surface, (255, 255, 255), (7, 4), 1)
            pygame.draw.circle(surface, (255, 255, 255), (self.size-7, 4), 1)
            
            # Parachoques delantero
            pygame.draw.rect(surface, (150, 150, 150), (5, 3, self.size-10, 2), border_radius=1)
            
            # Luces traseras
            pygame.draw.circle(surface, (200, 0, 0), (7, self.size-6), 1)
            pygame.draw.circle(surface, (200, 0, 0), (self.size-7, self.size-6), 1)
            
            # Parachoques trasero
            pygame.draw.rect(surface, (150, 150, 150), (5, self.size-4, self.size-10, 2), border_radius=1)
            
            # Detalles adicionales (espejos retrovisores)
            pygame.draw.rect(surface, (80, 80, 80), (3, 12, 2, 2))
            pygame.draw.rect(surface, (80, 80, 80), (self.size-5, 12, 2, 2))
        
        return surface
    
    def get_state(self):
        """Devuelve un diccionario con el estado completo del vehículo."""
        cargo_list = [item.type for item in self.cargo]
        
        return {
            "id": self.id,
            "gx": self.gx,
            "gy": self.gy, 
            "vehicle_type": self.vehicle_type,
            "trips_left": self.trips_left,
            "cargo": cargo_list,
            "alive": self.alive,
            "score": self.score,
            "returning_to_base": self.returning_to_base,
            "at_base": self.at_base,
            "forced_return": self.forced_return,
            "color": self.color,
            "base_position_pixels": self.base_pixel_pos,
            "base_position_grid": self.base_target_cell,
            "strategy_name": self.strategy.__class__.__name__ if self.strategy else None
        }

    def is_at_visual_target(self):
        """Comprueba si el sprite ha llegado al centro de la celda objetivo."""
        return self.x == self.target_pixel_x and self.y == self.target_pixel_y
    
    def distance_to(self, obj):
        return abs(self.gx - obj.gx) + abs(self.gy - obj.gy) # Manhattan

    def distance_to_point(self, gx, gy):
        return abs(self.gx - gx) + abs(self.gy - gy)
    
    def update(self, world):
        """
        Actualiza el estado LÓGICO (si está quieto) y el VISUAL (si se mueve).
        Devuelve True si fue un tick LÓGICO, False si fue solo de ANIMACIÓN.
        """
        
        if not self.alive:
            return False # No hubo cambio lógico

        # --- Lógica de Temporizadores ---
        if self.wait_timer > 0:
            self.wait_timer -= 1
            return True # Es un tick lógico, pero estamos esperando
        if self.evasion_timer > 0:
            self.evasion_timer -= 1
        # 1. ¿Estamos quietos? (En el centro de una celda)
        if self.is_at_visual_target():
            
            # --- Lógica de llegada a una celda ---
            if self.current_target_cell:
                self.gx, self.gy = self.current_target_cell
                self.current_target_cell = None
            
            # Intentar recolectar (¡esto es un evento lógico!)
            self.try_collect_at_current_cell(world)

            # --- Lógica de Decisión (¿Qué hacemos ahora?) ---
            if self.forced_return:
                if self.distance_to_point(self.base_gx, self.base_gy) <= self.base_radius_grid:
                    self.at_base = True
                    self.deliver_cargo()
                    self.forced_return = False  # 🔧 Resetear forced_return
                    return True # Evento lógico
                else:
                    self.at_base = False
                    if not self.path:
                        self.set_path_to_base(world)

            elif self.returning_to_base:
                if self.distance_to_point(self.base_gx, self.base_gy) <= self.base_radius_grid:
                    self.at_base = True
                    self.deliver_cargo()
                    self.returning_to_base = False
                    self.trips_left = self.max_trips
                    self.path.clear()
                    # Tomar decisión inmediata después de entregar
                    if self.strategy and len(world.resources) > 0:
                        action = self.strategy.decide(self, world)
                        self.execute_action(action, world)
                    return True # Evento lógico
                else:
                    self.at_base = False
                    if not self.path:
                        self.set_path_to_base(world)
            
            # Siempre intentar tomar una decisión si no tenemos path
            if not self.path and not self.forced_return and not self.returning_to_base and self.evasion_timer == 0:
                if self.strategy:
                    action = self.strategy.decide(self, world)
                    self.execute_action(action, world)
                    if self.path:
                        self.at_base = False
            
            # --- Lógica de Movimiento (Si la lógica anterior generó un 'path') ---
            if self.path:
                (next_gx, next_gy) = self.path[0] 
                
                if self.is_cell_safe(next_gx, next_gy, world):
                    (next_gx, next_gy) = self.path.pop(0) 
                    self.current_target_cell = (next_gx, next_gy)
                    self.target_pixel_x = next_gx * constants.TILE + constants.TILE // 2
                    self.target_pixel_y = next_gy * constants.TILE + constants.TILE // 2
                else:
                    # 🔧 Si la celda no es segura, ESPERAR en lugar de borrar la ruta.
                    self.wait_timer = 5 # Espera 5 ticks lógicos
                    self.path.clear() # Borramos la ruta para forzar un recalculo DESPUÉS de esperar
            
            return True # Fue un tick LÓGICO (tomamos decisiones o esperamos)

        # 2. ¿Nos estamos moviendo? (Interpolación visual)
        if not self.is_at_visual_target():
            
            # Moverse hacia self.target_pixel_x
            if self.x < self.target_pixel_x:
                self.x = min(self.x + self.speed_pixels_per_update, self.target_pixel_x)
            elif self.x > self.target_pixel_x:
                self.x = max(self.x - self.speed_pixels_per_update, self.target_pixel_x)
            
            if self.y < self.target_pixel_y:
                self.y = min(self.y + self.speed_pixels_per_update, self.target_pixel_y)
            elif self.y > self.target_pixel_y:
                self.y = max(self.y - self.speed_pixels_per_update, self.target_pixel_y)

        return False # Fue solo un tick de ANIMACIÓN

    def is_cell_safe(self, gx, gy, world):
        """
        Comprueba si la celda es segura contra OBSTÁCULOS ESTÁTICOS (minas/árboles)
        Y contra ALIADOS (tanto su posición actual como la celda a la que se dirigen).
        """
        # 1. ¿Está en el mapa?
        if not (0 <= gx < constants.GRID_WIDTH and 0 <= gy < constants.GRID_HEIGHT):
            return False

        # 2. ¿Hay un obstáculo (árbol)?
        if world.grid[gy][gx] == 1: # 1 = Árbol
             return False
                
        # 3. ¿Hay una mina?
        # if self.check_mine_collision(gx, gy, world):
        #      return False
        
        # 4. ¿Hay un ALIADO ocupando esa celda?
        for v in world.vehicles:
            if v is self or not v.alive:
                continue
            
            # Solo nos importan los aliados (mismo color)
            if v.color == self.color:
                
                # Comprobamos si el aliado YA ESTÁ en la celda
                is_at_target_cell = (v.gx == gx and v.gy == gy)
                
                # O si el aliado ESTÁ YENDO a esa celda
                is_moving_to_target_cell = (v.current_target_cell == (gx, gy))

                if is_at_target_cell or is_moving_to_target_cell:
                    
                    # (Lógica de la base: si está en su base, lo ignoramos)
                    v_at_base = (v.gx == v.base_gx and v.gy == v.base_gy)
                    if v_at_base:
                        continue

                    # La celda está ocupada O "reservada" por un aliado.
                    return False

        return True # La celda es segura
    
    def set_path_to_base(self, world):
        """Calcula la ruta a la base usando A* (A-Estrella)"""
        
        start_cell = (self.gx, self.gy)
        # self.base_target_cell es (base_gx, base_gy)
        
        # Llamamos a la función A*
        path_list = pathfinding.a_star(start_cell, self.base_target_cell, world)
        
        if path_list and len(path_list) > 1:
            self.path = path_list[1:] # Omitir el primer nodo (posición actual)
        else:
            self.path = [] # No se encontró ruta o ya estamos en la base
    
    def force_return_to_base(self):
        self.forced_return = True
        self.returning_to_base = False
        self.path.clear() # Borra la ruta actual

    def execute_action(self, action, world):
        """Interpreta la acción de la estrategia y define un 'path'."""
        if not action or "type" not in action:
            self.path = [] # No hacer nada
            return

        action_type = action["type"]
        target = action.get("target") # target puede ser un objeto o (gx, gy)
        
        start_cell = (self.gx, self.gy)
        target_cell = None

        if action_type == "move" and target:
            # Asumimos que el target es (gx, gy)
            target_cell = target
        
        elif action_type == "evade" and target:
            target_cell = target
            # Al evadir, activamos el temporizador para evitar oscilaciones
            self.evasion_timer = 20 # 20 ticks lógicos en estado de evasión

        elif action_type == "collect" and target:
            # Target es un objeto recurso. Convertimos sus píxeles a celda.
            target_gx = int(target.x) // constants.TILE
            target_gy = int(target.y) // constants.TILE
            target_cell = (target_gx, target_gy)

        elif action_type == "return_to_base":
            self.returning_to_base = True
            self.set_path_to_base(world) # Esta función ya se encarga de todo
            return # Salimos de la función aquí

        # Calcular la ruta si tenemos un objetivo válido
        if target_cell and target_cell != start_cell:
            path_list = pathfinding.a_star(start_cell, target_cell, world)
            
            if path_list and len(path_list) > 1:
                self.path = path_list[1:] # Omitir el primer nodo
            else:
                self.path = [] # No se encontró ruta
        else:
            self.path = [] # Objetivo inválido o ya estamos en él

    def try_collect_at_current_cell(self, world):
        """Intenta recoger recursos EN la celda actual."""
        for resource in world.resources[:]:
            res_gx = int(resource.x) // constants.TILE
            res_gy = int(resource.y) // constants.TILE
            
            if self.gx == res_gx and self.gy == res_gy:
                if resource.type in self.allowed_cargo:
                    self.collect(resource, world)
                    break # Solo recoge una cosa por turno

    def deliver_cargo(self):
        """Entrega la carga y suma puntos (función helper)."""
        if len(self.cargo) > 0:
            delivered_value = sum(item.value for item in self.cargo)
            self.score += delivered_value
            print(f"{self.id} entregó {len(self.cargo)} items por {delivered_value} puntos.")
        self.cargo.clear()

    def collect(self, resource, world):
        if resource.type not in self.allowed_cargo:
            return
        if resource not in world.resources:
            return
        
        self.cargo.append(resource)
        world.remove_resource(resource) # El mundo lo quita de las listas y la grid
        
        # Lógica de viaje único
        if self.vehicle_type in ["moto", "auto"]:
            self.trips_left -= 1
            self.returning_to_base = True
            self.path.clear() # Borra la ruta actual para recalcular (a la base)
        # Lógica de múltiples viajes
        elif self.vehicle_type in ["jeep", "camion"]:
            if self.should_return_to_base(): # Comprueba si está lleno
                self.trips_left -= 1
                self.returning_to_base = True
                self.path.clear()

    def should_return_to_base(self):
        """Determina si el vehículo debe regresar a la base."""
        if self.trips_left <= 0:
            return True
        
        cargo_limit = {"jeep": 3, "moto": 1, "camion": 5, "auto": 2}
        max_cargo = cargo_limit.get(self.vehicle_type, 2)
        
        if len(self.cargo) >= max_cargo:
            return True
        return False

    def check_mine_collision(self, gx, gy, world):
        """Verifica si una celda (gx, gy) está dentro del radio de una mina."""
        # Esta función es llamada por is_cell_safe ANTES de moverse
        px_center = gx * constants.TILE + constants.TILE // 2
        py_center = gy * constants.TILE + constants.TILE // 2
        
        for mine in world.mines:
            if not mine.active:
                continue
            
            # Usamos la función de chequeo de la propia mina
            if mine.check_collision(px_center, py_center):
                return True # Hay colisión
        return False # No hay colisión
    
    def die(self):
        print(f"¡{self.id} destruido!")
        self.alive = False
        self.cargo.clear()
        
    def draw(self, screen):
        """Dibuja el vehículo (sin rotación)"""
        if not self.alive:
            return
        
        # Dibujar sprite centrado en (self.x, self.y)
        rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(self.image, rect.topleft)
        
        # Indicador de carga
        if len(self.cargo) > 0:
            cargo_y = int(self.y - self.size//2 - 8)
            # Barra de fondo
            pygame.draw.rect(screen, (50, 50, 50), (int(self.x - 12), cargo_y, 24, 4), border_radius=2)
            # Barra de carga dorada
            cargo_width = int(24 * (len(self.cargo) / 5))
            pygame.draw.rect(screen, (255, 215, 0), (int(self.x - 12), cargo_y, cargo_width, 4), border_radius=2)
            # Número con sombra
            font = pygame.font.SysFont(None, 14, bold=True)
            shadow = font.render(str(len(self.cargo)), True, (0, 0, 0))
            text = font.render(str(len(self.cargo)), True, (255, 255, 255))
            screen.blit(shadow, (int(self.x - 3), cargo_y - 11))
            screen.blit(text, (int(self.x - 4), cargo_y - 12))
        
        # Indicador de retorno (flecha verde)
        if self.returning_to_base or self.forced_return:
            arrow_y = int(self.y - self.size//2 - 16)
            pygame.draw.circle(screen, (0, 255, 0), (int(self.x), arrow_y), 3)
            pygame.draw.polygon(screen, (0, 255, 0), [
                (int(self.x), arrow_y - 3),
                (int(self.x - 2), arrow_y + 1),
                (int(self.x + 2), arrow_y + 1)
            ])

class Jeep(Vehicle):
    def __init__(self, id, x, y, base_position, color):
        super().__init__(id, x, y, base_position, "jeep", 2,
                         ["person", "clothes", "food", "medicine", "weapons"], color)

class Moto(Vehicle):
    def __init__(self, id, x, y, base_position, color):
        super().__init__(id, x, y, base_position, "moto", 1, ["person"], color)

class Camion(Vehicle):
    def __init__(self, id, x, y, base_position, color):
        super().__init__(id, x, y, base_position, "camion", 3,
                         ["person", "clothes", "food", "medicine", "weapons"], color)

class Auto(Vehicle):
    def __init__(self, id, x, y, base_position, color):
        super().__init__(id, x, y, base_position, "auto", 1,
                         ["person", "clothes", "food", "medicine"], color)