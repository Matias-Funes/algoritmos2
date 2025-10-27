from . import constants
import pygame
from .elements import Tree, Person, Merchandise, Mine
import random 
import os
import math

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # grid: 0 libre, 1 árbol, 2 persona, 3 mercancía, 4 mina
        self.grid = [[0 for _ in range(constants.GRID_WIDTH)] for _ in range(constants.GRID_HEIGHT)]

        # cargar imagen de césped
        grass_path = os.path.join("assets", "images", "objects", "Grass.png")
        try:
            self.grass_image = pygame.image.load(grass_path).convert()
            self.grass_image = pygame.transform.scale(self.grass_image, (constants.TILE, constants.TILE))
        except Exception:
            self.grass_image = pygame.Surface((constants.TILE, constants.TILE))
            self.grass_image.fill((50, 150, 50))

        # Crear árboles
        self.trees = []
        for _ in range(constants.NUM_TREES):
            attempts = 0
            while attempts < 200:
                gx = random.randint(0, constants.GRID_WIDTH - 1)
                gy = random.randint(0, constants.GRID_HEIGHT - 1)
                attempts += 1
                if self.grid[gy][gx] == 0:
                    self.grid[gy][gx] = 1
                    px, py = self.cell_to_pixel(gx, gy)
                    self.trees.append(Tree(px, py))
                    break

        # Generar personas
        self.people = []
        for _ in range(constants.NUM_PEOPLE):
            attempts = 0
            while attempts < 200:
                gx = random.randint(0, constants.GRID_WIDTH - 1)
                gy = random.randint(0, constants.GRID_HEIGHT - 1)
                attempts += 1
                if self.grid[gy][gx] == 0:
                    self.grid[gy][gx] = 2
                    px, py = self.cell_to_pixel(gx, gy)
                    self.people.append(Person(px, py))
                    break

        # Generar mercancías
        self.merch = []
        for kind, cnt in constants.MERCH_COUNTS.items():
            for _ in range(cnt):
                attempts = 0
                while attempts < 200:
                    gx = random.randint(0, constants.GRID_WIDTH - 1)
                    gy = random.randint(0, constants.GRID_HEIGHT - 1)
                    attempts += 1
                    if self.grid[gy][gx] == 0:
                        self.grid[gy][gx] = 3
                        px, py = self.cell_to_pixel(gx, gy)
                        self.merch.append(Merchandise(px, py, kind))
                        break

        # Inicializar minas
        self.mines = []
        self.init_mines()

        # Lista unificada de recursos para las estrategias
        self.resources = []
        self.update_resources_list()

        # Lista de vehículos (se asigna desde game_engine)
        self.vehicles = []
    
    def update_resources_list(self):
        """Actualiza la lista unificada de recursos"""
        self.resources = []
        
        # Convertir mercancías
        for m in self.merch:
            m.type = m.kind
            m.value = constants.MERCH_POINTS.get(m.kind, 10)
            self.resources.append(m)
        
        # Convertir personas
        for p in self.people:
            p.type = "person"
            p.value = constants.POINTS_PERSON
            self.resources.append(p)

    def remove_resource(self, resource):
        """Remueve un recurso del mundo"""
        if resource in self.resources:
            self.resources.remove(resource)
        
        if resource in self.merch:
            self.merch.remove(resource)
            # Actualizar grid
            gx, gy = self.pixel_to_cell(resource.x, resource.y)
            if 0 <= gx < constants.GRID_WIDTH and 0 <= gy < constants.GRID_HEIGHT:
                self.grid[gy][gx] = 0
        
        if resource in self.people:
            self.people.remove(resource)
            # Actualizar grid
            gx, gy = self.pixel_to_cell(resource.x, resource.y)
            if 0 <= gx < constants.GRID_WIDTH and 0 <= gy < constants.GRID_HEIGHT:
                self.grid[gy][gx] = 0

    def random_position(self):
        """Devuelve una posición aleatoria válida en píxeles"""
        for _ in range(100):
            gx = random.randint(0, constants.GRID_WIDTH - 1)
            gy = random.randint(0, constants.GRID_HEIGHT - 1)
            if self.is_walkable(gx, gy):
                return self.cell_to_pixel(gx, gy)
        # Fallback: centro del mapa
        return (self.width // 2, self.height // 2)

    def find_nearest_enemy(self, vehicle):
        """Busca el vehículo enemigo más cercano"""
        enemies = [v for v in self.vehicles if v is not vehicle and v.alive]
        if not enemies:
            return None
        
        nearest = min(enemies, key=lambda e: math.hypot(vehicle.x - e.x, vehicle.y - e.y))
        return nearest
    
    def init_mines(self):
        """Inicializa las minas en posiciones aleatorias"""
        self.mines.clear()
        
        for mine_type, count in constants.MINES_COUNT.items():
            for _ in range(count):
                attempts = 0
                while attempts < 200:
                    gx = random.randint(0, constants.GRID_WIDTH - 1)
                    gy = random.randint(0, constants.GRID_HEIGHT - 1)
                    
                    if self.grid[gy][gx] != 0:
                        attempts += 1
                        continue
                
                    px, py = self.cell_to_pixel(gx, gy)
                
                    # Verificar distancia a otras minas
                    too_close = False
                    for mine in self.mines:
                        if math.hypot(px - mine.x, py - mine.y) < constants.TILE:
                            too_close = True
                            break
                        
                    if not too_close:
                        self.mines.append(Mine(px, py, mine_type))
                        self.grid[gy][gx] = 4
                        break
                    
                    attempts += 1
                    
    def update_g1_mines(self):
        """Actualiza minas dinámicas G1"""
        for mine in self.mines:
            if mine.type == "G1":
                mine.update()

    def relocate_g1_mines(self):
        """Reubica minas G1"""
        for mine in self.mines:
            if mine.type == "G1":
                gx_old, gy_old = self.pixel_to_cell(mine.x, mine.y)
                if 0 <= gx_old < constants.GRID_WIDTH and 0 <= gy_old < constants.GRID_HEIGHT:
                    self.grid[gy_old][gx_old] = 0

                attempts = 0
                while attempts < 200:
                    gx = random.randint(0, constants.GRID_WIDTH - 1)
                    gy = random.randint(0, constants.GRID_HEIGHT - 1)
                    if self.grid[gy][gx] == 0:
                        mine.x, mine.y = self.cell_to_pixel(gx, gy)
                        self.grid[gy][gx] = 4
                        break
                    attempts += 1

    def pixel_to_cell(self, x, y):
        """Convierte píxeles a coordenadas de celda"""
        return int(x) // constants.TILE, int(y) // constants.TILE

    def cell_to_pixel(self, gx, gy):
        """Convierte celda a píxeles (esquina superior izquierda)"""
        return gx * constants.TILE, gy * constants.TILE

    def is_walkable(self, gx, gy):
        """Verifica si una celda es caminable"""
        if gx < 0 or gy < 0 or gx >= constants.GRID_WIDTH or gy >= constants.GRID_HEIGHT:
            return False
        return self.grid[gy][gx] in (0, 2, 3, 4)

    def get_neighbors(self, gx, gy):
        """Obtiene celdas adyacentes válidas"""
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in dirs:
            nx, ny = gx + dx, gy + dy
            if 0 <= nx < constants.GRID_WIDTH and 0 <= ny < constants.GRID_HEIGHT and self.is_walkable(nx, ny):
                yield nx, ny

    def draw(self, screen):
        """Dibuja el mundo"""
        # Fondo
        for gy in range(constants.GRID_HEIGHT):
            for gx in range(constants.GRID_WIDTH):
                px, py = self.cell_to_pixel(gx, gy)
                screen.blit(self.grass_image, (px, py))

        # Objetos
        for tree in self.trees:
            tree.draw(screen)
        for person in self.people:
            person.draw(screen)
        for m in self.merch:
            m.draw(screen)
        for mine in self.mines:
            mine.draw(screen)

    def draw_team_stats(self, screen, vehicles, position="left", team_name="Equipo"):
        """Dibuja estadísticas del equipo"""
        font_title = pygame.font.SysFont(None, 20, bold=True)
        font = pygame.font.SysFont(None, 17)
        
        if position == "left":
            x, y = 10, 10
        else:
            x, y = constants.WIDTH - 220, 10

        # Calcular totales
        total_score = sum(v.score for v in vehicles)
        alive_count = sum(1 for v in vehicles if v.alive)
        total_cargo = sum(len(v.cargo) for v in vehicles)
        
        # Contar por tipo
        jeeps_alive = sum(1 for v in vehicles if v.vehicle_type == "jeep" and v.alive)
        motos_alive = sum(1 for v in vehicles if v.vehicle_type == "moto" and v.alive)
        camiones_alive = sum(1 for v in vehicles if v.vehicle_type == "camion" and v.alive)
        autos_alive = sum(1 for v in vehicles if v.vehicle_type == "auto" and v.alive)

        # Dibujar panel con fondo semi-transparente
        panel_surf = pygame.Surface((210, 180), pygame.SRCALPHA)
        panel_surf.fill((0, 0, 0, 180))
        screen.blit(panel_surf, (x-5, y-5))

        lines = [
            (f"{team_name}", font_title, constants.WHITE),
            ("", font, constants.WHITE),
            (f"PUNTOS: {total_score}", font, (255, 255, 0)),
            (f"Vivos: {alive_count}/10", font, constants.WHITE),
            (f"Carga actual: {total_cargo}", font, (150, 255, 150)),
            ("", font, constants.WHITE),
            (f"Jeeps: {jeeps_alive}/3", font, (200, 200, 200)),
            (f"Motos: {motos_alive}/2", font, (200, 200, 200)),
            (f"Camiones: {camiones_alive}/2", font, (200, 200, 200)),
            (f"Autos: {autos_alive}/3", font, (200, 200, 200)),
        ]

        for text, font_type, color in lines:
            if text:
                surf = font_type.render(text, True, color)
                screen.blit(surf, (x, y))
            y += 20