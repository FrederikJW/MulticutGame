import abc
import pygame

from graph import Graph, Vertex

from colors import *


# abstract game mode class
class GameMode(metaclass=abc.ABCMeta):

    def __init__(self, x, y, width, height):
        self.surface = pygame.Surface((width, height))
        self.surface.fill(COLOR_KEY)
        self.surface.set_colorkey(COLOR_KEY)
        self.rec = pygame.Rect(x, y, width, height)

    def objects(self):
        return self.surface, self.rec

    @abc.abstractmethod
    def switch_to(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass

    @abc.abstractmethod
    def exit(self):
        pass


class ClassicGameMode(GameMode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.graph = Graph(0, 185, self.rec.width, self.rec.height - 185)
        for i in range(4):
            self.graph.add_vertex(Vertex(i, ((i % 2) * 80 + 40, ((i // 2) * 80 + 40))))
        for i in range(4):
            self.graph.add_edge(i, (i+1) % 4)

    def switch_to(self):
        pass

    def run(self):
        self.surface.blit(*self.graph.objects())

    def exit(self):
        pass
