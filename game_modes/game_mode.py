import abc
import constants
from utils import sub_pos

import pygame

import colors


# abstract game mode class
class GameMode(metaclass=abc.ABCMeta):

    def __init__(self):
        self.head_surface = pygame.Surface(constants.GAME_MODE_HEAD_SIZE)
        self.head_surface.fill(colors.COLOR_KEY)
        self.head_surface.set_colorkey(colors.COLOR_KEY)

        self.body_surface = pygame.Surface(constants.GAME_MODE_BODY_SIZE)
        self.body_surface.fill(colors.COLOR_KEY)
        self.body_surface.set_colorkey(colors.COLOR_KEY)

        self.surface = pygame.Surface(constants.GAME_MODE_SCREEN_SIZE)
        self.surface.fill(colors.COLOR_KEY)
        self.surface.set_colorkey(colors.COLOR_KEY)

        self.rec = pygame.Rect(*constants.GAME_MODE_SCREEN_OFFSET, *constants.GAME_MODE_SCREEN_SIZE)

        self.buttons = []

        self.font = pygame.font.SysFont('Ariel', 32)
        self.draw_necessary = False

    def objects(self):
        return self.surface, self.rec

    def _draw_wrapper(self):
        if not self.draw_necessary:
            return
        self.draw_necessary = False
        self.head_surface.fill(colors.COLOR_KEY)
        self.body_surface.fill(colors.COLOR_KEY)
        self.surface.fill(colors.COLOR_KEY)

        for button in self.buttons:
            self.head_surface.blit(*button.objects())

        self.draw()

        self.surface.blit(self.head_surface, constants.GAME_MODE_HEAD_RELATIVE_OFFSET)
        self.surface.blit(self.body_surface, constants.GAME_MODE_BODY_RELATIVE_OFFSET)

        # draw border
        rec = pygame.Rect(sub_pos(constants.GAME_MODE_BODY_RELATIVE_OFFSET, (0, 2)), (constants.GAME_MODE_SCREEN_SIZE[0], 2))
        pygame.draw.rect(self.surface, colors.GREY, rec)

    def main(self, events):
        self.run(events)

        self._draw_wrapper()

    @abc.abstractmethod
    def draw(self):
        pass

    @abc.abstractmethod
    def switch_to(self):
        pass

    @abc.abstractmethod
    def run(self, events):
        pass

    @abc.abstractmethod
    def exit(self):
        pass
