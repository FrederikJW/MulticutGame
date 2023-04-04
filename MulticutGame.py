import pygame
import sys

from button import Button


class MulticutGame:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    SCREEN_COLOR = (255, 255, 255)
    GAME_MODES = []

    def __init__(self):
        pygame.init()

        # Set up font
        self.font = pygame.font.SysFont('Ariel', 32)
        self.text = self.font.render("0", True, (0, 0, 0))

        # Set up screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SCALED)
        pygame.display.set_caption("Multicut Game")

        self.screen.fill((255, 255, 255))
        pygame.display.update()

        self.buttons = []
        self.game_mode = None
        self.init_buttons()

    def init_buttons(self):
        self.buttons.append(Button('Quit', 0, 0, 100, 50, (255, 0, 0), (0, 255, 0), self.quit))

    def run(self):
        while True:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for button in self.buttons:
                        if button.collides(mouse_pos):
                            button.action()

            # draw buttons
            for button in self.buttons:
                self.screen.blit(*button.objects())

            pygame.display.update()

    def quit(self):
        pygame.quit()
        sys.exit()
