import gettext
import os

import pygame

import colors
import constants
from button import Button
from graph import GraphFactory
from utils import sub_pos
from .game_mode import GameMode

localedir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'locale')
de = gettext.translation('base', localedir, languages=['de'])
de.install()

_ = de.gettext


class ClassicGameMode(GameMode):
    def __init__(self, x, y, width, height, graph_type, graph_width=4, graph_height=4):
        super().__init__(x, y, width, height)

        self.graph = None
        self.graph_type = graph_type
        self.graph_width = graph_width
        self.graph_height = graph_height
        if graph_type == 'grid':
            self.graph = GraphFactory.generate_grid((self.graph_width, self.graph_height))
        elif graph_type == 'pentagram':
            self.graph = GraphFactory.generate_pentagram()
        self.score_drawn = False

        self.move_vertex = None
        self.gamemode_offset = (self.rec[0], self.rec[1])
        self.graph_offset = (self.graph.rec[0] + self.rec[0], self.graph.rec[1] + self.rec[1])
        self.graph_rel_offset = sub_pos(self.graph_offset, self.gamemode_offset)

        self.font = pygame.font.SysFont('Ariel', 32)
        self.draw_necessary = True

        # init buttons
        self.buttons = []
        margin_top = constants.MARGIN
        margin_right = constants.MARGIN
        size = (200, 40)
        pos_x = constants.GAME_MODE_SCREEN_SIZE[0] - margin_right - size[0]
        self.buttons.extend([
            Button(_('Reset'), (pos_x, margin_top), size, 'red', self.reset_graph, self.gamemode_offset),
            Button(_('Regenerate'), (pos_x, margin_top + 50), size, 'red', self.regenerate_graph, self.gamemode_offset)
        ])

    def regenerate_graph(self):
        if self.graph_type == 'grid':
            self.graph = GraphFactory.generate_grid((self.graph_width, self.graph_height))
        elif self.graph_type == 'pentagram':
            self.graph = GraphFactory.generate_pentagram()
        self.score_drawn = False

    def reset_graph(self):
        self.graph.reset()

    def switch_to(self):
        pass

    def print_score(self):
        score_surface = self.font.render(_('Score') + f" = {self.graph.get_score()}", True, colors.BLACK)
        score_rec = score_surface.get_rect().move((constants.MARGIN, constants.MARGIN))
        optimal_score = self.graph.optimal_score
        if optimal_score is None:
            optimal_score = _("calculating")
        else:
            optimal_score = str(int(optimal_score))
        optimal_score_surface = self.font.render(_('Optimal Score') + f" = {optimal_score}", True, colors.BLACK)
        optimal_score_rec = optimal_score_surface.get_rect().move((constants.MARGIN, constants.MARGIN + 50))

        self.surface.blit(score_surface, score_rec)
        self.surface.blit(optimal_score_surface, optimal_score_rec)

    def draw(self, highlight_group):
        if not self.draw_necessary:
            return
        self.draw_necessary = False
        self.surface.fill(colors.WHITE)
        self.graph.draw(highlight_group)
        self.print_score()
        for button in self.buttons:
            self.surface.blit(*button.objects())

        # draw border
        rec = pygame.Rect(sub_pos(self.graph_rel_offset, (0, 2)), (constants.GAME_MODE_SCREEN_SIZE[0], 2))
        pygame.draw.rect(self.surface, colors.GREY, rec)
        self.surface.blit(*self.graph.objects())

    def run(self, events):
        highlight_group = None

        mouse_pos = pygame.mouse.get_pos()
        if not pygame.Rect(self.graph_offset, self.graph.rec.size).collidepoint(mouse_pos):
            self.move_vertex = None
        graph_mouse_pos = sub_pos(mouse_pos, self.graph_offset)
        gamemode_mouse_pos = sub_pos(mouse_pos, self.gamemode_offset)

        if not self.score_drawn and self.graph.optimal_score is not None:
            self.draw_necessary = True

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
