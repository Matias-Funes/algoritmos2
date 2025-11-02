import math
import pygame

class Vehicle:
    def __init__(self, id, x, y, base_position, vehicle_type, max_trips, allowed_cargo, color):
        self.id = id
        self.x = float(x)
        self.y = float(y)
        self.vehicle_type = vehicle_type
        self.base_position = base_position
        self.trips_left = max_trips
        self.max_trips = max_trips
        self.allowed_cargo = allowed_cargo
        self.cargo = []
        self.color = color
        self.alive = True
        self.target = None
        self.strategy = None
        self.speed = 2
        self.score = 0
        self.returning_to_base = False
        self.at_base = False
        self.forced_return = False  # Para retorno forzado al final
        
        # Tamaño según tipo
        self.size = self._get_vehicle_size()
        
        # Para anti-amontonamiento
        self.separation_force_x = 0
        self.separation_force_y = 0
        
        # Crear sprite mejorado (SIN rotación)
        self.image = self._create_beautiful_sprite()
        
    def _get_vehicle_size(self):
        """Tamaño según tipo de vehículo"""
        sizes = {
            "jeep": 30,
            "moto": 22,
            "camion": 36,
            "auto": 26
        }
        return sizes.get(self.vehicle_type, 24)
    
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
            
            # Cuerpo alargado
            pygame.draw.ellipse(surface, body_color, (7, 6, self.size-14, self.size-12))
            pygame.draw.ellipse(surface, lighter, (7, 6, self.size-14, 6))
            
            # Tanque de combustible
            pygame.draw.ellipse(surface, darker if 'darker' in locals() else body_color, 
                              (9, center-3, self.size-18, 8))
            
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
            # AUTO sedan elegante
            
            # Sombra
            shadow = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 60), (3, self.size-9, self.size-6, 7))
            surface.blit(shadow, (0, 0))
            
            body_color = self.color
            lighter = tuple(min(c + 60, 255) for c in body_color[:3])
            darker = tuple(max(c - 30, 0) for c in body_color[:3])
            
            # Carrocería inferior
            pygame.draw.ellipse(surface, body_color, (4, 10, self.size-8, self.size-16))
            pygame.draw.ellipse(surface, lighter, (4, 10, self.size-8, 5))
            
            # Techo (habitáculo)
            pygame.draw.rect(surface, darker, (7, 6, self.size-14, 10), border_radius=3)
            pygame.draw.rect(surface, body_color, (7, 6, self.size-14, 4), border_radius=3)
            
            # Ventanas laterales con brillo
            pygame.draw.polygon(surface, (100, 150, 200), [(9, 8), (9, 13), (11, 11), (11, 10)])
            pygame.draw.polygon(surface, (100, 150, 200), [(self.size-9, 8), (self.size-9, 13), 
                                                           (self.size-11, 11), (self.size-11, 10)])
            # Brillo
            pygame.draw.line(surface, (180, 220, 255), (9, 8), (10, 9), 1)
            pygame.draw.line(surface, (180, 220, 255), (self.size-9, 8), (self.size-10, 9), 1)
            
            # Capó
            pygame.draw.rect(surface, lighter, (6, 8, self.size-12, 3))
            
            # Ruedas
            wheel_y = self.size - 6
            pygame.draw.circle(surface, (30, 30, 30), (8, wheel_y), 4)
            pygame.draw.circle(surface, (100, 100, 100), (8, wheel_y), 2)
            pygame.draw.circle(surface, (30, 30, 30), (self.size-8, wheel_y), 4)
            pygame.draw.circle(surface, (100, 100, 100), (self.size-8, wheel_y), 2)
            
            # Faros delanteros elegantes
            pygame.draw.circle(surface, (255, 255, 200), (7, 9), 2)
            pygame.draw.circle(surface, (255, 255, 200), (self.size-7, 9), 2)
            pygame.draw.circle(surface, (255, 255, 255), (7, 8), 1)
            pygame.draw.circle(surface, (255, 255, 255), (self.size-7, 8), 1)
            
            # Parachoques cromado
            pygame.draw.rect(surface, (150, 150, 150), (5, 7, self.size-10, 2), border_radius=1)
        
        return surface

    def get_state(self):
        """Devuelve un diccionario con el estado completo del vehículo."""
        
        # Guardamos la carga como una lista de 'tipos', no como objetos
        cargo_list = [item.type for item in self.cargo]
        
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "vehicle_type": self.vehicle_type,
            "trips_left": self.trips_left,
            "cargo": cargo_list, # Lista de strings
            "alive": self.alive,
            "score": self.score,
            "returning_to_base": self.returning_to_base,
            "at_base": self.at_base,
            "forced_return": self.forced_return,
            "speed": self.speed,
            "color": self.color,
            "base_position": self.base_position
            # NOTA: No guardamos 'strategy' o 'target',
            # se asumirá que la IA los recalcula al cargar.
        }
    
    def distance_to(self, obj):
        """Distancia euclidiana a otro objeto"""
        return math.hypot(self.x - obj.x, self.y - obj.y)

    def distance_to_point(self, x, y):
        """Distancia a un punto específico"""
        return math.hypot(self.x - x, self.y - y)

    def apply_separation(self, vehicles, separation_distance=35):
        """Sistema anti-amontonamiento mejorado"""
        self.separation_force_x = 0
        self.separation_force_y = 0
        
        for other in vehicles:
            if other is self or not other.alive:
                continue
            
            # Solo separar del mismo equipo
            if other.color != self.color:
                continue
            
            dist = self.distance_to(other)
            
            if dist < separation_distance and dist > 0:
                force_magnitude = (separation_distance - dist) / separation_distance
                
                dx = self.x - other.x
                dy = self.y - other.y
                
                length = math.hypot(dx, dy)
                if length > 0:
                    dx /= length
                    dy /= length
                    
                    self.separation_force_x += dx * force_magnitude * 2.5
                    self.separation_force_y += dy * force_magnitude * 2.5

    def move_towards(self, target_x, target_y):
        """Movimiento mejorado con separación"""
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist < 3:
            self.x = target_x
            self.y = target_y
            return True
        
        if dist > 0:
            dx /= dist
            dy /= dist
            
            dx += self.separation_force_x
            dy += self.separation_force_y
            
            total_force = math.hypot(dx, dy)
            if total_force > 0:
                dx /= total_force
                dy /= total_force
            
            move_dist = min(self.speed, dist)
            self.x += move_dist * dx
            self.y += move_dist * dy
        
        return dist < 5

    def update(self, world):
        """Actualización del vehículo"""
        if not self.alive:
            return
        
        # Aplicar separación
        self.apply_separation(world.vehicles)
        
        # Verificar colisiones
        self.check_mine_collision(world)
        if not self.alive:
            return
        
        # Si está en retorno forzado (fin del juego)
        if self.forced_return:
            bx, by = self.base_position
            dist_to_base = self.distance_to_point(bx, by)
            
            if dist_to_base < 20:
                # Llegó a la base
                if len(self.cargo) > 0:
                    delivered_value = sum(item.value for item in self.cargo)
                    self.score += delivered_value
                self.cargo.clear()
                self.at_base = True
                # Ya no se mueve más
                return
            else:
                # Moverse hacia la base
                self.move_towards(bx, by)
                return
        
        # Verificar retorno normal
        if self.returning_to_base:
            bx, by = self.base_position
            dist_to_base = self.distance_to_point(bx, by)
            
            if dist_to_base < 20:
                if len(self.cargo) > 0:
                    delivered_value = sum(item.value for item in self.cargo)
                    self.score += delivered_value
                
                self.cargo.clear()
                self.returning_to_base = False
                self.at_base = True
                self.trips_left = self.max_trips
                return
            else:
                self.at_base = False
        
        # Ejecutar estrategia
        if self.strategy:
            action = self.strategy.decide(self, world)
            self.execute_action(action, world)

    def force_return_to_base(self):
        """Fuerza el retorno a la base (fin del juego)"""
        self.forced_return = True
        self.returning_to_base = False

    def execute_action(self, action, world):
        """Ejecuta acción de la estrategia"""
        if not action or "type" not in action:
            return

        action_type = action["type"]
        target = action.get("target")

        if action_type == "move" and target:
            tx, ty = target
            self.move_towards(tx, ty)
            self.try_collect_nearby(world)

        elif action_type == "return_to_base":
            self.returning_to_base = True
            bx, by = self.base_position
            self.move_towards(bx, by)

        elif action_type == "collect" and target:
            self.move_towards(target.x, target.y)
            if self.distance_to(target) < 15:
                self.collect(target, world)

    def try_collect_nearby(self, world):
        """Intenta recoger recursos cercanos"""
        for resource in world.resources[:]:
            if self.distance_to(resource) < 15:
                if resource.type in self.allowed_cargo:
                    self.collect(resource, world)
                    break

    def collect(self, resource, world):
        """Recoge un recurso"""
        if resource.type not in self.allowed_cargo:
            return
        
        if resource not in world.resources:
            return
        
        self.cargo.append(resource)
        world.remove_resource(resource)
        
        if self.vehicle_type in ["moto", "auto"]:
            self.trips_left -= 1
            self.returning_to_base = True

    def check_mine_collision(self, world):
        """Verifica colisión con minas"""
        if not self.alive:
            return

        for mine in world.mines:
            if not mine.active:
                continue
            
            mine_center_x = mine.x + mine.size / 2
            mine_center_y = mine.y + mine.size / 2
            
            if mine.type in ["O1", "O2", "G1"]:
                dist = math.hypot(self.x - mine_center_x, self.y - mine_center_y)
                if dist <= mine.radius:
                    self.die()
                    return
            
            elif mine.type == "T1":
                if (abs(self.y - mine_center_y) <= 2 and 
                    abs(self.x - mine_center_x) <= mine.radius):
                    self.die()
                    return
            
            elif mine.type == "T2":
                if (abs(self.x - mine_center_x) <= 2 and 
                    abs(self.y - mine_center_y) <= mine.radius):
                    self.die()
                    return

    def die(self):
        """Destruye el vehículo"""
        self.alive = False
        self.cargo.clear()
        
    def draw(self, screen):
        """Dibuja el vehículo (sin rotación)"""
        if not self.alive:
            return
        
        # Dibujar sprite centrado (SIN ROTACIÓN)
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
        self.speed = 2.5

class Moto(Vehicle):
    def __init__(self, id, x, y, base_position, color):
        super().__init__(id, x, y, base_position, "moto", 1, ["person"], color)
        self.speed = 3.5

class Camion(Vehicle):
    def __init__(self, id, x, y, base_position, color):
        super().__init__(id, x, y, base_position, "camion", 3,
                         ["person", "clothes", "food", "medicine", "weapons"], color)
        self.speed = 1.8

class Auto(Vehicle):
    def __init__(self, id, x, y, base_position, color):
        super().__init__(id, x, y, base_position, "auto", 1,
                         ["person", "clothes", "food", "medicine"], color)
        self.speed = 2.2