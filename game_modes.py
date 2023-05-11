import abc

import pygame

import colors
from button import Button
from colors import *
from graph import GraphFactory
from utils import sub_pos


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
    def __init__(self, x, y, width, height, graph_type, graph_width=4, graph_height=4):
        super().__init__(x, y, width, height)

        self.graph = None
        if graph_type == 'grid':
            self.graph = GraphFactory.generate_grid((graph_width, graph_height))
        elif graph_type == 'pentagram':
            self.graph = GraphFactory.generate_pentagram()

        self.move_vertex = None
        self.gamemode_offset = (self.rec[0], self.rec[1])
        self.graph_offset = (self.graph.rec[0] + self.rec[0], self.graph.rec[1] + self.rec[1])

        self.font = pygame.font.SysFont('Ariel', 32)
        self.print_score()
        self.draw_necessary = True
        self.buttons = []
        self.buttons.append(Button('Reset', (100, 100), (200, 40), 'red', self.graph.reset, self.gamemode_offset))

    def switch_to(self):
        pass

    def print_score(self):
        score_surface = self.font.render(f"score={self.graph.get_score()}", True, colors.BLACK)
        score_rec = score_surface.get_rect()
        optimal_score = self.graph.optimal_score
        if optimal_score is None:
            optimal_score = "calculating"
        else:
            optimal_score = str(int(optimal_score))
        optimal_score_surface = self.font.render(f"optimal score={optimal_score}", True, colors.BLACK)
        optimal_score_rec = optimal_score_surface.get_rect()
        optimal_score_rec = optimal_score_rec.move(0, 20)

        self.surface.blit(score_surface, score_rec)
        self.surface.blit(optimal_score_surface, optimal_score_rec)

    def draw(self, highlight_group):
        if not self.draw_necessary:
            return
        self.draw_necessary = False
        self.surface.fill(WHITE)
        self.graph.draw(highlight_group)
        self.print_score()
        for button in self.buttons:
            self.surface.blit(*button.objects())
        self.surface.blit(*self.graph.objects())

    def run(self, events):
        highlight_group = None

        mouse_pos = pygame.mouse.get_pos()
        if not pygame.Rect(self.graph_offset, self.graph.rec.size).collidepoint(mouse_pos):
            self.move_vertex = None
        graph_mouse_pos = sub_pos(mouse_pos, self.graph_offset)
        gamemode_mouse_pos = sub_pos(mouse_pos, self.gamemode_offset)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for vertex in self.graph.vertices.values():
                    if vertex.rec.collidepoint(graph_mouse_pos):
                        self.move_vertex = vertex
                        if len(self.move_vertex.group.vertices) > 1:
                            self.graph.move_vertex_to_group(self.move_vertex, None)
                        break
                for button in self.buttons:
                    if button.collides(gamemode_mouse_pos):
                        button.action()
                        self.draw_necessary = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.move_vertex is not None:
                    for group in self.graph.groups:
                        if group != self.move_vertex.group and group.rec.colliderect(self.move_vertex.group.rec):
                            self.graph.move_vertex_to_group(self.move_vertex, group)
                            self.draw_necessary = True
                            break
                self.move_vertex = None

        if self.move_vertex is not None:
            self.move_vertex.move(graph_mouse_pos)
            for group in self.graph.groups:
                if group != self.move_vertex.group and group.rec.colliderect(self.move_vertex.group.rec):
                    highlight_group = group
                    break

            self.draw_necessary = True

        for button in self.buttons:
            if button.hover(button.collides(gamemode_mouse_pos)):
                self.draw_necessary = True

        self.draw(highlight_group)

    def exit(self):
        pass
