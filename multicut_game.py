import pygame
import sys

from button import Button
from game_modes import ClassicGameMode
from enum import Enum
from functools import partial


class GameMode(Enum):
    Classic = 1


class MulticutGame:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    SCREEN_COLOR = (255, 255, 255)

    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()

        # Set up font
        self.font = pygame.font.SysFont('Ariel', 32)
        self.text = self.font.render("0", True, (0, 0, 0))

        # Set up screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SCALED)
        pygame.display.set_caption("Multicut Game")

        self.screen.fill((255, 255, 255))
        pygame.display.update()

        # Set up buttons
        self.buttons = []
        self.current_game_mode = None
        self.init_buttons()

        self.game_modes = {
            'classic': ClassicGameMode(),
        }

    def init_buttons(self):
        self.buttons.append(Button('Level1', 50, 190, 200, 40, 'blue', partial(self.change_game_mode, 'classic')))
        self.buttons.append(Button('Level2', 50, 240, 200, 40, 'blue', None))
        self.buttons.append(Button('Level3', 50, 290, 200, 40, 'blue', None))
        self.buttons.append(Button('Level4', 50, 340, 200, 40, 'blue', None))
        self.buttons.append(Button('Level5', 50, 390, 200, 40, 'blue', None))
        self.buttons.append(Button('Level6', 50, 440, 200, 40, 'blue', None))
        self.buttons.append(Button('Level7', 50, 490, 200, 40, 'blue', None))
        self.buttons.append(Button('Level8', 50, 540, 200, 40, 'blue', None))
        self.buttons.append(Button('Level9', 50, 590, 200, 40, 'blue', None))
        self.buttons.append(Button('Quit', 50, 640, 200, 40, 'red', self.quit))

    def change_game_mode(self, game_mode):
        if self.current_game_mode == game_mode:
            return
        if game_mode not in self.game_modes.keys():
            return
        if self.current_game_mode is not None:
            self.game_modes[self.current_game_mode].exit()
        if game_mode is not None:
            self.game_modes[game_mode].switch_to()
        self.current_game_mode = game_mode

    def classic(self):
        pass

    def run(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons:
                        if button.collides(mouse_pos):
                            button.action()

            # draw buttons
            for button in self.buttons:
                button.hover(button.collides(mouse_pos))
                self.screen.blit(*button.objects())

            # run game mode
            if self.current_game_mode is not None:
                self.game_modes[self.current_game_mode].run()

            self.clock.tick(30)  # 30 FPS
            pygame.display.update()

    def quit(self):
        pygame.quit()
        sys.exit()
