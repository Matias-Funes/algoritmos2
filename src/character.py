from . import constants
from .pathfinding import a_star
import pygame
import os
import math

# personaje controlado por el jugador
class Character:
    def __init__(self, x, y):
        # Alinea la posición inicial a la cuadrícula: convierte píxeles a celda (división entera) y vuelve a píxeles. Así el personaje queda en la esquina superior izquierda de una celda completa.
        self.x = (x // constants.TILE) * constants.TILE
        self.y = (y // constants.TILE) * constants.TILE
        #Diccionario que guarda el estado del jugador: puntos, recursos recolectados y cantidad de personas rescatadas.
        self.inventory = {"points": 0, "clothes": 0, "food": 0, "medicine": 0, "rescued": 0}
        #cargar imagen y escalarla
        image_path = os.path.join("assets", "images", "characters", "autoRojo.png")
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (constants.PLAYER, constants.PLAYER))
        except Exception:
            self.image = pygame.Surface((constants.PLAYER, constants.PLAYER), pygame.SRCALPHA)
            self.image.fill((200, 0, 0))
        #Guarda el tamaño del sprite (ancho). Útil para posicionar/colisiones
        self.size = self.image.get_width()
        self.path = []  # lista de celdas (gx,gy) para seguir
        self._move_speed = 4  # pixels por frame para interpolación

        self.alive = True
        self.respawn_point = (x, y)

    #copia los píxeles de una Surface origen (self.image) sobre otra Surface destino (screen) en la posición dada.
    def draw(self, screen):
        #self.image es una Surface (cargada con pygame.image.load o creada como fallback)
        # screen.blit proviene de Pygame: blit es un método de la clase pygame.Surface.
        screen.blit(self.image, (self.x, self.y))

    def move_to_cell(self, gx, gy, world):
        # Calcula la celda actual del personaje a partir de su posición en píxeles (self.x, self.y).
        start = world.pixel_to_cell(self.x, self.y)
        #Define la celda destino como la tupla goal
        goal = (gx, gy)
        # llama al algoritmo A* para obtener el camino desde start hasta goal
        path = a_star(start, goal, world)
        if path:
            # Si A* devolvió una ruta, guarda en self.path la ruta excepto la primera celda (path[1:]).
            #Se excluye la primera celda porque es la celda actual (start); así la lista contiene solo los pasos que hay que seguir.
            self.path = path[1:]

    #Actualiza la posición del personaje y maneja la recolección de objetos y rescate de personas.
    def update(self, world):

        if not self.alive:
            return

        # Primero actualizar movimiento
        if self.path:
            next_cell = self.path[0]
            target_x, target_y = world.cell_to_pixel(*next_cell)
            dx = target_x - self.x # Diferencia en X
            dy = target_y - self.y # Diferencia en Y
            #Calcula la distancia al objetivo usando Pitágoras
            dist = math.hypot(dx, dy) # Distancia euclidiana
            
            if dist <= self._move_speed:
                # Si estamos lo suficientemente cerca, snap a la posición
                self.x, self.y = target_x, target_y
                self.path.pop(0) # Quita esta celda de la ruta
            else:
                # Movimiento suave hacia el objetivo
                self.x += (dx / dist) * self._move_speed
                self.y += (dy / dist) * self._move_speed

        # Convierte la posición actual en píxeles a coordenadas de celda
        current_cell = world.pixel_to_cell(self.x, self.y)

        # Verificar colisiones con minas
        self.check_mine_collision(world)
        
        # Revisar mercancías
        for merch in world.merch[:]:
            merch_cell = world.pixel_to_cell(merch.x, merch.y)
            if current_cell == merch_cell:
                # Añadir al inventario
                self.inventory[merch.kind] += 1
                # Sumar puntos según tipo
                self.inventory["points"] += constants.MERCH_POINTS[merch.kind]
                # Remover mercancía
                world.merch.remove(merch)
                # Actualizar grid
                world.grid[merch_cell[1]][merch_cell[0]] = 0
        
        # Revisar personas
        for person in world.people[:]:
            person_cell = world.pixel_to_cell(person.x, person.y)
            if current_cell == person_cell:
                # Verificar si tenemos recursos suficientes
                if (self.inventory["clothes"] >= 1 and 
                    self.inventory["food"] >= 1 and 
                    self.inventory["medicine"] >= 1):
                    # Consumir recursos
                    self.inventory["clothes"] -= 1
                    self.inventory["food"] -= 1
                    self.inventory["medicine"] -= 1
                    # Sumar puntos y contador de rescatados
                    self.inventory["points"] += constants.POINTS_PERSON
                    self.inventory["rescued"] += 1
                    # Remover persona y actualizar grid
                    world.people.remove(person)
                    world.grid[person_cell[1]][person_cell[0]] = 0
                    print(f"¡Persona rescatada! Puntos: {self.inventory['points']}")  # Debug

    def check_mine_collision(self, world):
        if not self.alive:
            return

        # Rectángulo del personaje
        char_rect = pygame.Rect(self.x, self.y, self.size, self.size)
    
        for mine in world.mines:
            if not mine.active:
                continue
            
            # Mina circular u otra forma
            if mine.type in ["O1", "O2", "G1"]:
                mine_center = (mine.x + mine.size/2, mine.y + mine.size/2)
                radius = constants.MINE_TYPES[mine.type]["radius"]
                # Colisión entre rectángulo y círculo
                closest_x = max(char_rect.left, min(mine_center[0], char_rect.right))
                closest_y = max(char_rect.top, min(mine_center[1], char_rect.bottom))
                distance = math.hypot(closest_x - mine_center[0], closest_y - mine_center[1])
                if distance <= radius:
                    world.detonate_mine(mine)
                    self.die()
                    break
            elif mine.type == "T1":
                mine_rect = pygame.Rect(mine.x - constants.MINE_TYPES[mine.type]["radius"], 
                                        mine.y - 2, 
                                        constants.MINE_TYPES[mine.type]["radius"]*2, 4)
                if char_rect.colliderect(mine_rect):
                    self.die()
                    break
            elif mine.type == "T2":
                mine_rect = pygame.Rect(mine.x - 2,
                                        mine.y - constants.MINE_TYPES[mine.type]["radius"],
                                        4,
                                        constants.MINE_TYPES[mine.type]["radius"]*2)
                if char_rect.colliderect(mine_rect):
                    self.die()
                    break
                
    def die(self):
        """Maneja la muerte del personaje"""
        self.alive = False
        self.inventory = {"points": 0, "clothes": 0, "food": 0, "medicine": 0, "rescued": 0}
        # Aquí podrías agregar efectos visuales, sonido, etc.
        
    def respawn(self):
        """Revive al personaje en su punto inicial"""
        self.alive = True
        self.x, self.y = self.respawn_point
        self.path = []
        


