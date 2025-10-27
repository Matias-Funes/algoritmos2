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
        
        # Tamaño según tipo de vehículo
        self.size = self._get_vehicle_size()
        
        # Crear sprite visual
        self.image = self._create_vehicle_sprite()
        
    def _get_vehicle_size(self):
        """Retorna el tamaño del vehículo según su tipo"""
        sizes = {
            "jeep": 25,
            "moto": 18,
            "camion": 32,
            "auto": 22
        }
        return sizes.get(self.vehicle_type, 20)
    
    def _create_vehicle_sprite(self):
        """Crea el sprite visual del vehículo"""
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        if self.vehicle_type == "jeep":
            # Jeep: rectángulo con ruedas
            pygame.draw.rect(surface, self.color, (3, 5, self.size-6, self.size-10))
            pygame.draw.rect(surface, (0, 0, 0), (3, 5, self.size-6, self.size-10), 2)
            # Ventanas
            pygame.draw.rect(surface, (100, 150, 200), (7, 8, 5, 5))
            pygame.draw.rect(surface, (100, 150, 200), (self.size-12, 8, 5, 5))
            # Ruedas
            pygame.draw.circle(surface, (40, 40, 40), (5, 5), 3)
            pygame.draw.circle(surface, (40, 40, 40), (self.size-5, 5), 3)
            pygame.draw.circle(surface, (40, 40, 40), (5, self.size-5), 3)
            pygame.draw.circle(surface, (40, 40, 40), (self.size-5, self.size-5), 3)
            
        elif self.vehicle_type == "moto":
            # Moto: forma delgada con 2 ruedas
            pygame.draw.ellipse(surface, self.color, (5, 3, self.size-10, self.size-6))
            pygame.draw.ellipse(surface, (0, 0, 0), (5, 3, self.size-10, self.size-6), 2)
            # Ruedas
            pygame.draw.circle(surface, (40, 40, 40), (self.size//2, 5), 3)
            pygame.draw.circle(surface, (40, 40, 40), (self.size//2, self.size-5), 3)
            # Manillar
            pygame.draw.line(surface, (80, 80, 80), (self.size//2-3, 8), (self.size//2+3, 8), 2)
            
        elif self.vehicle_type == "camion":
            # Camión: rectángulo grande con cabina
            pygame.draw.rect(surface, self.color, (2, 8, self.size-4, self.size-12))
            pygame.draw.rect(surface, self.color, (4, 3, 10, 8))  # Cabina
            pygame.draw.rect(surface, (0, 0, 0), (2, 8, self.size-4, self.size-12), 2)
            pygame.draw.rect(surface, (0, 0, 0), (4, 3, 10, 8), 2)
            # Ventanas cabina
            pygame.draw.rect(surface, (100, 150, 200), (6, 5, 6, 4))
            # Ruedas
            pygame.draw.circle(surface, (40, 40, 40), (8, self.size-3), 4)
            pygame.draw.circle(surface, (40, 40, 40), (self.size-8, self.size-3), 4)
            pygame.draw.circle(surface, (40, 40, 40), (self.size//2, self.size-3), 4)
            
        elif self.vehicle_type == "auto":
            # Auto: sedan clásico
            pygame.draw.ellipse(surface, self.color, (2, 6, self.size-4, self.size-12))
            pygame.draw.rect(surface, self.color, (5, 3, self.size-10, 8))  # Techo
            pygame.draw.rect(surface, (0, 0, 0), (2, 6, self.size-4, self.size-12), 2)
            pygame.draw.rect(surface, (0, 0, 0), (5, 3, self.size-10, 8), 2)
            # Ventanas
            pygame.draw.rect(surface, (100, 150, 200), (7, 5, 4, 4))
            pygame.draw.rect(surface, (100, 150, 200), (self.size-11, 5, 4, 4))
            # Ruedas
            pygame.draw.circle(surface, (40, 40, 40), (6, self.size-4), 3)
            pygame.draw.circle(surface, (40, 40, 40), (self.size-6, self.size-4), 3)
        
        return surface

    def distance_to(self, obj):
        """Calcula distancia euclidiana a otro objeto"""
        return math.hypot(self.x - obj.x, self.y - obj.y)

    def distance_to_point(self, x, y):
        """Distancia a un punto específico"""
        return math.hypot(self.x - x, self.y - y)

    def move_towards(self, target_x, target_y):
        """Mueve el vehículo hacia una posición objetivo - MEJORADO para evitar vibración"""
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        
        # Si está muy cerca del objetivo, detener movimiento
        if dist < 2:
            self.x = target_x
            self.y = target_y
            return True
        
        if dist > 0:
            move_dist = min(self.speed, dist)
            self.x += move_dist * (dx / dist)
            self.y += move_dist * (dy / dist)
        
        return dist < 3  # Retorna True si llegó

    def update(self, world):
        """Actualiza el estado del vehículo"""
        if not self.alive:
            return
        
        # Verificar colisión con minas
        self.check_mine_collision(world)
        if not self.alive:
            return
        
        # Verificar si llegó a la base
        if self.returning_to_base:
            bx, by = self.base_position
            dist_to_base = self.distance_to_point(bx, by)
            
            if dist_to_base < 15:
                # Entregó la carga exitosamente
                if len(self.cargo) > 0:
                    # Sumar puntos solo al entregar
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

    def execute_action(self, action, world):
        """Ejecuta la acción decidida por la estrategia"""
        if not action or "type" not in action:
            return

        action_type = action["type"]
        target = action.get("target")

        if action_type == "move" and target:
            tx, ty = target
            self.move_towards(tx, ty)
            # Verificar recolección si está cerca
            self.try_collect_nearby(world)

        elif action_type == "return_to_base":
            self.returning_to_base = True
            bx, by = self.base_position
            self.move_towards(bx, by)

        elif action_type == "collect" and target:
            # Moverse hacia el recurso
            arrived = self.move_towards(target.x, target.y)
            # Intentar recogerlo si está cerca
            if self.distance_to(target) < 12:
                self.collect(target, world)

    def try_collect_nearby(self, world):
        """Intenta recoger recursos cercanos"""
        for resource in world.resources[:]:
            if self.distance_to(resource) < 12:
                if resource.type in self.allowed_cargo:
                    self.collect(resource, world)
                    break

    def collect(self, resource, world):
        """Recoge un recurso si es permitido"""
        if resource.type not in self.allowed_cargo:
            return
        
        if resource not in world.resources:
            return  # Ya fue recogido
        
        # Agregar al cargo (NO sumar puntos aún)
        self.cargo.append(resource)
        
        # Remover del mundo
        world.remove_resource(resource)
        
        # Decrementar viajes si aplica
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
            
            # Calcular centro de la mina
            mine_center_x = mine.x + mine.size / 2
            mine_center_y = mine.y + mine.size / 2
            
            if mine.type in ["O1", "O2", "G1"]:
                # Mina circular
                dist = math.hypot(self.x - mine_center_x, self.y - mine_center_y)
                if dist <= mine.radius:
                    self.die()
                    return
            
            elif mine.type == "T1":
                # Mina horizontal
                if (abs(self.y - mine_center_y) <= 2 and 
                    abs(self.x - mine_center_x) <= mine.radius):
                    self.die()
                    return
            
            elif mine.type == "T2":
                # Mina vertical
                if (abs(self.x - mine_center_x) <= 2 and 
                    abs(self.y - mine_center_y) <= mine.radius):
                    self.die()
                    return

    def die(self):
        """Destruye el vehículo y pierde toda su carga"""
        self.alive = False
        self.cargo.clear()
        
    def draw(self, screen):
        """Dibuja el vehículo en pantalla"""
        if not self.alive:
            return
        
        # Dibujar sprite centrado
        screen.blit(self.image, (int(self.x - self.size//2), int(self.y - self.size//2)))
        
        # Indicador de carga
        if len(self.cargo) > 0:
            cargo_color = (255, 255, 0)  # Amarillo
            pygame.draw.circle(screen, cargo_color, (int(self.x), int(self.y-self.size//2-5)), 3)
            font = pygame.font.SysFont(None, 14)
            text = font.render(str(len(self.cargo)), True, (255, 255, 255))
            screen.blit(text, (int(self.x-3), int(self.y-self.size//2-8)))

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