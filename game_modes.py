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
    def run(self, events):
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
        self.graph.add_edge(0, 1, -1)
        self.graph.add_edge(0, 2, 1)
        self.graph.add_edge(2, 3, -1)
        self.graph.add_edge(1, 3, 1)
        self.move_vertex = None

    def switch_to(self):
        pass

    def run(self, events):
        offset = (self.graph.rec[0] + self.rec[0], self.graph.rec[1] + self.rec[1])
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = (mouse_pos[0] - offset[0], mouse_pos[1] - offset[1])
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for vertex in self.graph.vertices.values():
                    if vertex.rec.collidepoint(mouse_pos):
                        self.move_vertex = vertex
                        break
            elif event.type == pygame.MOUSEBUTTONUP:
                self.move_vertex = None

        if self.move_vertex is not None:
            self.move_vertex.move(mouse_pos)
            self.surface.fill(WHITE)
            self.graph.draw()
        self.surface.blit(*self.graph.objects())

    def exit(self):
        pass
