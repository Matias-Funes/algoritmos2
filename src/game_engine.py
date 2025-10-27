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
pygame.display.set_caption("Simulador de Rescate - Algoritmos II")

def main():
    clock = pygame.time.Clock()
    world = World(constants.WIDTH, constants.HEIGHT)

    # BASES: Jugador 1 IZQUIERDA, Jugador 2 DERECHA (según PDF)
    base1_x = 40
    base1_y = constants.HEIGHT // 2
    base2_x = constants.WIDTH - 40
    base2_y = constants.HEIGHT // 2

    # ==========================================
    # JUGADOR 1 - BASE IZQUIERDA (ROJO)
    # ==========================================
    player1_vehicles = []
    
    # 3 Jeeps - distribuidos verticalmente
    for i in range(3):
        y_offset = (i - 1) * 40  # -40, 0, 40
        jeep = Jeep(f"P1_Jeep_{i}", base1_x, base1_y + y_offset, (base1_x, base1_y), (220, 20, 20))
        jeep.strategy = JeepStrategy()
        player1_vehicles.append(jeep)
    
    # 2 Motos - más adelante
    for i in range(2):
        y_offset = (i - 0.5) * 35  # -17.5, 17.5
        moto = Moto(f"P1_Moto_{i}", base1_x + 25, base1_y + y_offset, (base1_x, base1_y), (255, 100, 100))
        moto.strategy = MotoStrategy()
        player1_vehicles.append(moto)
    
    # 2 Camiones - más atrás
    for i in range(2):
        y_offset = (i - 0.5) * 50  # -25, 25
        camion = Camion(f"P1_Camion_{i}", base1_x - 20, base1_y + y_offset, (base1_x, base1_y), (180, 0, 0))
        camion.strategy = CamionStrategy()
        player1_vehicles.append(camion)
    
    # 3 Autos - formación triangular
    auto_positions = [
        (base1_x + 15, base1_y - 25),
        (base1_x + 15, base1_y + 25),
        (base1_x + 35, base1_y)
    ]
    for i, (ax, ay) in enumerate(auto_positions):
        auto = Auto(f"P1_Auto_{i}", ax, ay, (base1_x, base1_y), (200, 50, 50))
        auto.strategy = AutoStrategy()
        player1_vehicles.append(auto)

    # ==========================================
    # JUGADOR 2 - BASE DERECHA (AZUL)
    # ==========================================
    player2_vehicles = []
    
    # 3 Jeeps - distribuidos verticalmente
    for i in range(3):
        y_offset = (i - 1) * 40
        jeep = Jeep(f"P2_Jeep_{i}", base2_x, base2_y + y_offset, (base2_x, base2_y), (20, 20, 220))
        jeep.strategy = AggressiveJeepStrategy()
        player2_vehicles.append(jeep)
    
    # 2 Motos - más adelante (hacia la izquierda)
    for i in range(2):
        y_offset = (i - 0.5) * 35
        moto = Moto(f"P2_Moto_{i}", base2_x - 25, base2_y + y_offset, (base2_x, base2_y), (100, 100, 255))
        moto.strategy = FastMotoStrategy()
        player2_vehicles.append(moto)
    
    # 2 Camiones - más atrás (hacia la derecha)
    for i in range(2):
        y_offset = (i - 0.5) * 50
        camion = Camion(f"P2_Camion_{i}", base2_x + 20, base2_y + y_offset, (base2_x, base2_y), (0, 0, 180))
        camion.strategy = SupportCamionStrategy()
        player2_vehicles.append(camion)
    
    # 3 Autos - formación triangular
    auto_positions = [
        (base2_x - 15, base2_y - 25),
        (base2_x - 15, base2_y + 25),
        (base2_x - 35, base2_y)
    ]
    for i, (ax, ay) in enumerate(auto_positions):
        auto = Auto(f"P2_Auto_{i}", ax, ay, (base2_x, base2_y), (50, 50, 200))
        auto.strategy = BalancedAutoStrategy()
        player2_vehicles.append(auto)

    # Asignar vehículos al mundo
    world.vehicles = player1_vehicles + player2_vehicles
    world.player1_vehicles = player1_vehicles
    world.player2_vehicles = player2_vehicles

    current_state = GameState.PLAYING
    game_time = 0
    max_game_time = 3600  # 60 segundos a 60fps

    # Dibujar zonas de base
    def draw_bases():
        # Base Jugador 1 (izquierda)
        pygame.draw.circle(screen, (220, 20, 20, 100), (base1_x, base1_y), 50, 3)
        font = pygame.font.SysFont(None, 20)
        text = font.render("BASE P1", True, (220, 20, 20))
        screen.blit(text, (base1_x - 30, base1_y - 70))
        
        # Base Jugador 2 (derecha)
        pygame.draw.circle(screen, (20, 20, 220, 100), (base2_x, base2_y), 50, 3)
        text = font.render("BASE P2", True, (20, 20, 220))
        screen.blit(text, (base2_x - 30, base2_y - 70))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_state == GameState.PLAYING:
                        current_state = GameState.PAUSED
                    else:
                        current_state = GameState.PLAYING
                
                # Reinicializar minas G1
                if event.key == pygame.K_i:
                    world.relocate_g1_mines()
                
                # Reset del juego
                if event.key == pygame.K_r:
                    main()  # Reiniciar todo
                    return

        # Lógica del juego
        if current_state == GameState.PLAYING:
            game_time += 1
            world.update_g1_mines()
            
            # Actualizar todos los vehículos
            for vehicle in world.vehicles:
                if vehicle.alive:
                    vehicle.update(world)
            
            # Verificar colisiones entre vehículos de diferentes jugadores
            for v1 in player1_vehicles:
                if not v1.alive:
                    continue
                for v2 in player2_vehicles:
                    if not v2.alive:
                        continue
                    # Colisión solo si están muy cerca y no en sus bases
                    dist = math.hypot(v1.x - v2.x, v1.y - v2.y)
                    if dist < (v1.size + v2.size) / 2 + 5:
                        # Verificar que no estén en sus bases
                        v1_at_base = v1.distance_to_point(*v1.base_position) < 50
                        v2_at_base = v2.distance_to_point(*v2.base_position) < 50
                        
                        if not v1_at_base and not v2_at_base:
                            v1.die()
                            v2.die()
            
            # Verificar fin del juego
            if game_time >= max_game_time:
                current_state = GameState.GAME_OVER

        # Dibujo
        world.draw(screen)
        draw_bases()
        
        # Dibujar vehículos
        for vehicle in world.vehicles:
            vehicle.draw(screen)
        
        # Mostrar estadísticas
        world.draw_team_stats(screen, player1_vehicles, "left", "Jugador 1 (ROJO)")
        world.draw_team_stats(screen, player2_vehicles, "right", "Jugador 2 (AZUL)")
        
        # Mostrar tiempo restante
        font = pygame.font.SysFont(None, 24)
        time_left = max(0, (max_game_time - game_time) // 60)
        time_text = font.render(f"Tiempo: {time_left}s", True, constants.WHITE)
        screen.blit(time_text, (constants.WIDTH//2 - 50, 10))
        
        # Mostrar estado del juego
        if current_state == GameState.PAUSED:
            pause_text = font.render("PAUSADO - ESC para continuar", True, (255, 255, 0))
            screen.blit(pause_text, (constants.WIDTH//2 - 150, constants.HEIGHT//2))
        
        if current_state == GameState.GAME_OVER:
            # Calcular ganador
            p1_score = sum(v.score for v in player1_vehicles)
            p2_score = sum(v.score for v in player2_vehicles)
            
            winner_text = "EMPATE"
            winner_color = (255, 255, 255)
            if p1_score > p2_score:
                winner_text = "¡GANA JUGADOR 1!"
                winner_color = (220, 20, 20)
            elif p2_score > p1_score:
                winner_text = "¡GANA JUGADOR 2!"
                winner_color = (20, 20, 220)
            
            game_over_font = pygame.font.SysFont(None, 48)
            text = game_over_font.render("JUEGO TERMINADO", True, (255, 255, 0))
            screen.blit(text, (constants.WIDTH//2 - 180, constants.HEIGHT//2 - 50))
            
            text = game_over_font.render(winner_text, True, winner_color)
            screen.blit(text, (constants.WIDTH//2 - 150, constants.HEIGHT//2))
            
            restart_font = pygame.font.SysFont(None, 24)
            text = restart_font.render("Presiona R para reiniciar", True, (255, 255, 255))
            screen.blit(text, (constants.WIDTH//2 - 120, constants.HEIGHT//2 + 50))
        
        pygame.display.flip()
        clock.tick(60)