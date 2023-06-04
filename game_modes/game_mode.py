import abc
import gettext
import os

import pygame

import colors
import constants
from button import Button
from utils import sub_pos

localedir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'locale')
de = gettext.translation('base', localedir, languages=['de'])
de.install()

_ = de.gettext


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

        self.mouse_pos = (0, 0)
        self.graph_mouse_pos = (0, 0)
        self.game_mode_mouse_pos = (0, 0)

        self.rec = pygame.Rect(*constants.GAME_MODE_SCREEN_OFFSET, *constants.GAME_MODE_SCREEN_SIZE)

        self.graphs = {}
        self.active_graph = None
        self.score_drawn = False
        self.move_vertex = None
        self.highlight_group = None

        self.font = pygame.font.SysFont('Ariel', 32)
        self.show_headline = True
        self.headline = ''
        self.show_points = True

        self.draw_necessary = True

        # init buttons
        margin_top = constants.MARGIN
        margin_right = constants.MARGIN
        size = (200, 40)
        pos_x = constants.GAME_MODE_SCREEN_SIZE[0] - margin_right - size[0]
        self.buttons = {}
        self.buttons.update({'reset': Button(_('Reset'), (pos_x, margin_top), size, 'red', self.reset_graph,
                                             constants.GAME_MODE_HEAD_OFFSET)})

    def reset_graph(self):
        if self.active_graph is not None:
            self.active_graph.reset()

    def set_active_graph(self, graph_id):
        if graph_id is None:
            self.buttons['reset'].deactivate()
            self.active_graph = None
        else:
            self.buttons['reset'].activate()
            self.active_graph = self.graphs[graph_id]

    def print_headline(self):
        headline_surface = self.font.render(self.headline, True, colors.BLACK)
        headline_rec = headline_surface.get_rect().move(constants.MARGIN, constants.MARGIN)

        self.head_surface.blit(headline_surface, headline_rec)

    def print_score(self):
        if self.active_graph is not None:
            score = self.active_graph.get_score()
            optimal_score = self.active_graph.optimal_score
            if optimal_score is None:
                optimal_score = _("calculating")
            else:
                optimal_score = str(round(optimal_score))
        else:
            score = ''
            optimal_score = ''

        score_surface = self.font.render(_('Score') + f" = {score}", True, colors.BLACK)
        score_rec = score_surface.get_rect()
        score_rec = score_surface.get_rect().move(
            (constants.MARGIN, constants.GAME_MODE_HEAD_SIZE[1] - constants.MARGIN - score_rec.height))

        optimal_score_surface = self.font.render(_('Optimal Score') + f" = {optimal_score}", True, colors.BLACK)
        optimal_score_rec = optimal_score_surface.get_rect().move(
            (score_rec.x + score_rec.width + constants.MARGIN, score_rec.y))

        self.head_surface.blit(score_surface, score_rec)
        self.head_surface.blit(optimal_score_surface, optimal_score_rec)

    def objects(self):
        return self.surface, self.rec

    def _draw_wrapper(self):
        if not self.draw_necessary:
            return
        self.draw_necessary = False
        self.head_surface.fill(colors.COLOR_KEY)
        self.body_surface.fill(colors.COLOR_KEY)
        self.surface.fill(colors.COLOR_KEY)

        for button in self.buttons.values():
            self.head_surface.blit(*button.objects())

        if self.active_graph is not None:
            self.active_graph.draw(self.highlight_group)
            self.body_surface.blit(*self.active_graph.objects())
        if self.show_points:
            self.print_score()
        if self.show_headline:
            self.print_headline()

        self.draw()

        self.surface.blit(self.head_surface, constants.GAME_MODE_HEAD_RELATIVE_OFFSET)
        self.surface.blit(self.body_surface, constants.GAME_MODE_BODY_RELATIVE_OFFSET)

        # draw border
        rec = pygame.Rect(sub_pos(constants.GAME_MODE_BODY_RELATIVE_OFFSET, (0, 2)),
                          (constants.GAME_MODE_SCREEN_SIZE[0], 2))
        pygame.draw.rect(self.surface, colors.GREY, rec)

    def mouse_down_event(self):
        for button in self.buttons.values():
            if button.collides(self.game_mode_mouse_pos):
                button.action()
                self.draw_necessary = True

        if self.active_graph is None:
            return

        for vertex in self.active_graph.vertices.values():
            if vertex.rec.collidepoint(self.graph_mouse_pos):
                self.move_vertex = vertex
                if len(self.move_vertex.group.vertices) > 1:
                    self.active_graph.move_vertex_to_group(self.move_vertex, None)
                break

    def mouse_up_event(self):
        if self.move_vertex is not None and self.active_graph is not None:
            for group in self.active_graph.groups:
                if group != self.move_vertex.group and group.rec.colliderect(self.move_vertex.group.rec):
                    self.active_graph.move_vertex_to_group(self.move_vertex, group)
                    self.draw_necessary = True
                    break
        self.move_vertex = None

    def main(self, events):
        self.highlight_group = None

        # calculate relative mouse positions
        self.mouse_pos = pygame.mouse.get_pos()
        if not pygame.Rect(constants.GAME_MODE_BODY_OFFSET, self.body_surface.get_size()).collidepoint(self.mouse_pos):
            self.move_vertex = None
        self.graph_mouse_pos = sub_pos(self.mouse_pos, constants.GAME_MODE_BODY_OFFSET)
        self.game_mode_mouse_pos = sub_pos(self.mouse_pos, constants.GAME_MODE_SCREEN_OFFSET)

        # if the score has been calculated, print it
        if self.active_graph is not None and not self.score_drawn and self.active_graph.optimal_score is not None:
            self.score_drawn = True
            self.draw_necessary = True

        # check events
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_down_event()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_up_event()
        if self.active_graph is not None and self.active_graph.is_solved():
            self.graph_solved_event()

        # move vertex
        if self.move_vertex is not None and self.active_graph is not None:
            self.move_vertex.move(self.graph_mouse_pos)
            for group in self.active_graph.groups:
                if group != self.move_vertex.group and group.rec.colliderect(self.move_vertex.group.rec):
                    self.highlight_group = group
                    break

            self.draw_necessary = True

        # mark hover effect
        for button in self.buttons.values():
            if button.hover(button.collides(self.game_mode_mouse_pos)):
                self.draw_necessary = True

        self.run()

        self._draw_wrapper()

    @abc.abstractmethod
    def graph_solved_event(self):
        pass

    @abc.abstractmethod
    def draw(self):
        pass

    @abc.abstractmethod
    def switch_to(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass

    @abc.abstractmethod
    def exit(self):
        pass
