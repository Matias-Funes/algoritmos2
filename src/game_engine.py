# src/game_engine.py

import pygame
import sys
import datetime
from .character import Character
from .world import World
from . import constants
from .game_states import GameState
from .database import GameDatabase
import math

class GameEngine:
    def __init__(self):
        """Inicializa Pygame, la ventana y los componentes del juego."""
        pygame.init()
        self.screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
        pygame.display.set_caption("Rescue Simulator")
        
        self.clock = pygame.time.Clock()
        self.current_state = GameState.PLAYING
        
        self.world = World(constants.WIDTH, constants.HEIGHT)
        self.player1 = Character(constants.WIDTH // 4, constants.HEIGHT // 2)
        self.player2 = Character(3 * constants.WIDTH // 4, constants.HEIGHT // 2)
        self.db = GameDatabase()
        
        # Fuentes para el menú
        self.menu_font = pygame.font.SysFont(None, 48)
        self.menu_small_font = pygame.font.SysFont(None, 36)

    def run(self):
        """El bucle principal del juego."""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

    def handle_events(self):
        """Maneja todas las entradas del usuario (teclado, mouse, etc.)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_state == GameState.PLAYING:
                        self.current_state = GameState.PAUSED
                    elif self.current_state == GameState.PAUSED:
                        self.current_state = GameState.PLAYING

                if self.current_state == GameState.PAUSED:
                    self.handle_pause_menu_input(event.key)
                elif self.current_state == GameState.PLAYING:
                    self.handle_playing_input(event.key)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.current_state == GameState.PLAYING:
                mx, my = pygame.mouse.get_pos()
                gx, gy = self.world.pixel_to_cell(mx, my)
                if self.world.is_walkable(gx, gy):
                    self.player1.move_to_cell(gx, gy, self.world)

    def handle_pause_menu_input(self, key):
        """Maneja las teclas del menú de pausa."""
        if key == pygame.K_r:
            self.current_state = GameState.PLAYING
        elif key == pygame.K_g:
            game_data = {
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "player1_score": getattr(self.player1, "score", 0),
                "player2_score": getattr(self.player2, "score", 0),
                "duration": 0,
                "mine_positions": getattr(self.world, "mine_positions", [])
            }
            self.db.save_game_state(game_data)
            print("Partida guardada exitosamente.")
        elif key == pygame.K_q:
            pygame.quit()
            sys.exit()
            
    def handle_playing_input(self, key):
        """Maneja las teclas durante el juego."""
        if key == pygame.K_i:
            self.world.relocate_g1_mines()

        # Movimiento Jugador 1
        start1 = self.world.pixel_to_cell(self.player1.x, self.player1.y)
        if key == pygame.K_LEFT: self.player1.move_to_cell(start1[0] - 1, start1[1], self.world)
        if key == pygame.K_RIGHT: self.player1.move_to_cell(start1[0] + 1, start1[1], self.world)
        if key == pygame.K_UP: self.player1.move_to_cell(start1[0], start1[1] - 1, self.world)
        if key == pygame.K_DOWN: self.player1.move_to_cell(start1[0], start1[1] + 1, self.world)

        # Movimiento Jugador 2
        start2 = self.world.pixel_to_cell(self.player2.x, self.player2.y)
        if key == pygame.K_a: self.player2.move_to_cell(start2[0] - 1, start2[1], self.world)
        if key == pygame.K_d: self.player2.move_to_cell(start2[0] + 1, start2[1], self.world)
        if key == pygame.K_w: self.player2.move_to_cell(start2[0], start2[1] - 1, self.world)
        if key == pygame.K_s: self.player2.move_to_cell(start2[0], start2[1] + 1, self.world)

    def update(self):
        """Actualiza la lógica del juego."""
        if self.current_state != GameState.PLAYING:
            return

        self.player1.update(self.world)
        self.player2.update(self.world)
        self.world.update_g1_mines()

        if (math.hypot(self.player1.x - self.player2.x, self.player1.y - self.player2.y) <
            (self.player1.size + self.player2.size) / 2):
            self.player1.die()
            self.player2.die()
    
    def draw(self):
        """Dibuja todos los elementos en la pantalla."""
        self.world.draw(self.screen)
        self.player1.draw(self.screen)
        self.player2.draw(self.screen)
        self.world.draw_inventory(self.screen, self.player1, position="left", player_name="Jugador 1")
        self.world.draw_inventory(self.screen, self.player2, position="right", player_name="Jugador 2")

        if self.current_state == GameState.PAUSED:
            self.draw_pause_menu()

        pygame.display.flip()

    def draw_pause_menu(self):
        """Dibuja el menú de pausa."""
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title = self.menu_font.render("Juego en Pausa", True, (255, 255, 255))
        self.screen.blit(title, (constants.WIDTH // 2 - title.get_width() // 2, 150))

        options = ["R - Reanudar", "G - Guardar Partida", "Q - Salir del Juego"]
        for i, text in enumerate(options):
            opt = self.menu_small_font.render(text, True, (255, 255, 255))
            self.screen.blit(opt, (constants.WIDTH // 2 - opt.get_width() // 2, 250 + i * 50))