import pygame
import sys
from .world import World
from . import constants
from .game_states import GameState
import math
from config.strategies.player1_strategies import JeepStrategy, MotoStrategy, CamionStrategy, AutoStrategy
from config.strategies.player2_strategies import AggressiveJeepStrategy, FastMotoStrategy, SupportCamionStrategy, BalancedAutoStrategy
from src.aircraft import Jeep, Moto, Camion, Auto

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
    world = World(constants.WIDTH, constants.HEIGHT)

    # Bases con mejor posicionamiento
    base1_x = 50
    base1_y = constants.HEIGHT // 2
    base2_x = constants.WIDTH - 50
    base2_y = constants.HEIGHT // 2

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

    current_state = GameState.PLAYING
    game_time = 0
    max_game_time = 7200  # 120 segundos

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
    
    # FUNCION QUE DIBUJA EL MENU DE PAUSA
    def draw_pause_menu(surface):
        """Dibuja un menú de pausa interactivo y estilizado."""
        # Fondo oscuro semitransparente
        overlay = pygame.Surface((constants.WIDTH, constants.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # Genero el panel
        panel_width = 350
        panel_height = 260
        panel_x = constants.WIDTH // 2 - panel_width // 2
        panel_y = constants.HEIGHT // 2 - panel_height // 2
        draw_panel(surface, panel_x, panel_y, panel_width, panel_height, (40, 50, 60))

        # Título del Menú
        y_pos = panel_y + 30
        title = FONT_TITLE.render("JUEGO EN PAUSA", True, (255, 215, 0))
        title_rect = title.get_rect(center=(constants.WIDTH // 2, y_pos))
        surface.blit(title, title_rect)
        y_pos += 55

        # Opciones del menú
        options = {
            "Reanudar": "[ESC]",
            "Nueva Simulación": "[R]", 
            "Guardar Partida": "[G]",
            "Salir del Juego": "[Q]"
        }

        for text, key in options.items():
            option_text = FONT_NORMAL.render(text, True, (220, 220, 220))
            key_text = FONT_NORMAL.render(key, True, (255, 215, 0))
            
            surface.blit(option_text, (panel_x + 40, y_pos))
            surface.blit(key_text, (panel_x + panel_width - 40 - key_text.get_width(), y_pos))
            y_pos += 40

    # Variables para efectos
    last_p1_alive = 10
    last_p2_alive = 10

    while True:
        # Bucle y manejo de eventos al pausar 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                # La tecla ESC siempre alterna entre jugar y pausar
                if event.key == pygame.K_ESCAPE:
                    current_state = GameState.PAUSED if current_state == GameState.PLAYING else GameState.PLAYING
                
                # Si estamos en pausa, escuchamos las teclas del menú
                if current_state == GameState.PAUSED:
                    if event.key == pygame.K_r:
                        main()  # Llama a main de nuevo para reiniciar
                        return  # Es importante salir de la instancia actual de main
                    if event.key == pygame.K_g:
                        print("Acción: Guardar partida (lógica a implementar)")
                        # Aquí iría la llamada a la función de guardado de la base de datos
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

                # Si estamos jugando, escuchamos las teclas del juego
                if current_state == GameState.PLAYING:
                    if event.key == pygame.K_i:
                        world.relocate_g1_mines()
                
                # Si el juego ha terminado, la 'R' reinicia
                if current_state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        main()  # Llama a main de nuevo para reiniciar
                        return

        # Lógica del juego
        if current_state == GameState.PLAYING:
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
                current_state = GameState.GAME_OVER

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
            text1 = banner_font.render("⚠ RECURSOS AGOTADOS ⚠", True, (255, 215, 0))
            text1_rect = text1.get_rect(center=(constants.WIDTH//2, banner_y + 18))
            screen.blit(text1, text1_rect)
            
            info_font = pygame.font.SysFont("Arial", 18)
            text2 = info_font.render("Todos los vehículos regresando a base...", True, (255, 255, 255))
            text2_rect = text2.get_rect(center=(constants.WIDTH//2, banner_y + 42))
            screen.blit(text2, text2_rect)
        
        # Estado del juego
        #Dibujo el menu de pausa 
        if current_state == GameState.PAUSED:
            # Llamamos a nuestra nueva función de menú en lugar del texto simple
            draw_pause_menu(screen)
        
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
            title = title_font.render("🏁 JUEGO TERMINADO", True, (255, 255, 0))
            title_rect = title.get_rect(center=(constants.WIDTH//2, y_start + 20))
            screen.blit(title, title_rect)
            
            # Determinar ganador
            y_start += 60
            winner_font = pygame.font.SysFont("Arial", 28, bold=True)
            if p1_score > p2_score:
                winner = winner_font.render("¡GANA JUGADOR 1!", True, (255, 100, 100))
                winner_icon = "🔴"
            elif p2_score > p1_score:
                winner = winner_font.render("¡GANA JUGADOR 2!", True, (100, 100, 255))
                winner_icon = "🔵"
            else:
                winner = winner_font.render("¡EMPATE!", True, (255, 255, 255))
                winner_icon = "🤝"
            
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