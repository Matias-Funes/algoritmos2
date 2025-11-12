import pygame
import sys
from .world import World
from . import constants
from .game_states import GameState
import math
from config.strategies.player1_strategies import JeepStrategy, MotoStrategy, CamionStrategy, AutoStrategy
from config.strategies.player2_strategies import AggressiveJeepStrategy, FastMotoStrategy, SupportCamionStrategy, BalancedAutoStrategy
from src.aircraft import Jeep, Moto, Camion, Auto
from .database import GameDatabase
import pickle 
import datetime
import os 
import glob
from .elements import Person, Merchandise, Mine, FireEffect

# Convierte los nombres de string (guardados) de nuevo a Clases (para cargar)
STRATEGY_MAP = {
    # Estrategias del Jugador 1
    "JeepStrategy": JeepStrategy,
    "MotoStrategy": MotoStrategy,
    "CamionStrategy": CamionStrategy,
    "AutoStrategy": AutoStrategy,
    # Estrategias del Jugador 2
    "AggressiveJeepStrategy": AggressiveJeepStrategy,
    "FastMotoStrategy": FastMotoStrategy,
    "SupportCamionStrategy": SupportCamionStrategy,
    "BalancedAutoStrategy": BalancedAutoStrategy
}
# --- FIN DEL MAPA ---

pygame.init()

screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
pygame.display.set_caption("🚁 Simulador de Rescate - Algoritmos II")

# Fuentes mejoradas
FONT_TITLE = pygame.font.SysFont("Arial", 24, bold=True)
FONT_NORMAL = pygame.font.SysFont("Arial", 16)
FONT_SMALL = pygame.font.SysFont("Arial", 14)

def draw_gradient_rect(surface, color1, color2, rect):
    """Dibuja un rectángulo con gradiente"""
    for y in range(rect.height):
        ratio = y / rect.height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(surface, (r, g, b), 
                        (rect.x, rect.y + y), 
                        (rect.x + rect.width, rect.y + y))

def draw_panel(surface, x, y, width, height, color=(30, 30, 40)):
    """Dibuja un panel con bordes redondeados y sombra"""
    # Sombra
    shadow_surf = pygame.Surface((width + 6, height + 6), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 80), (3, 3, width, height), border_radius=10)
    surface.blit(shadow_surf, (x - 3, y - 3))
    
    # Panel principal   
    panel_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, color + (220,), (0, 0, width, height), border_radius=10)
    pygame.draw.rect(panel_surf, (255, 255, 255, 30), (0, 0, width, height), 2, border_radius=10)
    surface.blit(panel_surf, (x, y))

