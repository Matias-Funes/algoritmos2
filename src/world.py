from . import constants
import pygame
from .elements import Tree, Person, Merchandise, Mine
import random 
import os
import math
from . import pathfinding


class World:
    def __init__(self, width, height):
        self.width = width
        self.height = constants.GAME_WORLD_HEIGHT

        # Definir las áreas de las bases para evitar que se generen objetos en ellas
        self.base1_pos = (50, constants.GAME_WORLD_HEIGHT // 2)
        self.base2_pos = (constants.WIDTH - 50, constants.GAME_WORLD_HEIGHT // 2)
        self.base_radius = 50  # Radio de la base en píxeles
        
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
                if self.grid[gy][gx] == 0 and not self.is_in_base_area(gx, gy):
                    self.grid[gy][gx] = 1
                    px, py = self.cell_to_pixel(gx, gy)
                    self.trees.append(Tree(px, py))
                    break
        # Inicializamos las listas como vacías
        self.people = []
        self.merch = []
        self.mines = []
        self.resources = []
        self.vehicles = []

    # Funcion para verificar si una celda esta dentro de alguna base 
    def is_in_base_area(self, gx, gy):
        """Verifica si una celda de la grid está dentro de alguna base."""
        # Calculamos el centro de la celda en píxeles
        px, py = self.cell_to_pixel(gx, gy)
        px_center = px + constants.TILE // 2
        py_center = py + constants.TILE // 2
        
        # Comprobamos la distancia a los centros de las bases
        dist_base1 = math.hypot(px_center - self.base1_pos[0], py_center - self.base1_pos[1])
        dist_base2 = math.hypot(px_center - self.base2_pos[0], py_center - self.base2_pos[1])
        
        # Si está dentro del radio de CUALQUIER base, es verdadero
        if dist_base1 <= self.base_radius or dist_base2 <= self.base_radius:
            return True
        return False
    
    def initialize_map_elements(self):
        """
        Limpia y (re)genera todas las minas, personas y mercancías.
        """
        print("Generando nuevos elementos en el mapa...")
        
        #Limpiar listas de objetos
        self.people.clear()
        self.merch.clear()
        self.mines.clear()
        self.resources.clear()
        
        #Resetear la grid (borrar todo excepto los árboles '1')
        for y in range(constants.GRID_HEIGHT):
            for x in range(constants.GRID_WIDTH):
                if self.grid[y][x] != 1: # Si no es un árbol
                    self.grid[y][x] = 0  # Limpiar la celda
                    
        #Generar personas 
        for _ in range(constants.NUM_PEOPLE):
            attempts = 0
            while attempts < 200:
                gx = random.randint(0, constants.GRID_WIDTH - 1)
                gy = random.randint(0, constants.GRID_HEIGHT - 1)
                attempts += 1
                if self.grid[gy][gx] == 0 and not self.is_in_base_area(gx, gy):
                    self.grid[gy][gx] = 2
                    px, py = self.cell_to_pixel(gx, gy)
                    self.people.append(Person(px, py))
                    break

        # Generar mercancias 
        for kind, cnt in constants.MERCH_COUNTS.items():
            for _ in range(cnt):
                attempts = 0
                while attempts < 200:
                    gx = random.randint(0, constants.GRID_WIDTH - 1)
                    gy = random.randint(0, constants.GRID_HEIGHT - 1)
                    attempts += 1
                    if self.grid[gy][gx] == 0 and not self.is_in_base_area(gx, gy):
                        self.grid[gy][gx] = 3
                        px, py = self.cell_to_pixel(gx, gy)
                        self.merch.append(Merchandise(px, py, kind))
                        break

        # Generar minas 
        self.init_mines()

        # Actualizar recursos 
        self.update_resources_list()
        
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

    #Guardar 
    def get_state(self):
        """Recopila el estado de todos los elementos del mundo."""
        return {
            "people": [p.get_state() for p in self.people],
            "merchandise": [m.get_state() for m in self.merch],
            "mines": [m.get_state() for m in self.mines]
        }
    
    #Cargar
    def load_state(self, world_data):
        """Limpia el mundo y lo recrea a partir de los datos guardados."""
        
        # 1. Limpiar todas las listas de objetos
        self.people.clear()
        self.merch.clear()
        self.mines.clear()
        self.resources.clear()
        
        # 2. Recrear Personas
        for person_data in world_data.get('people', []):
            p = Person(person_data['x'], person_data['y'])
            # (Podemos añadir más atributos si los guardamos en el futuro)
            self.people.append(p)
            
        # 3. Recrear Mercancías
        for merch_data in world_data.get('merchandise', []):
            m = Merchandise(merch_data['x'], merch_data['y'], merch_data['kind'])
            self.merch.append(m)

        # 4. Recrear Minas
        for mine_data in world_data.get('mines', []):
            m = Mine(mine_data['x'], mine_data['y'], mine_data['type'])
            # Restaurar el estado de la mina (temporizador, actividad)
            m.active = mine_data.get('active', True)
            m.toggle_timer = mine_data.get('toggle_timer', 0)
            self.mines.append(m)
            
        # 5. Reconstruir la lista de recursos unificada
        self.update_resources_list()
        
        # 6. Reconstruir la grid de navegación
        self._rebuild_grid()

    def _rebuild_grid(self):
        """
        Limpia y reconstruye la grid de navegación basada en los objetos cargados.
        """
        # 1. Resetear la grid (borrar todo excepto los árboles '1')
        for y in range(constants.GRID_HEIGHT):
            for x in range(constants.GRID_WIDTH):
                if self.grid[y][x] != 1: # Si no es un árbol
                    self.grid[y][x] = 0  # Limpiar la celda
        
        # 2. Repoblar la grid con los objetos cargados
        for p in self.people:
            gx, gy = self.pixel_to_cell(p.x, p.y)
            if 0 <= gx < constants.GRID_WIDTH and 0 <= gy < constants.GRID_HEIGHT:
                self.grid[gy][gx] = 2
        
        for m in self.merch:
            gx, gy = self.pixel_to_cell(m.x, m.y)
            if 0 <= gx < constants.GRID_WIDTH and 0 <= gy < constants.GRID_HEIGHT:
                self.grid[gy][gx] = 3
                
        for m in self.mines:
            gx, gy = self.pixel_to_cell(m.x, m.y)
            if 0 <= gx < constants.GRID_WIDTH and 0 <= gy < constants.GRID_HEIGHT:
                self.grid[gy][gx] = 4
    
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
                    
                    if self.grid[gy][gx] != 0 or self.is_in_base_area(gx, gy):
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
        """
        Actualiza minas dinámicas G1.
        Devuelve True si ALGUNA mina cambió de estado.
        """
        a_mine_changed = False
        for mine in self.mines:
            if mine.type == "G1":
                if mine.update(): # mine.update() ahora devuelve True si cambió
                    a_mine_changed = True
        return a_mine_changed

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
                    if self.grid[gy][gx] == 0 and not self.is_in_base_area(gx, gy):
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
        """
        Verifica si una celda es caminable para el ALGORITMO A*.
        """
        if gx < 0 or gy < 0 or gx >= constants.GRID_WIDTH or gy >= constants.GRID_HEIGHT:
            return False # Fuera del mapa
            
        # Es caminable si es 0 (suelo), 2 (persona) o 3 (mercancía).
        # NO es caminable si es 1 (árbol) o 4 (mina).
        return self.grid[gy][gx] in (0, 2, 3)

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

    def draw_premium_hud(self, screen, player1_vehicles, player2_vehicles, game_time):
        """HUD moderno y mejorado"""
        import pygame
        
        # Función auxiliar para paneles con sombra
        def draw_panel(surface, x, y, width, height, color=(30, 30, 40)):
            # Sombra
            shadow_surf = pygame.Surface((width + 4, height + 4), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 100), (2, 2, width, height), border_radius=8)
            surface.blit(shadow_surf, (x - 2, y - 2))
            
            # Panel
            panel_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(panel_surf, color + (230,), (0, 0, width, height), border_radius=8)
            pygame.draw.rect(panel_surf, (255, 255, 255, 50), (0, 0, width, height), 2, border_radius=8)
            surface.blit(panel_surf, (x, y))
        
        font_title = pygame.font.SysFont("Arial", 18, bold=True)
        font_normal = pygame.font.SysFont("Arial", 14)
        font_small = pygame.font.SysFont("Arial", 12)
        
        # Calcular estadísticas
        p1_score = sum(v.score for v in player1_vehicles)
        p1_alive = sum(1 for v in player1_vehicles if v.alive)
        p1_cargo = sum(len(v.cargo) for v in player1_vehicles)
        
        p2_score = sum(v.score for v in player2_vehicles)
        p2_alive = sum(1 for v in player2_vehicles if v.alive)
        p2_cargo = sum(len(v.cargo) for v in player2_vehicles)
        
        # Panel Jugador 1 (Izquierda)
        panel_width = 200
        panel_height = 160
        draw_panel(screen, 10, 10, panel_width, panel_height, (50, 20, 20))
        
        y = 20
        # Título
        title = font_title.render("JUGADOR 1", True, (255, 150, 150))
        screen.blit(title, (20, y))
        y += 30
        
        # Puntos destacados
        points = font_title.render(f"{p1_score}", True, (255, 215, 0))
        screen.blit(points, (20, y))
        pts_label = font_small.render("puntos", True, (200, 200, 200))
        screen.blit(pts_label, (80, y + 5))
        y += 30
        
        # Progreso
        alive_text = font_normal.render(f"Vivos: {p1_alive}/10", True, (150, 255, 150) if p1_alive > 5 else (255, 150, 150))
        screen.blit(alive_text, (20, y))
        y += 22
        
        # Barra de vivos
        bar_width = panel_width - 40
        pygame.draw.rect(screen, (50, 50, 50), (20, y, bar_width, 8), border_radius=4)
        alive_bar = int(bar_width * (p1_alive / 10))
        color = (100, 255, 100) if p1_alive > 5 else (255, 100, 100)
        pygame.draw.rect(screen, color, (20, y, alive_bar, 8), border_radius=4)
        y += 18
        
        # Carga actual
        cargo_text = font_normal.render(f"Carga: {p1_cargo}", True, (255, 255, 150))
        screen.blit(cargo_text, (20, y))
        y += 20
        
        # Tipos de vehículos con iconos
        types = [
            ("J", sum(1 for v in player1_vehicles if v.vehicle_type == "jeep" and v.alive), 3),
            ("M", sum(1 for v in player1_vehicles if v.vehicle_type == "moto" and v.alive), 2),
            ("C", sum(1 for v in player1_vehicles if v.vehicle_type == "camion" and v.alive), 2),
            ("A", sum(1 for v in player1_vehicles if v.vehicle_type == "auto" and v.alive), 3)
        ]
        
        x_offset = 20
        for icon, alive, total in types:
            color = (150, 255, 150) if alive == total else (255, 200, 100) if alive > 0 else (100, 100, 100)
            text = font_small.render(f"{icon}:{alive}/{total}", True, color)
            screen.blit(text, (x_offset, y))
            x_offset += 45
        
        # Panel Jugador 2 (Derecha)
        draw_panel(screen, constants.WIDTH - panel_width - 10, 10, panel_width, panel_height, (20, 20, 50))
        
        y = 20
        x_base = constants.WIDTH - panel_width
        
        # Título
        title = font_title.render("JUGADOR 2", True, (150, 150, 255))
        screen.blit(title, (x_base, y))
        y += 30
        
        # Puntos
        points = font_title.render(f"{p2_score}", True, (255, 215, 0))
        screen.blit(points, (x_base, y))
        pts_label = font_small.render("puntos", True, (200, 200, 200))
        screen.blit(pts_label, (x_base + 60, y + 5))
        y += 30
        
        # Vivos
        alive_text = font_normal.render(f"Vivos: {p2_alive}/10", True, (150, 255, 150) if p2_alive > 5 else (255, 150, 150))
        screen.blit(alive_text, (x_base, y))
        y += 22
        
        # Barra de vivos
        pygame.draw.rect(screen, (50, 50, 50), (x_base, y, bar_width, 8), border_radius=4)
        alive_bar = int(bar_width * (p2_alive / 10))
        color = (100, 255, 100) if p2_alive > 5 else (255, 100, 100)
        pygame.draw.rect(screen, color, (x_base, y, alive_bar, 8), border_radius=4)
        y += 18
        
        # Carga
        cargo_text = font_normal.render(f"Carga: {p2_cargo}", True, (255, 255, 150))
        screen.blit(cargo_text, (x_base, y))
        y += 20
        
        # Tipos
        types = [
            ("J", sum(1 for v in player2_vehicles if v.vehicle_type == "jeep" and v.alive), 3),
            ("M", sum(1 for v in player2_vehicles if v.vehicle_type == "moto" and v.alive), 2),
            ("C", sum(1 for v in player2_vehicles if v.vehicle_type == "camion" and v.alive), 2),
            ("A", sum(1 for v in player2_vehicles if v.vehicle_type == "auto" and v.alive), 3)
        ]
        
        x_offset = x_base
        for icon, alive, total in types:
            color = (150, 255, 150) if alive == total else (255, 200, 100) if alive > 0 else (100, 100, 100)
            text = font_small.render(f"{icon}:{alive}/{total}", True, color)
            screen.blit(text, (x_offset, y))
            x_offset += 45
        
        # Panel de recursos restantes (en lugar de tiempo)
        resource_panel_width = 240
        resource_panel_x = (constants.WIDTH - resource_panel_width) // 2
        draw_panel(screen, resource_panel_x, 10, resource_panel_width, 55, (40, 40, 50))
        
        # Calcular recursos totales y restantes
        total_resources = 60  # 10 personas + 50 mercancías
        resources_remaining = len(self.resources)
        resources_collected = total_resources - resources_remaining
        
        # Texto de recursos
        resource_color = (150, 255, 150) if resources_remaining > 30 else (255, 200, 100) if resources_remaining > 10 else (255, 100, 100)
        resource_text = font_title.render(f"Recursos: {resources_remaining}/60", True, resource_color)
        screen.blit(resource_text, (resource_panel_x + 20, 18))
        
        # Barra de progreso de recolección
        progress_bar_width = resource_panel_width - 40
        collection_progress = resources_collected / total_resources
        pygame.draw.rect(screen, (50, 50, 50), (resource_panel_x + 20, 45, progress_bar_width, 8), border_radius=4)
        pygame.draw.rect(screen, resource_color, (resource_panel_x + 20, 45, int(progress_bar_width * collection_progress), 8), border_radius=4)
        
        # Mini contador de tiempo transcurrido
        time_elapsed_seconds = game_time // 60
        time_minutes = time_elapsed_seconds // 60
        time_seconds = time_elapsed_seconds % 60
        time_elapsed_text = font_small.render(f"Tiempo: {time_minutes:02d}:{time_seconds:02d}", True, (200, 200, 200))
        screen.blit(time_elapsed_text, (resource_panel_x + resource_panel_width//2 - 35, 32))
        
        # Recursos restantes (mini panel abajo)
        resources_remaining = len(self.resources)
        if resources_remaining > 0:
            mini_panel_width = 150
            mini_panel_x = (constants.WIDTH - mini_panel_width) // 2
            draw_panel(screen, mini_panel_x, constants.GAME_WORLD_HEIGHT - 50, mini_panel_width, 35, (40, 50, 40))
            
            res_text = font_normal.render(f"Recursos: {resources_remaining}", True, (150, 255, 150))
            screen.blit(res_text, (mini_panel_x + 15, constants.GAME_WORLD_HEIGHT - 38))