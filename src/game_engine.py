import pygame
import sys
from .character import Character
from .world import World
from . import constants
from .game_states import GameState
import math
from config.strategies.player1_strategies import AutoStrategy
from config.strategies.player2_strategies import BalancedAutoStrategy
from src.character import Character

##comandos para empezar a trabjar en git bash:
# cd ~/rescue_simulator
#source .venv/Scripts/activate
#python rescue_simulator.py

#inicializar pygame
pygame.init()


#crear ventana
screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
pygame.display.set_caption("Rescue Simulator")

#estructura principal del juego
def main():
    clock = pygame.time.Clock()
    world = World(constants.WIDTH, constants.HEIGHT)

    player1 = Character(constants.WIDTH//4, constants.HEIGHT//2, strategy=AutoStrategy())
    player2 = Character(3*constants.WIDTH//4, constants.HEIGHT//2, strategy=BalancedAutoStrategy())

    world.vehicles = [player1, player2]  # para que find_nearest_enemy funcione

    current_state = GameState.PLAYING 

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            #esto permite pausar y reanudar el juego con ESCAPE
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_state == GameState.PLAYING:
                        current_state = GameState.PAUSED
                    else:
                        current_state = GameState.PLAYING
                #Tecla para inicializar minas
                if event.key == pygame.K_i:
                    world.relocate_g1_mines()

                # mover por teclas: una celda
                # if current_state == GameState.PLAYING:
                    # start1 = world.pixel_to_cell(player1.x, player1.y)
                    # if event.key == pygame.K_LEFT:
                        # player1.move_to_cell(start1[0] - 1, start1[1], world)
                    # if event.key == pygame.K_RIGHT:
                        # player1.move_to_cell(start1[0] + 1, start1[1], world)
                    # if event.key == pygame.K_UP:
                        # player1.move_to_cell(start1[0], start1[1] - 1, world)
                    # if event.key == pygame.K_DOWN:
                        # player1.move_to_cell(start1[0], start1[1] + 1, world)
                    # # Controles para player2 (WASD)
                    # start2 = world.pixel_to_cell(player2.x, player2.y)
                    # if event.key == pygame.K_a:
                        # player2.move_to_cell(start2[0] - 1, start2[1], world)
                    # if event.key == pygame.K_d:
                        # player2.move_to_cell(start2[0] + 1, start2[1], world)
                    # if event.key == pygame.K_w:
                        # player2.move_to_cell(start2[0], start2[1] - 1, world)
                    # if event.key == pygame.K_s:
                        # player2.move_to_cell(start2[0], start2[1] + 1, world)
                    
       

                    
                    # Actualizar minas G1
                    world.update_g1_mines()  
                    player1.update(world)
                    player2.update(world)

                    # Verificar colisión entre jugadores
                    # if (math.hypot(player1.x - player2.x, player1.y - player2.y) < 
                        # (player1.size + player2.size)/2):
                        # player1.die()
                        # player2.die()
            
            #esto hace que el personaje se mueva a la celda clickeada
            # if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and current_state == GameState.PLAYING:
                # mx, my = pygame.mouse.get_pos()
                # gx, gy = world.pixel_to_cell(mx, my)
                # if world.is_walkable(gx, gy):
                    # player1.move_to_cell(gx, gy, world)

        # lógica del juego
        if current_state == GameState.PLAYING:
            world.update_g1_mines()
            player1.update(world)
            player2.update(world)
            
             # Colisión entre jugadores
            if (math.hypot(player1.x - player2.x, player1.y - player2.y) < (player1.size + player2.size)/2):
                player1.die()
                player2.die()

        # dibujo
        world.draw(screen)
        player1.draw(screen)
        player2.draw(screen)
        world.draw_inventory(screen, player1, position="left", player_name="Jugador 1")
        world.draw_inventory(screen, player2, position="right", player_name="Jugador 2")
        pygame.display.flip()
        clock.tick(60)

