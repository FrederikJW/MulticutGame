import abc

import pygame

import colors


# abstract game mode class
class GameMode(metaclass=abc.ABCMeta):

    def __init__(self, x, y, width, height):
        self.surface = pygame.Surface((width, height))
        self.surface.fill(colors.COLOR_KEY)
        self.surface.set_colorkey(colors.COLOR_KEY)
        self.rec = pygame.Rect(x, y, width, height)

    def objects(self):
        return self.surface, self.rec

    @abc.abstractmethod
    def switch_to(self):
        pass

    @abc.abstractmethod
    def run(self, events):
        pass

    @abc.abstractmethod
    def exit(self):
        pass
