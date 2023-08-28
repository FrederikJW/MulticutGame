import abc
import os
from functools import partial

import pygame
from pygame import gfxdraw

import colors
import constants
import utils
from button import ActionButton, Switch
from utils import sub_pos, get_distance
from definitions import ROOT_DIR


# abstract game mode class
class GameMode(metaclass=abc.ABCMeta):

    def __init__(self, size_factor=1):
        self.size_factor = size_factor

        self.head_surface = pygame.Surface(constants.GAME_MODE_HEAD_SIZE)
        self.head_surface.fill(colors.COLOR_KEY)
        self.head_surface.set_colorkey(colors.COLOR_KEY)

        self.text_box_surface = pygame.Surface(constants.GAME_MODE_TEXT_BOX_SIZE)
        self.text_box_surface.fill(colors.COLOR_KEY)
        self.text_box_surface.set_colorkey(colors.COLOR_KEY)

        self.body_surface = pygame.Surface(constants.GAME_MODE_BODY_SIZE)
        self.body_surface.fill(colors.COLOR_KEY)
        self.body_surface.set_colorkey(colors.COLOR_KEY)
        self.grey_overlay = pygame.Surface(constants.GAME_MODE_BODY_SIZE)
        self.grey_overlay.fill(colors.BLACK)
        self.grey_overlay.set_alpha(100)

        self.surface = pygame.Surface(constants.GAME_MODE_SCREEN_SIZE)
        self.surface.fill(colors.COLOR_KEY)
        self.surface.set_colorkey(colors.COLOR_KEY)

        self.mouse_pos = (0, 0)
        self.graph_mouse_pos = (0, 0)
        self.game_mode_mouse_pos = (0, 0)

        self.is_cutting = False
        self.cut_line = []
        self.cut_edge_set = set()

        self.rec = pygame.Rect(*constants.GAME_MODE_SCREEN_OFFSET, *constants.GAME_MODE_SCREEN_SIZE)

        self.active_graph = None
        self.score_drawn = False
        self.move_vertex = None
        self.move_group = None
        self.group_mouse_distance = None
        self.highlight_group = None

        self.font = pygame.font.SysFont('Ariel', 32)
        self.show_headline = True
        self.standard_headline = ''
        self.headline = ''
        self.show_points = True

        self.draw_necessary = True

        self.was_solved = False

        # init buttons
        margin_top = constants.GAME_MODE_MARGIN
        margin_right = constants.GAME_MODE_MARGIN
        size = (200, 40)
        pos_x = constants.GAME_MODE_SCREEN_SIZE[0] - margin_right - size[0]
        self.buttons = {}
        self.buttons.update({
            'reset': ActionButton('Reset Cut', (pos_x, margin_top), (90, 40), 'red', constants.GAME_MODE_HEAD_OFFSET,
                                  self.reset_graph),
            'reset2': ActionButton('Reset Group', (pos_x + 110, margin_top), (90, 40), 'red',
                                   constants.GAME_MODE_HEAD_OFFSET, partial(self.reset_graph, True)),
            'solution': Switch(pygame.image.load(os.path.join(ROOT_DIR, "assets", "idea.png")).convert_alpha(), (pos_x - 40 - 10, margin_top),
                               (40, 40), 'blue', constants.GAME_MODE_HEAD_OFFSET,
                               second_label=pygame.image.load(os.path.join(ROOT_DIR, "assets", "ideaOn.png")).convert_alpha()),
            'movegroup': Switch(pygame.image.load(os.path.join(ROOT_DIR, "assets", "singleNode.png")).convert_alpha(),
                                (pos_x - 80 - 20, margin_top), (40, 40), 'blue',
                                second_label=pygame.image.load(os.path.join(ROOT_DIR, "assets", "group.png")).convert_alpha())})

    def reset_graph(self, one_group=False, reset_game_mode=True):
        if self.active_graph is not None:
            if one_group:
                self.active_graph.reset_to_one_group()
            else:
                self.active_graph.reset()

        if reset_game_mode:
            self.reset_game_mode()

    def reset_game_mode(self):
        self.headline = self.standard_headline
        self.was_solved = False
        self.score_drawn = False

    def change_all_buttons(self, action):
        for button in self.buttons.values():
            if action == 'hide':
                button.hide()
            elif action == 'show':
                button.show()
            elif action == 'activate':
                button.activate()
            elif action == 'deactivate':
                button.deactivate()

    def print_headline(self):
        if self.headline == '':
            self.headline = self.standard_headline

        self.text_box_surface.fill(colors.COLOR_KEY)
        utils.blit_text(self.text_box_surface, self.headline, (0, 0), self.font, colors.BLACK)

        self.head_surface.blit(self.text_box_surface, (constants.GAME_MODE_MARGIN, constants.GAME_MODE_MARGIN,
                                                       *self.text_box_surface.get_size()))

    def print_score(self):
        if self.active_graph is not None:
            score = self.active_graph.get_score()
            optimal_score = self.active_graph.optimal_score
            if optimal_score is None:
                optimal_score = "calculating"
            else:
                optimal_score = str(round(optimal_score))
        else:
            score = ''
            optimal_score = ''

        score_surface = self.font.render('Score' + f" = {score}", True, colors.BLACK)
        score_rec = score_surface.get_rect()
        score_rec = score_surface.get_rect().move(
            (constants.GAME_MODE_MARGIN, constants.GAME_MODE_HEAD_SIZE[1] - constants.GAME_MODE_MARGIN - score_rec.height))

        optimal_score_surface = self.font.render('Optimal Score' + f" = {optimal_score}", True, colors.BLACK)
        optimal_score_rec = optimal_score_surface.get_rect().move(
            (score_rec.x + score_rec.width + constants.GAME_MODE_MARGIN, score_rec.y))

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
            self.active_graph.draw(self.highlight_group, self.buttons['solution'].get_mode())
            self.body_surface.blit(*self.active_graph.objects())
        if self.show_points:
            self.print_score()
        if self.show_headline:
            self.print_headline()

        # draw cut line
        if len(self.cut_line) != 0:
            prev_point = None
            for point in self.cut_line:
                if prev_point is not None:
                    gfxdraw.line(self.body_surface, *point, *prev_point, colors.BLACK)
                prev_point = point
            gfxdraw.line(self.body_surface, *prev_point, *self.graph_mouse_pos, colors.BLACK)

        self.draw()

        if self.active_graph.deactivated:
            self.body_surface.blit(self.grey_overlay, (0, 0))

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

        if self.active_graph is None or self.active_graph.deactivated:
            return

        if self.buttons['movegroup'].get_mode():
            # reversed because groups at the end are drawn on top and groups on top should hit first
            for group in reversed(self.active_graph.groups):
                if group.is_hit(self.graph_mouse_pos):
                    self.move_group = group
                    self.group_mouse_distance = utils.sub_pos(self.move_group.pos, self.graph_mouse_pos)
                    break
        else:
            for vertex in self.active_graph.vertices.values():
                if vertex.is_hit(self.graph_mouse_pos):
                    self.move_vertex = vertex
                    if len(self.move_vertex.group.vertices) > 1:
                        self.active_graph.move_vertex_to_group(self.move_vertex, None)
                    break

        if (self.move_vertex is None and self.move_group is None
                and pygame.Rect(constants.GAME_MODE_BODY_OFFSET,
                                self.body_surface.get_size()).collidepoint(self.mouse_pos)):
            self.is_cutting = True

    def mouse_up_event(self):
        # if moved vertex is dropped on a group, add vertex to group
        if self.move_vertex is not None and self.active_graph is not None:
            group_hit = self.active_graph.get_collided_group(self.graph_mouse_pos, except_group=self.move_vertex.group)
            if group_hit is not None:
                self.active_graph.move_vertex_to_group(self.move_vertex, group_hit)
                self.draw_necessary = True
            else:
                if self.active_graph.state_saving:
                    self.active_graph.save_state()

        # if moved group is dropped on another group, merge groups
        if self.move_group is not None and self.active_graph is not None:
            group_hit = self.active_graph.get_collided_group(self.graph_mouse_pos, except_group=self.move_group)
            if group_hit is not None:
                self.active_graph.merge_groups(self.move_group, group_hit)
                self.draw_necessary = True
            else:
                if self.active_graph.state_saving:
                    self.active_graph.save_state()

        self.move_vertex = None
        self.move_group = None
        self.is_cutting = False

    def main(self, events, mouse_pos):
        self.highlight_group = None

        # calculate relative mouse positions
        self.mouse_pos = mouse_pos
        if not pygame.Rect(constants.GAME_MODE_BODY_OFFSET, self.body_surface.get_size()).collidepoint(self.mouse_pos):
            self.move_vertex = None
            self.is_cutting = False
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
        if self.active_graph is not None and self.active_graph.is_solved() and not self.was_solved:
            self.was_solved = True
            self.graph_solved_event()

        # move vertex
        if self.move_vertex is not None and self.active_graph is not None:
            self.move_vertex.group.move(self.graph_mouse_pos)
            group_hit = self.active_graph.get_collided_group(self.graph_mouse_pos, except_group=self.move_vertex.group)
            if group_hit is not None:
                self.highlight_group = group_hit

            self.draw_necessary = True

        # move group
        if self.move_group is not None and self.active_graph is not None:
            self.move_group.move(utils.add_pos(self.graph_mouse_pos, self.group_mouse_distance))
            group_hit = self.active_graph.get_collided_group(self.graph_mouse_pos, except_group=self.move_group)
            if group_hit is not None:
                self.highlight_group = group_hit
            self.draw_necessary = True

        # mark hover effect
        for button in self.buttons.values():
            if button.hover(button.collides(self.game_mode_mouse_pos)):
                self.draw_necessary = True

        # calculate cut line
        if self.is_cutting:
            if len(self.cut_line) == 0 or get_distance(self.graph_mouse_pos,
                                                       self.cut_line[-1]) > constants.GRAPH_CUT_LINE_POINT_DISTANCE:
                if len(self.cut_line) != 0:
                    self.cut_edge_set = self.cut_edge_set.union(
                        self.active_graph.get_intersected_edges(self.cut_line[-1], self.graph_mouse_pos))
                self.cut_line.append(self.graph_mouse_pos)
            self.draw_necessary = True

        # make the cut
        if not self.is_cutting and len(self.cut_line) != 0:
            self.cut_line = []
            self.active_graph.cut(self.cut_edge_set)
            self.cut_edge_set = set()
            self.draw_necessary = True

        self.run()

        self._draw_wrapper()

    def graph_solved_event(self):
        self.active_graph.deactivated = True
        self.draw_necessary = True

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
