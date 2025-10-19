import pygame
import sys
from .character import Character
from .world import World
from . import constants
from .game_states import GameState


##comandos para empezar a trabjar en git bash: 
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
    character = Character(constants.WIDTH//2, constants.HEIGHT//2)  
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
                # mover por teclas: una celda
                if current_state == GameState.PLAYING:
                    start = world.pixel_to_cell(character.x, character.y)
                    if event.key == pygame.K_LEFT:
                        character.move_to_cell(start[0] - 1, start[1], world)
                    if event.key == pygame.K_RIGHT:
                        character.move_to_cell(start[0] + 1, start[1], world)
                    if event.key == pygame.K_UP:
                        character.move_to_cell(start[0], start[1] - 1, world)
                    if event.key == pygame.K_DOWN:
                        character.move_to_cell(start[0], start[1] + 1, world)
            #esto hace que el personaje se mueva a la celda clickeada
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and current_state == GameState.PLAYING:
                mx, my = pygame.mouse.get_pos()
                gx, gy = world.pixel_to_cell(mx, my)
                if world.is_walkable(gx, gy):
                    character.move_to_cell(gx, gy, world)

        # lógica del juego
        if current_state == GameState.PLAYING:
            character.update(world)

        # dibujo
        world.draw(screen)
        character.draw(screen)
        world.draw_inventory(screen, character)
        pygame.display.flip()
        clock.tick(60)

