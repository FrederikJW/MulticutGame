import abc

import pygame

from colors import *
from graph import GraphFactory


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
        self.graph = GraphFactory.generate_grid((4, 4))

        self.move_vertex = None
        self.offset = (self.graph.rec[0] + self.rec[0], self.graph.rec[1] + self.rec[1])

    def switch_to(self):
        pass

    def run(self, events):
        highlight_group = None

        mouse_pos = pygame.mouse.get_pos()
        if not pygame.Rect(self.offset, self.graph.rec.size).collidepoint(mouse_pos):
            self.move_vertex = None
        mouse_pos = (mouse_pos[0] - self.offset[0], mouse_pos[1] - self.offset[1])

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for vertex in self.graph.vertices.values():
                    if vertex.rec.collidepoint(mouse_pos):
                        self.move_vertex = vertex
                        if len(self.move_vertex.group.vertices) > 1:
                            self.graph.move_vertex_to_group(self.move_vertex, None)
                        break
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.move_vertex is not None:
                    for group in self.graph.groups:
                        if group != self.move_vertex.group and group.rec.colliderect(self.move_vertex.group.rec):
                            self.graph.move_vertex_to_group(self.move_vertex, group)
                            self.surface.fill(WHITE)
                            self.graph.draw(highlight_group)
                            break
                self.move_vertex = None

        if self.move_vertex is not None:
            self.move_vertex.move(mouse_pos)
            for group in self.graph.groups:
                if group != self.move_vertex.group and group.rec.colliderect(self.move_vertex.group.rec):
                    highlight_group = group
                    break

            self.surface.fill(WHITE)
            self.graph.draw(highlight_group)
        self.surface.blit(*self.graph.objects())

    def exit(self):
        pass
