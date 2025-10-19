import pygame
import sys
from .character import Character
from .world import World
from . import constants

##comandos para empezar a trabjar en git bash: 
#cd /c/Users/Mati/ProyectoAlgoritmos2
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


    while True:

        #inicio la ventana
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        #defino los movimientos de los personajes
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            character.move(-5, 0, world)
        if keys[pygame.K_RIGHT]:
            character.move(5, 0, world)
        if keys[pygame.K_UP]:
            character.move(0, -5, world)
        if keys[pygame.K_DOWN]:
            character.move(0, 5, world)

        #dibujo todo
        world.draw(screen)
        #esta linea dibuja el personaje
        character.draw(screen)
        #esta linea dibuja el inventario
        world.draw_inventory(screen, character)
        #este comando actualiza la pantalla
        pygame.display.flip()

        #marco que los movimientos sean a 60 fps
        clock.tick(60)

#este comando corre la funcion main
if __name__ == "__main__":
    main()