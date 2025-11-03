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
from .elements import Person, Merchandise, Mine

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
    # (Añade BaseStrategy si alguna vez la usas directamente)
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

    # ==========================================
    # JUGADOR 1 - ROJO (Izquierda)
    # ==========================================
    player1_vehicles = []
    
    # 3 Jeeps en formación escalonada
    for i in range(3):
        y_offset = (i - 1) * 45
        jeep = Jeep(f"P1_Jeep_{i}", base1_x + i*8, base1_y + y_offset, 
                   (base1_x, base1_y), (220, 20, 20))
        jeep.strategy = JeepStrategy()
        player1_vehicles.append(jeep)
    
    # 2 Motos adelante
    for i in range(2):
        y_offset = (i - 0.5) * 40
        moto = Moto(f"P1_Moto_{i}", base1_x + 30, base1_y + y_offset, 
                   (base1_x, base1_y), (255, 80, 80))
        moto.strategy = MotoStrategy()
        player1_vehicles.append(moto)
    
    # 2 Camiones atrás
    for i in range(2):
        y_offset = (i - 0.5) * 55
        camion = Camion(f"P1_Camion_{i}", base1_x - 25, base1_y + y_offset, 
                       (base1_x, base1_y), (180, 0, 0))
        camion.strategy = CamionStrategy()
        player1_vehicles.append(camion)
    
    # 3 Autos en V
    auto_positions = [
        (base1_x + 20, base1_y - 30),
        (base1_x + 20, base1_y + 30),
        (base1_x + 40, base1_y)
    ]
    for i, (ax, ay) in enumerate(auto_positions):
        auto = Auto(f"P1_Auto_{i}", ax, ay, (base1_x, base1_y), (200, 40, 40))
        auto.strategy = AutoStrategy()
        player1_vehicles.append(auto)

    # ==========================================
    # JUGADOR 2 - AZUL (Derecha)
    # ==========================================
    player2_vehicles = []
    
    # 3 Jeeps en formación escalonada
    for i in range(3):
        y_offset = (i - 1) * 45
        jeep = Jeep(f"P2_Jeep_{i}", base2_x - i*8, base2_y + y_offset, 
                   (base2_x, base2_y), (20, 20, 220))
        jeep.strategy = AggressiveJeepStrategy()
        player2_vehicles.append(jeep)
    
    # 2 Motos adelante
    for i in range(2):
        y_offset = (i - 0.5) * 40
        moto = Moto(f"P2_Moto_{i}", base2_x - 30, base2_y + y_offset, 
                   (base2_x, base2_y), (80, 80, 255))
        moto.strategy = FastMotoStrategy()
        player2_vehicles.append(moto)
    
    # 2 Camiones atrás
    for i in range(2):
        y_offset = (i - 0.5) * 55
        camion = Camion(f"P2_Camion_{i}", base2_x + 25, base2_y + y_offset, 
                       (base2_x, base2_y), (0, 0, 180))
        camion.strategy = SupportCamionStrategy()
        player2_vehicles.append(camion)
    
    # 3 Autos en V
    auto_positions = [
        (base2_x - 20, base2_y - 30),
        (base2_x - 20, base2_y + 30),
        (base2_x - 40, base2_y)
    ]
    for i, (ax, ay) in enumerate(auto_positions):
        auto = Auto(f"P2_Auto_{i}", ax, ay, (base2_x, base2_y), (40, 40, 200))
        auto.strategy = BalancedAutoStrategy()
        player2_vehicles.append(auto)

    world.vehicles = player1_vehicles + player2_vehicles
    world.player1_vehicles = player1_vehicles
    world.player2_vehicles = player2_vehicles

    current_state = GameState.PREPARATION
    game_time = 0
    max_game_time = 7200  # 120 segundos
    file_menu_cache = [] # Lista genérica para guardar archivos (partidas O replays)
    file_menu_buttons = [] # Lista genérica para los rects de los botones
    file_menu_scroll_offset = 0
    previous_state = GameState.PREPARATION # Para saber a dónde volver
    
    # Variables para el REPLAY
    replay_buffer = [] # Aquí se guardan las "fotos" de la simulación
    replay_data = [] # Aquí se guarda el replay que estamos VIENDO
    current_replay_frame = 0 # El "cabezal" de la reproducción
    
    
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
    

    # --- NUEVA FUNCIÓN HELPER ---
    def draw_button_text(surface, text, rect, font=FONT_NORMAL):
        """Helper para centrar texto en un botón"""
        text_surf = font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

    #FUNCIÓN DE DIBUJO DEL PANEL
    def draw_control_panel(surface, state):
        """Dibuja el panel de control fijo en la parte inferior."""
        # Fondo del panel
        panel_rect = pygame.Rect(0, constants.UI_PANEL_Y, constants.WIDTH, constants.UI_PANEL_HEIGHT)
        draw_gradient_rect(surface, (30, 30, 40), (50, 50, 60), panel_rect)
        pygame.draw.line(surface, (100, 100, 110), (0, constants.UI_PANEL_Y), (constants.WIDTH, constants.UI_PANEL_Y), 2)
        
        # --- Colores de Botones (con lógica de estado) ---
        color_disabled = (40, 40, 40)
        color_default = (80, 80, 90)
        color_play = (60, 150, 60)
        color_pause = (150, 60, 60)
        
        # Lógica de habilitación
        init_enabled = state == GameState.PREPARATION
        play_enabled = state == GameState.PREPARATION or state == GameState.PAUSED
        pause_enabled = state == GameState.PLAYING
        init_enabled = state == GameState.PREPARATION
        play_enabled = state == GameState.PREPARATION or state == GameState.PAUSED
        pause_enabled = state == GameState.PLAYING
        save_enabled = state == GameState.PLAYING or state == GameState.PAUSED
        load_enabled = state == GameState.PREPARATION or state == GameState.PAUSED # <-- AÑADE ESTA LÍNEA
        
        # Asignar colores
        color_init = color_default if init_enabled else color_disabled
        color_play_btn = color_play if play_enabled else color_disabled
        color_pause_btn = color_pause if pause_enabled else color_disabled
        
        # Dibujar botones
        pygame.draw.rect(surface, color_init, btn_init, border_radius=5)
        pygame.draw.rect(surface, color_play_btn, btn_play, border_radius=5)
        pygame.draw.rect(surface, color_pause_btn, btn_pause, border_radius=5)
        
        # (El resto de botones por ahora)
        pygame.draw.rect(surface, color_default, btn_step_back, border_radius=5)
        pygame.draw.rect(surface, color_default, btn_step_fwd, border_radius=5)
        pygame.draw.rect(surface, color_default, btn_save, border_radius=5)
        color_load_btn = color_default if load_enabled else color_disabled
        pygame.draw.rect(surface, color_load_btn, btn_load, border_radius=5)
        pygame.draw.rect(surface, color_default, btn_replay, border_radius=5)
        pygame.draw.rect(surface, color_default, btn_stats, border_radius=5)
        
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
        
    def draw_file_selection_menu(surface, title, file_list, scroll_offset):
        """Dibuja un menú genérico para seleccionar un archivo (guardado o replay)."""
        nonlocal file_menu_buttons # Usamos la variable global
        file_menu_buttons.clear() # Limpiamos los botones

        # 1. Fondo oscuro
        overlay = pygame.Surface((constants.WIDTH, constants.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        # 2. Panel principal
        panel_width = 500
        panel_height = 400
        panel_x = constants.WIDTH // 2 - panel_width // 2
        panel_y = constants.HEIGHT // 2 - panel_height // 2
        draw_panel(surface, panel_x, panel_y, panel_width, panel_height, (40, 50, 60))

        # 3. Título (ahora es un parámetro)
        title_surf = FONT_TITLE.render(title, True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(constants.WIDTH // 2, panel_y + 40))
        surface.blit(title_surf, title_rect)

        # 4. Dibujar la lista de archivos (ahora es un parámetro)
        y_pos = panel_y + 80
        files_to_show = file_list[scroll_offset : scroll_offset + 5]

        for i, filename in enumerate(files_to_show):
            # Limpiar el nombre para que sea más legible
            display_name = filename.replace(".pkl", "").replace("_", "  ")
            
            btn_rect = pygame.Rect(panel_x + 20, y_pos, panel_width - 40, 40)
            file_menu_buttons.append((btn_rect, filename)) # Guardamos rect y nombre

            mouse_pos = pygame.mouse.get_pos()
            if btn_rect.collidepoint(mouse_pos):
                pygame.draw.rect(surface, (100, 110, 120), btn_rect, border_radius=5)
            else:
                pygame.draw.rect(surface, (60, 70, 80), btn_rect, border_radius=5)
            
            text_surf = FONT_NORMAL.render(display_name, True, (255, 255, 255))
            surface.blit(text_surf, (btn_rect.x + 15, btn_rect.y + 10))
            y_pos += 50
        
        # 5. Botón de Cancelar
        btn_cancel_rect = pygame.Rect(constants.WIDTH // 2 - 50, panel_y + panel_height - 60, 100, 40)
        file_menu_buttons.append((btn_cancel_rect, "CANCEL"))
        
        if btn_cancel_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(surface, (180, 50, 50), btn_cancel_rect, border_radius=5)
        else:
            pygame.draw.rect(surface, (150, 30, 30), btn_cancel_rect, border_radius=5)
        draw_button_text(surface, "Cancelar", btn_cancel_rect)
    
    
    # Variables para efectos
    last_p1_alive = 10
    last_p2_alive = 10

    def get_full_game_state():
        """
        Recopila el estado de todos los objetos del juego y lo empaqueta.
        """
        print("Creando 'foto' del estado del juego...")
        # 1. Guardar el estado de todos los vehículos
        p1_vehicles_state = [v.get_state() for v in player1_vehicles]
        p2_vehicles_state = [v.get_state() for v in player2_vehicles]
        
        # 2. Guardar el estado del mundo (minas, recursos, etc.)
        world_state = world.get_state() # Llama al get_state() de world
        
        # 3. Empaquetar todo en un solo diccionario
        game_state_data = {
            "game_time": game_time,
            "world": world_state,
            "player1_vehicles": p1_vehicles_state,
            "player2_vehicles": p2_vehicles_state
        }
        return game_state_data

    def load_game_from_data(data):
        """
        Reconstruye el estado completo del juego a partir de un diccionario de datos.
        """
        nonlocal game_time, current_state # ¡Importante!
        
        print("Cargando partida...")
        
        # 1. Restaurar el mundo
        world.load_state(data['world'])
        
        # 2. Limpiar flotas actuales
        player1_vehicles.clear()
        player2_vehicles.clear()

        # Diccionario para recrear vehículos por su tipo
        vehicle_classes = {
            "jeep": Jeep,
            "moto": Moto,
            "camion": Camion,
            "auto": Auto
        }
        
        # 3. Reconstruir Flota del Jugador 1
        for v_data in data.get('player1_vehicles', []):
            v_type = v_data.get('vehicle_type')
            if v_type in vehicle_classes:
                # Crear la nueva instancia del vehículo
                cls = vehicle_classes[v_type]
                new_v = cls(v_data['id'], v_data['x'], v_data['y'], 
                            v_data['base_position'], v_data['color'])
                
                # Restaurar todos los atributos guardados
                new_v.trips_left = v_data.get('trips_left', 1)
                new_v.alive = v_data.get('alive', True)
                new_v.score = v_data.get('score', 0)
                new_v.returning_to_base = v_data.get('returning_to_base', False)
                new_v.at_base = v_data.get('at_base', False)
                new_v.forced_return = v_data.get('forced_return', False)
                new_v.speed = v_data.get('speed', 2)

                # Reconstruir la carga (importante!)
                new_v.cargo = []
                for item_type in v_data.get('cargo', []):
                    if item_type == 'person':
                        # Creamos un objeto 'Person' temporal. Solo nos importa su .value
                        new_v.cargo.append(Person(0,0)) 
                    elif item_type in constants.MERCH_COUNTS:
                        # Creamos un objeto 'Merchandise' temporal.
                        new_v.cargo.append(Merchandise(0,0, item_type))
                
                # Restaurar el "cerebro" (la estrategia)
                strategy_name = v_data.get('strategy_name')
                if strategy_name in STRATEGY_MAP:
                    new_v.strategy = STRATEGY_MAP[strategy_name]() # Crea una nueva instancia
                else:
                    new_v.strategy = None
                    
                player1_vehicles.append(new_v)

        # 4. Reconstruir Flota del Jugador 2
        for v_data in data.get('player2_vehicles', []):
            v_type = v_data.get('vehicle_type')
            if v_type in vehicle_classes:
                cls = vehicle_classes[v_type]
                new_v = cls(v_data['id'], v_data['x'], v_data['y'], 
                            v_data['base_position'], v_data['color'])
                
                # (Copiar y pegar la misma lógica de restauración de atributos de arriba)
                new_v.trips_left = v_data.get('trips_left', 1)
                new_v.alive = v_data.get('alive', True)
                new_v.score = v_data.get('score', 0)
                new_v.returning_to_base = v_data.get('returning_to_base', False)
                new_v.at_base = v_data.get('at_base', False)
                new_v.forced_return = v_data.get('forced_return', False)
                new_v.speed = v_data.get('speed', 2)
                
                new_v.cargo = []
                for item_type in v_data.get('cargo', []):
                    if item_type == 'person':
                        new_v.cargo.append(Person(0,0))
                    elif item_type in constants.MERCH_COUNTS:
                        new_v.cargo.append(Merchandise(0,0, item_type))
                
                # Restaurar el "cerebro" (la estrategia)
                strategy_name = v_data.get('strategy_name')
                if strategy_name in STRATEGY_MAP:
                    new_v.strategy = STRATEGY_MAP[strategy_name]() # Crea una nueva instancia
                else:
                    new_v.strategy = None
                     
                player2_vehicles.append(new_v)

        # 5. Actualizar la lista de vehículos del mundo
        world.vehicles = player1_vehicles + player2_vehicles
        
        # 6. Restaurar el tiempo y pausar el juego
        game_time = data.get('game_time', 0)
        current_state = GameState.PAUSED # Carga la partida en pausa
        print("¡Partida cargada! El juego está en pausa.")
    
    
    while True:
        # Bucle y manejo de eventos al pausar 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # --- MANEJO DE CLICS DEL MOUSE ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Clic izquierdo
                    pos = pygame.mouse.get_pos()

                    # --- Lógica si estamos en un MENÚ DE SELECCIÓN DE ARCHIVO ---
                    if current_state in (GameState.SELECT_LOAD, GameState.SELECT_REPLAY):
                        for rect, filename in file_menu_buttons:
                            if rect.collidepoint(pos):
                                if filename == "CANCEL":
                                    current_state = previous_state # Volver a PREPARATION o PAUSED
                                
                                # Si NO es "cancelar", es un archivo
                                else:
                                    try:
                                        # -- Lógica dividida --
                                        if current_state == GameState.SELECT_LOAD:
                                            print(f"Cargando partida: {filename}")
                                            with open(filename, 'rb') as f:
                                                game_data = pickle.load(f)
                                            load_game_from_data(game_data)
                                            # (load_game_from_data ya pone el estado en PAUSED)
                                        
                                        elif current_state == GameState.SELECT_REPLAY:
                                            print(f"Cargando replay: {filename}")
                                            with open(filename, 'rb') as f:
                                                replay_data = pickle.load(f) # Carga la lista de "fotos"
                                            current_replay_frame = 0 # Reinicia el cabezal
                                            current_state = GameState.REPLAYING # Inicia el modo replay
                                            
                                    except Exception as e:
                                        print(f"Error al cargar el archivo {filename}: {e}")
                                
                                break # Salir del bucle for (ya encontramos un clic)
                    
                    # --- Lógica si estamos en el JUEGO (panel de control) ---
                    elif current_state != GameState.GAME_OVER:
                        if btn_init.collidepoint(pos) and current_state == GameState.PREPARATION:
                            world.initialize_map_elements()
                                
                        elif btn_play.collidepoint(pos) and (current_state == GameState.PREPARATION or current_state == GameState.PAUSED):
                            if current_state == GameState.PREPARATION and not world.resources:
                                print("Presiona 'Init' primero para generar el mapa.")
                                continue
                            current_state = GameState.PLAYING
                        
                        elif btn_pause.collidepoint(pos) and current_state == GameState.PLAYING:
                            current_state = GameState.PAUSED
                        
                        elif btn_save.collidepoint(pos) and (current_state == GameState.PLAYING or current_state == GameState.PAUSED):
                            # ... (tu código de guardar partida no cambia) ...
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

                        # --- NUEVO: Lógica del botón Replay ---
                        elif btn_replay.collidepoint(pos) and (current_state == GameState.PREPARATION or current_state == GameState.PAUSED):
                            print("Abriendo menú de Replay...")
                            file_menu_cache = glob.glob("Replay_*.pkl")
                            file_menu_cache.sort(key=os.path.getctime, reverse=True)
                            file_menu_scroll_offset = 0
                            previous_state = current_state
                            current_state = GameState.SELECT_REPLAY

            # --- MANEJO DE TECLADO ---
            if event.type == pygame.KEYDOWN:
                if current_state in (GameState.SELECT_LOAD, GameState.SELECT_REPLAY):
                    # Scroll del menú de archivos con flechas
                    if event.key == pygame.K_DOWN:
                        file_menu_scroll_offset = min(file_menu_scroll_offset + 1, max(0, len(file_menu_cache) - 5))
                    elif event.key == pygame.K_UP:
                        file_menu_scroll_offset = max(0, file_menu_scroll_offset - 1)
                    elif event.key == pygame.K_ESCAPE:
                        current_state = previous_state # Salir con ESC

                elif current_state == GameState.PLAYING:
                    if event.key == pygame.K_i:
                        world.relocate_g1_mines()
                
                elif current_state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        main()
                        return

        # Lógica del juego
        if current_state == GameState.PLAYING:
            # 1. GRABAR FOTOGRAMA PARA REPLAY
            # Guardamos la "foto" del estado actual ANTES de que algo se mueva
            try:
                replay_buffer.append(get_full_game_state())
            except Exception as e:
                print(f"Error al grabar fotograma de replay: {e}")
            game_time += 1
            world.update_g1_mines()
    
            # VERIFICAR SI SE TERMINARON LOS RECURSOS
            if len(world.resources) == 0 and not hasattr(world, 'ending_phase'):
                # Iniciar fase de finalización
                world.ending_phase = True
                world.ending_timer = 0
                # Forzar a todos los vehículos a regresar
                for vehicle in world.vehicles:
                    if vehicle.alive:
                        vehicle.force_return_to_base()
            
            # Si está en fase de finalización
            if hasattr(world, 'ending_phase') and world.ending_phase:
                world.ending_timer += 1
                
                # Verificar si todos llegaron a base o pasó tiempo suficiente
                all_at_base = all(v.at_base or not v.alive for v in world.vehicles)
                
                if all_at_base or world.ending_timer > 300:  # 5 segundos máximo
                    if replay_buffer:
                        print("Guardando Replay (fin de recursos)...")
                        replay_name = f"Replay_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pkl"
                        try:
                            with open(replay_name, 'wb') as f:
                                pickle.dump(replay_buffer, f)
                            print(f"Replay guardado exitosamente en {replay_name}")
                        except Exception as e:
                            print(f"Error al guardar el replay: {e}")
                        replay_buffer.clear() # Limpiar para la próxima partida
                            
                    current_state = GameState.GAME_OVER
            
            # Actualizar vehículos
            for vehicle in world.vehicles:
                if vehicle.alive:
                    vehicle.update(world)
            
            # Detectar destrucciones para efectos
            p1_alive = sum(1 for v in player1_vehicles if v.alive)
            p2_alive = sum(1 for v in player2_vehicles if v.alive)
            
            if p1_alive < last_p1_alive:
                # Encontrar vehículo destruido
                for v in player1_vehicles:
                    if not v.alive and hasattr(v, 'last_x'):
                        create_explosion(v.last_x, v.last_y, (255, 0, 0))
            
            if p2_alive < last_p2_alive:
                for v in player2_vehicles:
                    if not v.alive and hasattr(v, 'last_x'):
                        create_explosion(v.last_x, v.last_y, (0, 0, 255))
            
            last_p1_alive = p1_alive
            last_p2_alive = p2_alive
            
            # Guardar última posición para explosiones
            for v in world.vehicles:
                if v.alive:
                    v.last_x = v.x
                    v.last_y = v.y
            
            # Colisiones entre jugadores
            for v1 in player1_vehicles:
                if not v1.alive:
                    continue
                for v2 in player2_vehicles:
                    if not v2.alive:
                        continue
                    dist = math.hypot(v1.x - v2.x, v1.y - v2.y)
                    if dist < (v1.size + v2.size) / 2 + 5:
                        v1_at_base = v1.distance_to_point(*v1.base_position) < 50
                        v2_at_base = v2.distance_to_point(*v2.base_position) < 50
                        
                        if not v1_at_base and not v2_at_base:
                            create_explosion(v1.x, v1.y, (255, 128, 0))
                            v1.die()
                            v2.die()
            
            if game_time >= max_game_time:
                if replay_buffer:
                    print("Guardando Replay (fin de recursos)...")
                    replay_name = f"Replay_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pkl"
                    try:
                        with open(replay_name, 'wb') as f:
                            pickle.dump(replay_buffer, f)
                        print(f"Replay guardado exitosamente en {replay_name}")
                    except Exception as e:
                        print(f"Error al guardar el replay: {e}")
                    replay_buffer.clear() # Limpiar para la próxima partida
                current_state = GameState.GAME_OVER
                
                        
        elif current_state == GameState.REPLAYING:
            # Modo "Reproductor de Video"
            if current_replay_frame < len(replay_data):
                try:
                    # 1. Cargar el fotograma (la "foto")
                    current_frame_data = replay_data[current_replay_frame]
                    # 2. Reconstruir el estado (usa la misma función que Cargar)
                    load_game_from_data(current_frame_data)
                    # 3. Avanzar al siguiente fotograma
                    current_replay_frame += 1
                    # 4. Forzar el estado a PAUSA (para que se vea 1 fotograma)
                    current_state = GameState.REPLAYING # Se mantiene en replay
                except Exception as e:
                    print(f"Error al reproducir fotograma de replay: {e}")
                    current_state = GameState.PAUSED # Salir a pausa si hay error
            else:
                print("Replay finalizado.")
                current_state = GameState.PAUSED # Queda en pausa al final
                

        # Dibujo
        world.draw(screen)
        draw_bases()
        
        # Dibujar vehículos
        for vehicle in world.vehicles:
            vehicle.draw(screen)
        
        # Efectos de partículas
        update_particles()
        
        # HUD moderno
        world.draw_premium_hud(screen, player1_vehicles, player2_vehicles, game_time, max_game_time)
        
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
        draw_control_panel(screen, current_state)
        
        # Estado del juego
        # --- DIBUJAR EL PANEL DE CONTROL FIJO ---
        # (No lo dibujamos si estamos en un menú de selección)
        if current_state not in (GameState.SELECT_LOAD, GameState.SELECT_REPLAY):
            draw_control_panel(screen, current_state)
        
        # --- DIBUJAR ESTADOS SUPERPUESTOS ---
        if current_state == GameState.PAUSED:
            # ... (tu código de pausa no cambia) ...
            overlay = pygame.Surface((constants.WIDTH, constants.GAME_WORLD_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            pause_text = FONT_TITLE.render("PAUSADO", True, (255, 255, 0))
            text_rect = pause_text.get_rect(center=(constants.WIDTH // 2, constants.GAME_WORLD_HEIGHT // 2))
            screen.blit(pause_text, text_rect)

        elif current_state == GameState.SELECT_LOAD:
            draw_file_selection_menu(screen, "Cargar Partida", file_menu_cache, file_menu_scroll_offset)
        
        elif current_state == GameState.SELECT_REPLAY:
            draw_file_selection_menu(screen, "Seleccionar Replay", file_menu_cache, file_menu_scroll_offset)
        
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
            if p1_score > p2_score:
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