def main():
    frame_history = []
    current_frame_index = -1

    clock = pygame.time.Clock()
    db = GameDatabase()
    # Usamos GAME_WORLD_HEIGHT para inicializar el mundo
    world = World(constants.WIDTH, constants.GAME_WORLD_HEIGHT)

    # Bases con mejor posicionamiento
    base1_x = 50
    # Centramos las bases en el MUNDO, no en la ventana
    base1_y = constants.GAME_WORLD_HEIGHT // 2 
    base2_x = constants.WIDTH - 50
    base2_y = constants.GAME_WORLD_HEIGHT // 2

    # Convertir las posiciones de base de píxeles a coordenadas de celda
    base1_gx = base1_x // constants.TILE
    base1_gy = base1_y // constants.TILE
    base2_gx = base2_x // constants.TILE
    base2_gy = base2_y // constants.TILE

    # ==========================================
    # JUGADOR 1 - ROJO (Izquierda)
    # ==========================================
    player1_vehicles = []
    
    # 3 Jeeps en formación escalonada
    # Los offsets se ajustan para ser en celdas
    for i in range(3):
        jeep_gx_offset = i // 2 # 0, 0, 1
        jeep_gy_offset = (i - 1) # -1, 0, 1
        jeep = Jeep(f"P1_Jeep_{i}", base1_gx + jeep_gx_offset, base1_gy + jeep_gy_offset, 
                   (base1_x, base1_y), (220, 20, 20))
        jeep.strategy = JeepStrategy()
        player1_vehicles.append(jeep)
    
    # 2 Motos adelante
    for i in range(2):
        moto_gy_offset = (i * 2 - 1) # -1, 1
        moto = Moto(f"P1_Moto_{i}", base1_gx + 1, base1_gy + moto_gy_offset, 
                   (base1_x, base1_y), (255, 80, 80))
        moto.strategy = MotoStrategy()
        player1_vehicles.append(moto)
    
    # 2 Camiones atrás
    for i in range(2):
        camion_gy_offset = (i * 2 - 1) # -1, 1
        camion = Camion(f"P1_Camion_{i}", base1_gx - 1, base1_gy + camion_gy_offset, 
                       (base1_x, base1_y), (180, 0, 0))
        camion.strategy = CamionStrategy()
        player1_vehicles.append(camion)
    
    # 3 Autos en V
    # Se definen directamente en coordenadas de celda
    auto_grid_positions = [
        (base1_gx, base1_gy - 1),
        (base1_gx, base1_gy + 1),
        (base1_gx + 1, base1_gy)
    ]
    for i, (agx, agy) in enumerate(auto_grid_positions):
        auto = Auto(f"P1_Auto_{i}", agx, agy, (base1_x, base1_y), (200, 40, 40))
        auto.strategy = AutoStrategy()
        player1_vehicles.append(auto)

    # ==========================================
    # JUGADOR 2 - AZUL (Derecha)
    # ==========================================
    player2_vehicles = []
    
    # 3 Jeeps en formación escalonada (offsets inversos para el lado derecho)
    for i in range(3):
        jeep_gx_offset = -(i // 2) # 0, 0, -1
        jeep_gy_offset = (i - 1) # -1, 0, 1
        jeep = Jeep(f"P2_Jeep_{i}", base2_gx + jeep_gx_offset, base2_gy + jeep_gy_offset, 
                   (base2_x, base2_y), (20, 20, 220))
        jeep.strategy = AggressiveJeepStrategy()
        player2_vehicles.append(jeep)
    
    # 2 Motos adelante
    for i in range(2):
        moto_gy_offset = (i * 2 - 1) # -1, 1
        moto = Moto(f"P2_Moto_{i}", base2_gx - 1, base2_gy + moto_gy_offset, 
                   (base2_x, base2_y), (80, 80, 255))
        moto.strategy = FastMotoStrategy()
        player2_vehicles.append(moto)
    
    # 2 Camiones atrás
    for i in range(2):
        camion_gy_offset = (i * 2 - 1) # -1, 1
        camion = Camion(f"P2_Camion_{i}", base2_gx + 1, base2_gy + camion_gy_offset, 
                       (base2_x, base2_y), (0, 0, 180))
        camion.strategy = SupportCamionStrategy()
        player2_vehicles.append(camion)
    
    # 3 Autos en V
    # Se definen directamente en coordenadas de celda
    auto_grid_positions = [
        (base2_gx, base2_gy - 1),
        (base2_gx, base2_gy + 1),
        (base2_gx - 1, base2_gy)
    ]
    for i, (agx, agy) in enumerate(auto_grid_positions):
        auto = Auto(f"P2_Auto_{i}", agx, agy, (base2_x, base2_y), (40, 40, 200))
        auto.strategy = BalancedAutoStrategy()
        player2_vehicles.append(auto)

    world.vehicles = player1_vehicles + player2_vehicles
    world.player1_vehicles = player1_vehicles
    world.player2_vehicles = player2_vehicles

    # ... (rest of the main function) ...

    def _rebuild_fleet(vehicle_data_list):
        """
        Función genérica para reconstruir una flota (lista de vehículos)
        a partir de sus datos guardados.
        """
        rebuilt_fleet = [] # 1. Crea una lista vacía
        
        # Diccionario para recrear vehículos por su tipo
        vehicle_classes = {
            "jeep": Jeep,
            "moto": Moto,
            "camion": Camion,
            "auto": Auto
        }
        for v_data in vehicle_data_list: # 2. Itera sobre los datos
            v_type = v_data.get('vehicle_type')
            if v_type in vehicle_classes:
                cls = vehicle_classes[v_type]
                
                # --- Lógica de reconstrucción (la misma que ya tenías) ---
                g_x = v_data['gx']
                g_y = v_data['gy']
                # Ya no necesitamos calcular p_x, p_y aquí, pasamos gx, gy directamente
                
                new_v = cls(v_data['id'], g_x, g_y, 
                            v_data['base_position_pixels'], v_data['color'])

                new_v.trips_left = v_data.get('trips_left', 1)
                new_v.alive = v_data.get('alive', True)
                new_v.score = v_data.get('score', 0)
                new_v.returning_to_base = v_data.get('returning_to_base', False)
                new_v.at_base = v_data.get('at_base', False)
                new_v.forced_return = v_data.get('forced_return', False)
                new_v.speed_pixels_per_update = v_data.get('speed_pixels_per_update', 1.5)

                new_v.cargo = []
                for item_type in v_data.get('cargo', []):
                    if item_type == 'person':
                        p_obj = Person(0,0)
                        p_obj.value = constants.POINTS_PERSON
                        new_v.cargo.append(p_obj) 
                    elif item_type in constants.MERCH_POINTS:
                        m_obj = Merchandise(0,0, item_type)
                        m_obj.value = constants.MERCH_POINTS.get(item_type, 0)
                        new_v.cargo.append(m_obj)
                
                # Restaurar el "cerebro" (usa STRATEGY_MAP, que es global)
                strategy_name = v_data.get('strategy_name')
                if strategy_name in STRATEGY_MAP:
                    new_v.strategy = STRATEGY_MAP[strategy_name]()
                else:
                    new_v.strategy = None
                
                rebuilt_fleet.append(new_v) # 3. Añade el vehículo a la NUEVA lista
        
        return rebuilt_fleet # 4. Devuelve la flota completa    

    current_state = GameState.PREPARATION
    game_time = 0
    file_menu_cache = [] # Lista genérica para guardar archivos (partidas O replays)
    file_menu_buttons = [] # Lista genérica para los rects de los botones
    file_menu_scroll_offset = 0
    previous_state = GameState.PREPARATION # Para saber a dónde volver
    
    # Variables para el REPLAY
    replay_buffer = [] # Aquí se guardan las "fotos" de la simulación
    replay_data = [] # Aquí se guarda el replay que estamos VIENDO
    current_replay_frame = 0 # El "cabezal" de la reproducción
    
    stats_data = [] # Para guardar los datos de la DB
    stats_menu_buttons = [] # Para los clics
    stats_scroll_offset = 0
    stats_saved_this_game = False # Flag para evitar guardar 60 veces por segundo
    
    #Definición de las áreas de los botones
    btn_height = 50
    btn_y = constants.UI_PANEL_Y + (constants.UI_PANEL_HEIGHT - btn_height) // 2
    btn_width_small = 60
    btn_width_large = 80
    btn_width_xl = 90 # Para "Guardar" y "Cargar"

    # Grupo 1: Controles de Simulación (Izquierda)
    btn_init = pygame.Rect(20, btn_y, btn_width_large, btn_height)
    btn_play = pygame.Rect(110, btn_y, btn_width_small, btn_height)
    btn_pause = pygame.Rect(180, btn_y, btn_width_small, btn_height)
    btn_step_back = pygame.Rect(250, btn_y, btn_width_small, btn_height)
    btn_step_fwd = pygame.Rect(320, btn_y, btn_width_small, btn_height)
    
    # Grupo 2: Persistencia (Derecha)
    btn_save = pygame.Rect(constants.WIDTH - 420, btn_y, btn_width_xl, btn_height)
    btn_load = pygame.Rect(constants.WIDTH - 320, btn_y, btn_width_xl, btn_height)
    btn_replay = pygame.Rect(constants.WIDTH - 220, btn_y, btn_width_large, btn_height)
    btn_stats = pygame.Rect(constants.WIDTH - 130, btn_y, btn_width_large, btn_height)

    # Efectos de partículas
    particles = []

    def create_explosion(x, y, color):
        """Crea partículas de explosión"""
        for _ in range(15):
            angle = math.radians(pygame.time.get_ticks() % 360)
            speed = 2 + (pygame.time.get_ticks() % 3)
            particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': color,
                'life': 30
            })

    def update_particles():
        """Actualiza y dibuja partículas"""
        for particle in particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                particles.remove(particle)
            else:
                alpha = int(255 * (particle['life'] / 30))
                size = max(1, particle['life'] // 10)
                color = particle['color'] + (alpha,)
                pygame.draw.circle(screen, color, 
                                 (int(particle['x']), int(particle['y'])), size)

    def draw_bases():
        """Dibuja zonas de base mejoradas"""
        # Base 1 - Rojo
        # Efecto de pulso
        pulse = abs(math.sin(game_time * 0.05)) * 10 + 45
        
        # Círculos concéntricos
        pygame.draw.circle(screen, (220, 20, 20, 30), (base1_x, base1_y), int(pulse + 20), 2)
        pygame.draw.circle(screen, (220, 20, 20, 60), (base1_x, base1_y), int(pulse), 3)
        pygame.draw.circle(screen, (220, 20, 20), (base1_x, base1_y), 50, 2)
        
        # Texto con sombra
        text = FONT_NORMAL.render("BASE P1", True, (0, 0, 0))
        screen.blit(text, (base1_x - 32, base1_y - 72))
        text = FONT_NORMAL.render("BASE P1", True, (255, 100, 100))
        screen.blit(text, (base1_x - 33, base1_y - 73))
        
        # Base 2 - Azul
        pygame.draw.circle(screen, (20, 20, 220, 30), (base2_x, base2_y), int(pulse + 20), 2)
        pygame.draw.circle(screen, (20, 20, 220, 60), (base2_x, base2_y), int(pulse), 3)
        pygame.draw.circle(screen, (20, 20, 220), (base2_x, base2_y), 50, 2)
        
        text = FONT_NORMAL.render("BASE P2", True, (0, 0, 0))
        screen.blit(text, (base2_x - 32, base2_y - 72))
        text = FONT_NORMAL.render("BASE P2", True, (100, 100, 255))
        screen.blit(text, (base2_x - 33, base2_y - 73))

    def draw_button_text(surface, text, rect, font=FONT_NORMAL):
        """Helper para centrar texto en un botón"""
        text_surf = font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

    #FUNCIÓN DE DIBUJO DEL PANEL
    def draw_control_panel(surface):
        """Dibuja el panel de control fijo en la parte inferior."""
        # Fondo del panel
        panel_rect = pygame.Rect(0, constants.UI_PANEL_Y, constants.WIDTH, constants.UI_PANEL_HEIGHT)
        draw_gradient_rect(surface, (30, 30, 40), (50, 50, 60), panel_rect)
        pygame.draw.line(surface, (100, 100, 110), (0, constants.UI_PANEL_Y), (constants.WIDTH, constants.UI_PANEL_Y), 2)
        
        # Dibujar botones (los colores vienen del bucle principal)
        pygame.draw.rect(surface, color_init, btn_init, border_radius=5)
        pygame.draw.rect(surface, color_play_btn, btn_play, border_radius=5)
        pygame.draw.rect(surface, color_pause_btn, btn_pause, border_radius=5)
        pygame.draw.rect(surface, color_default, btn_step_back, border_radius=5) # color_default está bien
        pygame.draw.rect(surface, color_step_fwd, btn_step_fwd, border_radius=5)
        pygame.draw.rect(surface, color_save_btn, btn_save, border_radius=5)
        pygame.draw.rect(surface, color_load_btn, btn_load, border_radius=5)
        pygame.draw.rect(surface, color_default, btn_replay, border_radius=5) # color_default está bien
        pygame.draw.rect(surface, color_default, btn_stats, border_radius=5) # color_default está bien
        
        # --- Dibujar texto de botones ---
        draw_button_text(surface, "Init", btn_init)
        draw_button_text(surface, "Play", btn_play)
        draw_button_text(surface, "Pause", btn_pause)
        draw_button_text(surface, "<<", btn_step_back, FONT_TITLE)
        draw_button_text(surface, ">>", btn_step_fwd, FONT_TITLE)
        draw_button_text(surface, "Guardar", btn_save)
        draw_button_text(surface, "Cargar", btn_load)
        draw_button_text(surface, "Replay", btn_replay)
        draw_button_text(surface, "Stats", btn_stats)
        
    def draw_popup_base(surface, width, height):
        """
        Dibuja el fondo oscuro y el panel principal para CUALQUIER pop-up.
        Devuelve las coordenadas (x, y) del panel para dibujar contenido dentro.
        """
        # 1. Fondo oscuro
        overlay = pygame.Surface((constants.WIDTH, constants.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        # 2. Panel principal
        panel_x = constants.WIDTH // 2 - width // 2
        panel_y = constants.HEIGHT // 2 - height // 2
        draw_panel(surface, panel_x, panel_y, width, height, (40, 50, 60))
        
        return panel_x, panel_y # Devolvemos las coordenadas
    
    def draw_file_selection_menu(surface, title, file_list, scroll_offset):
        """Dibuja un menú genérico para seleccionar un archivo."""
        nonlocal file_menu_buttons
        file_menu_buttons.clear()

        # 1. Dibuja el fondo y el panel (500x400)
        panel_x, panel_y = draw_popup_base(surface, 500, 400)

        # 2. Título
        title_surf = FONT_TITLE.render(title, True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(constants.WIDTH // 2, panel_y + 40))
        surface.blit(title_surf, title_rect)

        # 3. Dibujar la lista de archivos
        y_pos = panel_y + 80
        files_to_show = file_list[scroll_offset : scroll_offset + 5]

        for i, filename in enumerate(files_to_show):
            display_name = filename.replace(".pkl", "").replace("_", "  ")
            
            btn_rect = pygame.Rect(panel_x + 20, y_pos, 500 - 40, 40)
            file_menu_buttons.append((btn_rect, filename)) # Guardamos rect y nombre

            mouse_pos = pygame.mouse.get_pos()
            if btn_rect.collidepoint(mouse_pos):
                pygame.draw.rect(surface, (100, 110, 120), btn_rect, border_radius=5)
            else:
                pygame.draw.rect(surface, (60, 70, 80), btn_rect, border_radius=5)
            
            text_surf = FONT_NORMAL.render(display_name, True, (255, 255, 255))
            surface.blit(text_surf, (btn_rect.x + 15, btn_rect.y + 10))
            y_pos += 50
        
        # 4. Botón de Cancelar
        btn_cancel_rect = pygame.Rect(constants.WIDTH // 2 - 50, panel_y + 400 - 60, 100, 40)
        file_menu_buttons.append((btn_cancel_rect, "CANCEL"))
        
        if btn_cancel_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(surface, (180, 50, 50), btn_cancel_rect, border_radius=5)
        else:
            pygame.draw.rect(surface, (150, 30, 30), btn_cancel_rect, border_radius=5)
        draw_button_text(surface, "Cancelar", btn_cancel_rect)
    
    def draw_stats_menu(surface):
        """Dibuja un menú superpuesto para mostrar el historial de partidas."""
        nonlocal file_menu_buttons # Usamos la variable global
        file_menu_buttons.clear() # Limpiamos los botones

        # 1. Dibuja el fondo y el panel (600x400)
        panel_x, panel_y = draw_popup_base(surface, 600, 400)

        # 2. Título
        title = FONT_TITLE.render("Historial de Partidas", True, (255, 215, 0))
        title_rect = title.get_rect(center=(constants.WIDTH // 2, panel_y + 40))
        surface.blit(title, title_rect)

        # 3. Encabezados
        y_pos = panel_y + 80
        header_font = pygame.font.SysFont("Arial", 16, bold=True)
        header1 = header_font.render("Fecha", True, (200, 200, 200))
        header2 = header_font.render("Ganador", True, (200, 200, 200))
        header3 = header_font.render("Puntajes (J1 / J2)", True, (200, 200, 200))
        surface.blit(header1, (panel_x + 30, y_pos))
        surface.blit(header2, (panel_x + 200, y_pos))
        surface.blit(header3, (panel_x + 350, y_pos))
        y_pos += 30

        # 4. Dibujar la lista de estadísticas
        stats_to_show = stats_data[stats_scroll_offset : stats_scroll_offset + 5]

        for row in stats_to_show:
            date, winner, p1_score, p2_score = row
            
            date_surf = FONT_NORMAL.render(date, True, (255, 255, 255))
            winner_surf = FONT_NORMAL.render(str(winner), True, (255, 255, 255))
            score_surf = FONT_NORMAL.render(f"{p1_score} / {p2_score}", True, (255, 215, 0))
            
            surface.blit(date_surf, (panel_x + 30, y_pos))
            surface.blit(winner_surf, (panel_x + 200, y_pos))
            surface.blit(score_surf, (panel_x + 350, y_pos))
            y_pos += 40
        
        # 5. Botón de Cerrar
        btn_close_rect = pygame.Rect(constants.WIDTH // 2 - 50, panel_y + 400 - 60, 100, 40)
        file_menu_buttons.append((btn_close_rect, "CANCEL")) # "CANCEL" es la acción
        
        if btn_close_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(surface, (100, 110, 120), btn_close_rect, border_radius=5)
        else:
            pygame.draw.rect(surface, (60, 70, 80), btn_close_rect, border_radius=5)
        draw_button_text(surface, "Cerrar", btn_close_rect)
    
    # Variables para efectos
    last_p1_alive = 10
    last_p2_alive = 10

    def get_full_game_state():
        """
        Recopila el estado de todos los objetos del juego y lo empaqueta.
        """
        # 1. Guardar el estado de todos los vehículos
        p1_vehicles_state = [v.get_state() for v in player1_vehicles]
        p2_vehicles_state = [v.get_state() for v in player2_vehicles]
        
        # 2. Guardar el estado del mundo (minas, recursos, etc.)
        world_state = world.get_state()  # Llama al get_state() de world
        
        # 3. Empaquetar todo en un solo diccionario
        game_state_data = {
            "game_time": game_time,
            "world": world_state,
            "player1_vehicles": p1_vehicles_state,
            "player2_vehicles": p2_vehicles_state
        }
        return game_state_data


    def get_lightweight_state():
        """
        Guarda solo las posiciones y estados básicos de los vehículos.
        Ideal para avanzar/retroceder rápido sin recargar todo el mundo.
        """
        return {
            "p1": [
                {"x": v.x, "y": v.y, "alive": v.alive, "score": v.score}
                for v in player1_vehicles
            ],
            "p2": [
                {"x": v.x, "y": v.y, "alive": v.alive, "score": v.score}
                for v in player2_vehicles
            ]
        }
        
    def _rebuild_fleet(vehicle_data_list):
        """
        Función genérica para reconstruir una flota (lista de vehículos)
        a partir de sus datos guardados.
        """
        rebuilt_fleet = [] # 1. Crea una lista vacía
        # Diccionario para recrear vehículos por su tipo
        vehicle_classes = {
            "jeep": Jeep,
            "moto": Moto,
            "camion": Camion,
            "auto": Auto
        }
        for v_data in vehicle_data_list: # 2. Itera sobre los datos
            v_type = v_data.get('vehicle_type')
            if v_type in vehicle_classes:
                cls = vehicle_classes[v_type]
                
                # Lógica de reconstrucción
                g_x = v_data['gx']
                g_y = v_data['gy']
                # CORRECCIÓN: Pasamos gx, gy directamente al constructor del vehículo.
                new_v = cls(v_data['id'], g_x, g_y,
                            v_data['base_position_pixels'], v_data['color'])

                new_v.trips_left = v_data.get('trips_left', 1)
                new_v.alive = v_data.get('alive', True)
                new_v.score = v_data.get('score', 0)
                new_v.returning_to_base = v_data.get('returning_to_base', False)
                new_v.at_base = v_data.get('at_base', False)
                new_v.forced_return = v_data.get('forced_return', False)
                new_v.speed_pixels_per_update = v_data.get('speed_pixels_per_update', 1.5)

                new_v.cargo = []
                for item_type in v_data.get('cargo', []):
                    if item_type == 'person':
                        p_obj = Person(0,0)
                        p_obj.value = constants.POINTS_PERSON
                        new_v.cargo.append(p_obj) 
                    elif item_type in constants.MERCH_POINTS:
                        m_obj = Merchandise(0,0, item_type)
                        m_obj.value = constants.MERCH_POINTS.get(item_type, 0)
                        new_v.cargo.append(m_obj)
                
                # Restaurar el "cerebro"
                strategy_name = v_data.get('strategy_name')
                if strategy_name in STRATEGY_MAP:
                    new_v.strategy = STRATEGY_MAP[strategy_name]()
                else:
                    new_v.strategy = None
                
                rebuilt_fleet.append(new_v) # 3. Añade el vehículo a la NUEVA lista
        
        return rebuilt_fleet # 4. Devuelve la flota completa    

    def load_game_from_data(data):
        """
        Restaura el estado del juego desde un diccionario.
        Si el frame es 'liviano', solo actualiza posiciones y puntajes.
        Si es completo, reconstruye todo el mundo.
        """
        nonlocal game_time, current_state

        # --- Caso 1: Frame liviano (replay rápido) ---
        if "p1" in data and "p2" in data:
            for v, d in zip(player1_vehicles, data["p1"]):
                v.x = d["x"]
                v.y = d["y"]
                v.alive = d.get("alive", True)
                v.score = d.get("score", 0)
            for v, d in zip(player2_vehicles, data["p2"]):
                v.x = d["x"]
                v.y = d["y"]
                v.alive = d.get("alive", True)
                v.score = d.get("score", 0)
            return  # listo, no se recarga el mundo

        # --- Caso 2: Frame completo (carga total) ---
        world.load_state(data['world'])

        player1_vehicles.clear()
        player2_vehicles.clear()
        player1_vehicles.extend(_rebuild_fleet(data.get('player1_vehicles', [])))
        player2_vehicles.extend(_rebuild_fleet(data.get('player2_vehicles', [])))

        world.vehicles = player1_vehicles + player2_vehicles
        world.player1_vehicles = player1_vehicles
        world.player2_vehicles = player2_vehicles

        game_time = data.get('game_time', 0)


    def handle_mine_explosion(mine):
        """
        Gestiona la lógica completa de la explosión de una mina,
        afectando a toda el área y a todas las entidades.
        """
        print(f"¡BOOM! Mina {mine.type} explotó en ({mine.x}, {mine.y})")
        create_explosion(mine.x, mine.y, (255, 100, 0))

        # 1. Encontrar todas las celdas afectadas por el radio
        affected_cells = set() # Usar un set para evitar duplicados
        center_gx, center_gy = world.pixel_to_cell(mine.x, mine.y)
        radius_in_cells = math.ceil(mine.radius / constants.TILE)

        for gy_offset in range(-radius_in_cells, radius_in_cells + 1):
            for gx_offset in range(-radius_in_cells, radius_in_cells + 1):
                gx, gy = center_gx + gx_offset, center_gy + gy_offset
                
                if 0 <= gx < constants.GRID_WIDTH and 0 <= gy < constants.GRID_HEIGHT:
                    px, py = world.cell_to_pixel_center(gx, gy)
                    if mine.check_collision(px, py):
                        affected_cells.add((gx, gy))

        # 2. Identificar todas las entidades a ser destruidas
        vehicles_to_kill = []
        for v in world.vehicles:
            if v.alive and (v.gx, v.gy) in affected_cells:
                vehicles_to_kill.append(v)

        resources_to_remove = []
        for r in world.resources:
            res_gx, res_gy = world.pixel_to_cell(r.x, r.y)
            if (res_gx, res_gy) in affected_cells:
                resources_to_remove.append(r)

        # 3. Destruir las entidades identificadas
        for v in vehicles_to_kill:
            v.die()
            create_explosion(v.x, v.y, v.color)

        for r in resources_to_remove:
            world.remove_resource(r)

        # 4. Limpiar la grid y añadir efectos de fuego
        for gx, gy in affected_cells:
            world.grid[gy][gx] = 0 # Asegura que la celda quede vacía
            fire_x, fire_y = world.cell_to_pixel(gx, gy)
            world.effects.append(FireEffect(fire_x, fire_y))

        # 5. Desactivar la mina
        mine.active = False

    def run_game_logic_tick():
        """
        Ejecuta UN SOLO fotograma (tick) de la lógica del juego.
        Devuelve True si ocurrió un evento lógico, False si solo fue animación.
        """
        nonlocal game_time, current_state, stats_saved_this_game, replay_buffer
        nonlocal last_p1_alive, last_p2_alive
        
        a_logical_update_happened = False
        game_time += 1
        
        if world.update_g1_mines():
             a_logical_update_happened = True

        for effect in world.effects[:]:
            if not effect.update():
                world.effects.remove(effect)

        # 1. LÓGICA DE FIN DE JUEGO (RECURSOS)
        if len(world.resources) == 0 and not hasattr(world, 'ending_phase'):
            a_logical_update_happened = True
            world.ending_phase = True
            world.ending_timer = 0
            for vehicle in world.vehicles:
                if vehicle.alive:
                    vehicle.force_return_to_base()
        
        if hasattr(world, 'ending_phase') and world.ending_phase:
            world.ending_timer += 1
            all_at_base = all(v.at_base or not v.alive for v in world.vehicles)
            
            if all_at_base or world.ending_timer > 300: 
                if not stats_saved_this_game:
                    p1_score = sum(v.score for v in player1_vehicles)
                    p2_score = sum(v.score for v in player2_vehicles)
                    
                    p1_alive = sum(1 for v in player1_vehicles if v.alive)
                    p2_alive = sum(1 for v in player2_vehicles if v.alive)

                    winner = "Empate"
                    if p1_alive == 0 and p2_alive > 0:
                        winner = "Jugador 2"
                    elif p2_alive == 0 and p1_alive > 0:
                        winner = "Jugador 1"
                    elif p1_score > p2_score: 
                        winner = "Jugador 1"
                    elif p2_score > p1_score: 
                        winner = "Jugador 2"

                    db.save_match_result(winner, p1_score, p2_score)
                    stats_saved_this_game = True
                
                if replay_buffer:
                    replay_name = f"Replay_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pkl"
                    try:
                        with open(replay_name, 'wb') as f: pickle.dump(replay_buffer, f)
                    except Exception as e: print(f"Error al guardar el replay: {e}")
                    replay_buffer.clear()
                
                current_state = GameState.GAME_OVER
                return True

        # 2. COLISIONES CON MINAS
        mines_to_explode = []
        for mine in world.mines:
            if not mine.active: continue
            mine_gx, mine_gy = world.pixel_to_cell(mine.x, mine.y)
            for v in world.vehicles:
                if v.alive and v.gx == mine_gx and v.gy == mine_gy:
                    if mine not in mines_to_explode:
                        mines_to_explode.append(mine)
                    break 
        
        if mines_to_explode:
            a_logical_update_happened = True
            for mine in mines_to_explode:
                handle_mine_explosion(mine)
            world.mines = [m for m in world.mines if m.active]

        # 3. ACTUALIZAR VEHÍCULOS
        for vehicle in world.vehicles:
            if vehicle.alive:
                if vehicle.update(world):
                    a_logical_update_happened = True 
        
        # 4. COLISIONES FÍSICAS (ENEMIGOS)
        for v1 in player1_vehicles:
            if not v1.alive: continue
            v1_at_base = (v1.gx == v1.base_gx and v1.gy == v1.base_gy)
            for v2 in player2_vehicles:
                if not v2.alive: continue
                if v1.gx == v2.gx and v1.gy == v2.gy:
                    v2_at_base = (v2.gx == v2.base_gx and v2.gy == v2.base_gy)
                    if not v1_at_base and not v2_at_base:
                        a_logical_update_happened = True
                        create_explosion(v1.x, v1.y, (255, 128, 0)) 
                        v1.die()
                        v2.die()

        # 5. DETECTAR DESTRUCCIONES (para efectos visuales)
        p1_alive_now = sum(1 for v in player1_vehicles if v.alive)
        p2_alive_now = sum(1 for v in player2_vehicles if v.alive)
        if p1_alive_now < last_p1_alive or p2_alive_now < last_p2_alive:
            a_logical_update_happened = True
        last_p1_alive = p1_alive_now
        last_p2_alive = p2_alive_now
        
        # LÓGICA DE FIN DE JUEGO POR ANIQUILACIÓN
        if (p1_alive_now == 0 or p2_alive_now == 0) and not hasattr(world, 'ending_phase'):
            a_logical_update_happened = True
            world.ending_phase = True
            world.ending_timer = 301 # Forzar fin inmediato en el siguiente ciclo
        
        # 6. GRABAR FOTOGRAMA PARA REPLAY
        if a_logical_update_happened:
            try:
                replay_buffer.append(get_full_game_state())
            except Exception as e:
                print(f"Error al grabar fotograma de replay: {e}")
        
        try:
            frame_history.append(get_full_game_state())
            current_frame_index = len(frame_history) - 1
        except Exception as e:
            print(f"Error al guardar frame del historial: {e}")

        return a_logical_update_happened
    
    while True:
        
        # --- Colores de Botones (con lógica de estado) ---
        color_disabled = (40, 40, 40)
        color_default = (80, 80, 90)
        color_play = (60, 150, 60)
        color_pause = (150, 60, 60)

        # Lógica de habilitación (usa "current_state" en lugar de "state")
        init_enabled = current_state == GameState.PREPARATION
        play_enabled = current_state in (GameState.PREPARATION, GameState.PAUSED, GameState.REPLAY_PAUSED)
        pause_enabled = current_state in (GameState.PLAYING, GameState.REPLAYING)
        save_enabled = current_state in (GameState.PLAYING, GameState.PAUSED)
        load_enabled = current_state in (GameState.PREPARATION, GameState.PAUSED)
        step_fwd_enabled = current_state in (GameState.PAUSED, GameState.REPLAY_PAUSED)
        
        # Asignar colores
        color_init = color_default if init_enabled else color_disabled
        color_play_btn = color_play if play_enabled else color_disabled
        color_pause_btn = color_pause if pause_enabled else color_disabled
        color_save_btn = color_default if save_enabled else color_disabled
        color_load_btn = color_default if load_enabled else color_disabled
        color_step_fwd = color_default if step_fwd_enabled else color_disabled
        color_step_back = color_default if step_fwd_enabled else color_disabled

        # Bucle y manejo de eventos al pausar 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # --- MANEJO DE CLICS DEL MOUSE ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic izquierdo
                    pos = pygame.mouse.get_pos()

                    # --- Lógica si estamos en un MENÚ DE SELECCIÓN DE ARCHIVO ---
                    if current_state in (GameState.SELECT_LOAD, GameState.SELECT_REPLAY, GameState.SHOW_STATS):
                        for rect, filename in file_menu_buttons:
                            if rect.collidepoint(pos):
                                if filename == "CANCEL":
                                    current_state = previous_state  # Volver a PREPARATION o PAUSED
                                else:
                                    try:
                                        if current_state == GameState.SELECT_LOAD:
                                            print(f"Cargando partida: {filename}")
                                            with open(filename, 'rb') as f:
                                                game_data = pickle.load(f)
                                            load_game_from_data(game_data)
                                            current_state = GameState.PAUSED
                                        
                                        elif current_state == GameState.SELECT_REPLAY:
                                            print(f"Cargando replay: {filename}")
                                            with open(filename, 'rb') as f:
                                                replay_data = pickle.load(f)
                                            current_replay_frame = 0
                                            current_state = GameState.REPLAYING
                                            
                                    except Exception as e:
                                        print(f"Error al cargar el archivo {filename}: {e}")
                                break  # salir del bucle de botones
                    
                    # --- Lógica del panel de control (en juego o replay) ---
                    elif current_state != GameState.GAME_OVER:
                        if btn_init.collidepoint(pos) and current_state == GameState.PREPARATION:
                            world.initialize_map_elements()
                            frame_history.clear()
                            frame_history.append(get_full_game_state())
                            current_frame_index = 0
                            stats_saved_this_game = False
                        
                        elif btn_play.collidepoint(pos) and play_enabled:
                            if current_state == GameState.REPLAY_PAUSED:
                                print(f"Reanudando replay desde frame {current_replay_frame}")
                                current_state = GameState.REPLAYING
                            else:
                                if current_state == GameState.PREPARATION and not world.resources:
                                    print("Presiona 'Init' primero para generar el mapa.")
                                    continue
                                current_state = GameState.PLAYING
                        
                        elif btn_pause.collidepoint(pos) and pause_enabled:
                            if current_state == GameState.PLAYING:
                                current_state = GameState.PAUSED
                            elif current_state == GameState.REPLAYING:
                                current_state = GameState.REPLAY_PAUSED
                        
                        # --- Paso adelante ---
                        elif btn_step_fwd.collidepoint(pos):
                            if current_state == GameState.PAUSED:
                                print("Avanzando varios frames lógicos (juego normal)...")
                                step_size = 20
                                for _ in range(step_size):
                                    if run_game_logic_tick():
                                        try:
                                            frame_history.append(get_full_game_state())
                                            current_frame_index = len(frame_history) - 1
                                        except Exception as e:
                                            print(f"Error al guardar frame: {e}")
                                print(f"Avanzó {step_size} frames.")
                            
                            elif current_state == GameState.REPLAY_PAUSED:
                                # --- Adelantar replay varios frames ---
                                if replay_data:
                                    step = 5  # cantidad de frames que avanza por clic (ajustable)
                                    keys = pygame.key.get_mods()
                                    if keys & pygame.KMOD_SHIFT:
                                        step = 20  # con Shift, salto grande
                                    current_replay_frame = min(current_replay_frame + step, len(replay_data) - 1)
                                    load_game_from_data(replay_data[current_replay_frame])
                                    print(f"Replay -> +{step} frames | Frame {current_replay_frame+1}/{len(replay_data)}")
                                else:
                                    print("No hay datos de replay para avanzar.")

                        # --- Paso atrás ---
                        elif btn_step_back.collidepoint(pos):
                            if current_state == GameState.PAUSED:
                                if current_frame_index > 0:
                                    current_frame_index = max(0, current_frame_index - 10)
                                    print(f"Retrocediendo al frame {current_frame_index}")
                                    frame_data = frame_history[current_frame_index]

                                    # Detectamos tipo de frame
                                    if "p1" in frame_data and "p2" in frame_data:
                                        for v, data in zip(player1_vehicles, frame_data["p1"]):
                                            v.x = data["x"]; v.y = data["y"]
                                            v.alive = data["alive"]; v.score = data["score"]
                                        for v, data in zip(player2_vehicles, frame_data["p2"]):
                                            v.x = data["x"]; v.y = data["y"]
                                            v.alive = data["alive"]; v.score = data["score"]
                                    else:
                                        load_game_from_data(frame_data)
                                else:
                                    print("Llegaste al inicio del juego.")

                            elif current_state == GameState.REPLAY_PAUSED:
                                # --- Retroceder replay varios frames ---
                                if replay_data:
                                    step = 5  # cantidad de frames que retrocede por clic
                                    keys = pygame.key.get_mods()
                                    if keys & pygame.KMOD_SHIFT:
                                        step = 20  # con Shift, salto grande
                                    current_replay_frame = max(0, current_replay_frame - step)
                                    load_game_from_data(replay_data[current_replay_frame])
                                    print(f"Replay -> -{step} frames | Frame {current_replay_frame+1}/{len(replay_data)}")
                                else:
                                    print("No hay datos de replay para retroceder.")

                        elif btn_save.collidepoint(pos) and save_enabled:
                            print("Guardando partida...")
                            game_data = get_full_game_state()
                            save_name = f"Partida_Guardada_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pkl"
                            try:
                                with open(save_name, 'wb') as f:
                                    pickle.dump(game_data, f)
                                print(f"¡Partida guardada exitosamente en {save_name}!")
                            except Exception as e:
                                print(f"Error al guardar partida: {e}")
                        
                        elif btn_load.collidepoint(pos) and (current_state == GameState.PREPARATION or current_state == GameState.PAUSED):
                            print("Abriendo menú de Cargar Partida...")
                            file_menu_cache = glob.glob("Partida_Guardada_*.pkl")
                            file_menu_cache.sort(key=os.path.getctime, reverse=True)
                            file_menu_scroll_offset = 0
                            previous_state = current_state
                            current_state = GameState.SELECT_LOAD

                        elif btn_replay.collidepoint(pos) and (current_state == GameState.PREPARATION or current_state == GameState.PAUSED):
                            print("Abriendo menú de Replay...")
                            file_menu_cache = glob.glob("Replay_*.pkl")
                            file_menu_cache.sort(key=os.path.getctime, reverse=True)
                            file_menu_scroll_offset = 0
                            previous_state = current_state
                            current_state = GameState.SELECT_REPLAY
                            
                        elif btn_stats.collidepoint(pos) and (current_state == GameState.PREPARATION or current_state == GameState.PAUSED):
                            print("Abriendo menú de Estadísticas...")
                            try:
                                stats_data = db.get_statistics()
                                stats_scroll_offset = 0
                                previous_state = current_state
                                current_state = GameState.SHOW_STATS
                            except Exception as e:
                                print(f"Error al cargar estadísticas: {e}")
             
            # MANEJO DE TECLADO
            if event.type == pygame.KEYDOWN:
                # Comprobación de estados de menú O de replay
                if current_state in (GameState.SELECT_LOAD, GameState.SELECT_REPLAY, GameState.SHOW_STATS, 
                                     GameState.REPLAYING, GameState.REPLAY_PAUSED):
                    
                    if event.key == pygame.K_ESCAPE:
                        if current_state in (GameState.REPLAYING, GameState.REPLAY_PAUSED):
                            # Si salimos del replay, limpiamos los datos
                            print("Saliendo del replay...")
                            replay_data.clear()
                            current_replay_frame = 0
                        current_state = previous_state # Salir con ESC a la pantalla anterior
                    
                    # Scroll (solo si estamos en menú de stats/archivos)
                    elif current_state in (GameState.SELECT_LOAD, GameState.SELECT_REPLAY, GameState.SHOW_STATS):
                        if event.key == pygame.K_DOWN:
                            file_menu_scroll_offset = min(file_menu_scroll_offset + 1, max(0, len(file_menu_cache) - 5))
                        elif event.key == pygame.K_UP:
                            file_menu_scroll_offset = max(0, file_menu_scroll_offset - 1)

                elif current_state == GameState.PLAYING:
                    if event.key == pygame.K_i:
                        world.relocate_g1_mines()
                
                elif current_state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        main()
                        return

        # Lógica del juego
        if current_state == GameState.PLAYING:
            # Ejecutar la lógica normal
            run_game_logic_tick()
            
            # Guardar una captura  del estado del juego
            try:
                frame_history.append(get_lightweight_state())
                current_frame_index = len(frame_history) - 1
                
                # Evitar consumir toda la RAM
                if len(frame_history) > 10000:
                    frame_history.pop(0)
                    current_frame_index -= 1

            except Exception as e:
                print(f"Error guardando frame: {e}")

                    
        elif current_state == GameState.REPLAYING:
            # Inicialización la primera vez que entramos aquí
            if 'replay_playing' not in locals():
                replay_playing = True
                replay_speed = 1
                replay_fps = 30 
                last_update_time = pygame.time.get_ticks()
                last_key_time = 0
                key_debounce_ms = 150

            now = pygame.time.get_ticks()

            eff_speed = replay_speed if replay_speed != 0 else 1
            base_interval = int(1000 / replay_fps)
            interval = max(1, int(base_interval / abs(eff_speed)))

            # --- LÓGICA DE REPRODUCCIÓN CORREGIDA ---
            if replay_playing and now - last_update_time >= interval:
                last_update_time = now

                # 1. Calculamos el próximo frame
                next_frame = current_replay_frame + replay_speed
                next_frame = max(0, min(next_frame, max(0, len(replay_data) - 1)))

                # 2. Comprobamos si nos movimos o si llegamos al final/inicio
                if next_frame == current_replay_frame:
                    # No nos movimos (estamos al inicio o al final)
                    replay_playing = False # Pausamos
                    
                    # Si pausamos Y estamos en el último frame Y íbamos hacia adelante
                    if current_replay_frame == len(replay_data) - 1 and replay_speed > 0:
                        print("Replay finalizado.")
                        current_state = GameState.GAME_OVER #Terminamos el juego
                
                # 4. Si nos movimos, cargamos el frame
                else:
                    current_replay_frame = next_frame
                    try:
                        frame_data = replay_data[current_replay_frame]
                        load_game_from_data(frame_data)
                    except Exception as e:
                        print(f"Error al reproducir frame de replay: {e}")
                        replay_playing = False

            # Controles de teclado (debounce no bloqueante)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and now - last_key_time > key_debounce_ms:
                replay_playing = not replay_playing
                last_key_time = now

            if keys[pygame.K_RIGHT] and now - last_key_time > key_debounce_ms:
                replay_speed = min(8, replay_speed + 1)
                if replay_speed == 0: replay_speed = 1
                last_key_time = now

            if keys[pygame.K_LEFT] and now - last_key_time > key_debounce_ms:
                replay_speed = max(-8, replay_speed - 1)
                if replay_speed == 0: replay_speed = -1
                last_key_time = now

            # Barra de progreso (igual que antes)
            progress = current_replay_frame / max(1, len(replay_data) - 1)
            pygame.draw.rect(screen, (50, 50, 60), (100, constants.HEIGHT - 30, 600, 10))
            pygame.draw.rect(screen, (255, 215, 0), (100, constants.HEIGHT - 30, int(600 * progress), 10))

            info = FONT_SMALL.render(
                f"Frame {current_replay_frame+1}/{len(replay_data)}  |  Vel: x{replay_speed}  |  {'▶️' if replay_playing else '⏸️'}",
                True, (255, 255, 255)
            )
            screen.blit(info, (constants.WIDTH//2 - 150, constants.HEIGHT - 50))

                        

        # Dibujo
        world.draw(screen)
        draw_bases()
        
        # Dibujar vehículos
        for vehicle in world.vehicles:
            vehicle.draw(screen)
        
        # Efectos de partículas
        update_particles()
        
        # HUD moderno
        world.draw_premium_hud(screen, player1_vehicles, player2_vehicles, game_time)
        
        # Mensaje cuando se terminan los recursos
        if hasattr(world, 'ending_phase') and world.ending_phase:
            # Banner de finalización
            banner_height = 60
            banner_y = constants.HEIGHT // 2 - banner_height // 2
            
            # Fondo del banner con animación
            pulse = abs(math.sin(game_time * 0.15)) * 20 + 200
            banner_surf = pygame.Surface((constants.WIDTH, banner_height), pygame.SRCALPHA)
            banner_surf.fill((0, 0, 0, 180))
            screen.blit(banner_surf, (0, banner_y))
            
            # Borde superior e inferior
            pygame.draw.line(screen, (int(pulse), 215, 0), 
                           (0, banner_y), (constants.WIDTH, banner_y), 3)
            pygame.draw.line(screen, (int(pulse), 215, 0), 
                           (0, banner_y + banner_height), (constants.WIDTH, banner_y + banner_height), 3)
            
            # Texto animado
            banner_font = pygame.font.SysFont("Arial", 24, bold=True)
            text1 = banner_font.render("RECURSOS AGOTADOS", True, (255, 215, 0))
            text1_rect = text1.get_rect(center=(constants.WIDTH//2, banner_y + 18))
            screen.blit(text1, text1_rect)
            
            info_font = pygame.font.SysFont("Arial", 18)
            text2 = info_font.render("Todos los vehículos regresando a base...", True, (255, 255, 255))
            text2_rect = text2.get_rect(center=(constants.WIDTH//2, banner_y + 42))
            screen.blit(text2, text2_rect)
        
        # --- DIBUJAR EL PANEL DE CONTROL FIJO ---
        # (Se dibuja siempre, encima del HUD pero debajo de los pop-ups)
        draw_control_panel(screen)
        
        # Estado del juego
        # --- DIBUJAR EL PANEL DE CONTROL FIJO ---
        # (No lo dibujamos si estamos en un menú de selección)
        if current_state not in (GameState.SELECT_LOAD, GameState.SELECT_REPLAY, GameState.SHOW_STATS):
            draw_control_panel(screen)
        
        # --- DIBUJAR ESTADOS SUPERPUESTOS ---
        if current_state == GameState.PAUSED:
            overlay = pygame.Surface((constants.WIDTH, constants.GAME_WORLD_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            pause_text = FONT_TITLE.render("PAUSADO", True, (255, 255, 0))
            text_rect = pause_text.get_rect(center=(constants.WIDTH // 2, constants.GAME_WORLD_HEIGHT // 2))
            screen.blit(pause_text, text_rect)

        elif current_state == GameState.REPLAY_PAUSED:
            overlay = pygame.Surface((constants.WIDTH, constants.GAME_WORLD_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            
            # Texto principal "REPLAY PAUSADO"
            pause_text = FONT_TITLE.render("REPLAY PAUSADO", True, (100, 200, 255))
            # (Lo centramos un poco más arriba)
            text_rect = pause_text.get_rect(center=(constants.WIDTH // 2, constants.GAME_WORLD_HEIGHT // 2 - 15))
            screen.blit(pause_text, text_rect)
            
            # Instrucción "Presiona ESC para salir" (NUEVO)
            # (Usamos FONT_NORMAL, que ya está definida al inicio de main)
            esc_text = FONT_NORMAL.render("Presiona ESC para salir", True, (200, 200, 200))
            # (La centramos 30px por debajo del texto principal)
            esc_rect = esc_text.get_rect(center=(constants.WIDTH // 2, constants.GAME_WORLD_HEIGHT // 2 + 15))
            screen.blit(esc_text, esc_rect)
        
        elif current_state == GameState.SELECT_LOAD:
            draw_file_selection_menu(screen, "Cargar Partida", file_menu_cache, file_menu_scroll_offset)
        
        elif current_state == GameState.SELECT_REPLAY:
            draw_file_selection_menu(screen, "Seleccionar Replay", file_menu_cache, file_menu_scroll_offset)
        
        elif current_state == GameState.SHOW_STATS:
            draw_stats_menu(screen)
        
        if current_state == GameState.GAME_OVER:
            overlay = pygame.Surface((constants.WIDTH, constants.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            p1_score = sum(v.score for v in player1_vehicles)
            p2_score = sum(v.score for v in player2_vehicles)
            
            # Panel de resultados más grande
            panel_width = 450
            panel_height = 280
            draw_panel(screen, constants.WIDTH//2 - panel_width//2, 
                      constants.HEIGHT//2 - panel_height//2, panel_width, panel_height)
            
            y_start = constants.HEIGHT//2 - panel_height//2 + 20
            
            # Título
            title_font = pygame.font.SysFont("Arial", 32, bold=True)
            title = title_font.render("JUEGO TERMINADO", True, (255, 255, 0))
            title_rect = title.get_rect(center=(constants.WIDTH//2, y_start + 20))
            screen.blit(title, title_rect)
            
            # Determinar ganador
            y_start += 60
            winner_font = pygame.font.SysFont("Arial", 28, bold=True)
            
            p1_alive = sum(1 for v in player1_vehicles if v.alive)
            p2_alive = sum(1 for v in player2_vehicles if v.alive)

            if p1_alive == 0 and p2_alive > 0:
                winner = winner_font.render("¡GANA JUGADOR 2!", True, (100, 100, 255))
            elif p2_alive == 0 and p1_alive > 0:
                winner = winner_font.render("¡GANA JUGADOR 1!", True, (255, 100, 100))
            elif p1_score > p2_score:
                winner = winner_font.render("¡GANA JUGADOR 1!", True, (255, 100, 100))
            elif p2_score > p1_score:
                winner = winner_font.render("¡GANA JUGADOR 2!", True, (100, 100, 255))
            else:
                winner = winner_font.render("¡EMPATE!", True, (255, 255, 255))
            
            winner_rect = winner.get_rect(center=(constants.WIDTH//2, y_start))
            screen.blit(winner, winner_rect)
            
            # Línea separadora
            y_start += 45
            pygame.draw.line(screen, (100, 100, 100), 
                           (constants.WIDTH//2 - 180, y_start), 
                           (constants.WIDTH//2 + 180, y_start), 2)
            
            # Puntuaciones detalladas
            y_start += 25
            score_font = pygame.font.SysFont("Arial", 22)
            
            # Jugador 1
            p1_text = score_font.render(f"Jugador 1:", True, (255, 150, 150))
            p1_score_text = score_font.render(f"{p1_score} puntos", True, (255, 215, 0))
            screen.blit(p1_text, (constants.WIDTH//2 - 180, y_start))
            screen.blit(p1_score_text, (constants.WIDTH//2 - 50, y_start))
            
            # Estadísticas J1
            y_start += 30
            stats_font = pygame.font.SysFont("Arial", 16)
            p1_alive = sum(1 for v in player1_vehicles if v.alive)
            p1_stats = stats_font.render(f"Sobrevivientes: {p1_alive}/10", True, (200, 200, 200))
            screen.blit(p1_stats, (constants.WIDTH//2 - 180, y_start))
            
            # Jugador 2
            y_start += 35
            p2_text = score_font.render(f"Jugador 2:", True, (150, 150, 255))
            p2_score_text = score_font.render(f"{p2_score} puntos", True, (255, 215, 0))
            screen.blit(p2_text, (constants.WIDTH//2 - 180, y_start))
            screen.blit(p2_score_text, (constants.WIDTH//2 - 50, y_start))
            
            # Estadísticas J2
            y_start += 30
            p2_alive = sum(1 for v in player2_vehicles if v.alive)
            p2_stats = stats_font.render(f"Sobrevivientes: {p2_alive}/10", True, (200, 200, 200))
            screen.blit(p2_stats, (constants.WIDTH//2 - 180, y_start))
            
            # Diferencia de puntos
            y_start += 40
            diff = abs(p1_score - p2_score)
            diff_text = stats_font.render(f"Diferencia: {diff} puntos", True, (180, 180, 180))
            diff_rect = diff_text.get_rect(center=(constants.WIDTH//2, y_start))
            screen.blit(diff_text, diff_rect)
            
            # Instrucciones
            y_start += 35
            restart_font = pygame.font.SysFont("Arial", 18)
            restart = restart_font.render("Presiona R para reiniciar", True, (200, 200, 200))
            restart_rect = restart.get_rect(center=(constants.WIDTH//2, y_start))
            screen.blit(restart, restart_rect)
        
        pygame.display.flip()
        clock.tick(60)