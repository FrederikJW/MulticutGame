import gettext
import os
import pickle
import time

import numpy
import pygame

import colors
import constants
import utils
from button import Switch
from graph import GraphFactory
from .walkthrough_game_mode import WalkthroughGameMode, GameStep

localedir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'locale')
de = gettext.translation('base', localedir, languages=['de'])
de.install()

_ = de.gettext


class ImageSegmentation(WalkthroughGameMode):
    def __init__(self, size_factor=1):
        super().__init__(size_factor)

        seed = 3057040375451409601543510203563232304367163140911798783
        self.graphs.update({0: GraphFactory.generate_grid(0.7, (10, 10), seed), })

        # init buttons
        margin_top = constants.GAME_MODE_MARGIN
        margin_right = constants.GAME_MODE_MARGIN
        size = (200, 40)
        pos_x = constants.GAME_MODE_SCREEN_SIZE[0] - margin_right - size[0]
        self.buttons.update({'switch': Switch(pygame.image.load("assets/imageOff.png").convert_alpha(),
                                              (pos_x - 40 - 10, margin_top + 50), (40, 40), 'blue',
                                              constants.GAME_MODE_HEAD_OFFSET,
                                              second_label=pygame.image.load("assets/imageOn.png").convert_alpha())})

        # init steps
        self.init_game_steps([SegmentationStep1(self), SegmentationStep2(self), ])

        # start with first step
        self.next_step()

        # self.buttons['reset'].hide()

    @property
    def show_image(self):
        return self.buttons['switch'].get_mode()


class SegmentationStep1(GameStep):
    def __init__(self, game_mode):
        super().__init__(game_mode)

        self.has_finished = False
        self.image_offset = (200, 20)
        image_size = (500, 500)
        self.image_overlay_surface = pygame.Surface(image_size)
        # self.image_overlay_surface.set_alpha(200)
        self.image_overlay_surface.set_colorkey(colors.COLOR_KEY)
        self.image = pygame.transform.scale(pygame.image.load("assets/PixelArtTree.png").convert_alpha(), image_size)
        self.image_overlay_rects = []
        rect_size = utils.round_pos(utils.div_pos(image_size, (10, 10)))
        for y in range(0, image_size[1], rect_size[1]):
            for x in range(0, image_size[0], rect_size[0]):
                self.image_overlay_rects.append(pygame.Rect((x, y), rect_size))
        self.image_overlay_colors = {}

        self.edge_line_map = {}
        for i in range(100):
            if i % 10 != 0:
                pos1 = (rect_size[0] * (i % 10), rect_size[1] * (i // 10))
                pos2 = (rect_size[0] * (i % 10), rect_size[1] * ((i // 10) + 1))
                self.edge_line_map[(i - 1, i)] = (pos1, pos2)
                self.edge_line_map[(i, i - 1)] = (pos1, pos2)
            if i // 10 != 0:
                pos1 = (rect_size[0] * (i % 10), rect_size[1] * (i // 10))
                pos2 = (rect_size[0] * ((i % 10) + 1), rect_size[1] * (i // 10))
                self.edge_line_map[(i, i - 10)] = (pos1, pos2)
                self.edge_line_map[(i - 10, i)] = (pos1, pos2)

    def enter(self):
        self.game_mode.headline = "Image Segmentation"
        self.game_mode.set_active_graph(0)
        self.game_mode.active_graph.reset_to_one_group()
        self.game_mode.buttons['previous'].deactivate()
        # TODO: just for testing. change this to deactivate
        self.game_mode.buttons['next'].activate()
        self.game_mode.buttons['reset'].hide()
        self.game_mode.show_points = False

        if self.has_finished:
            self.game_mode.buttons['next'].activate()

    def draw(self):
        if len(self.image_overlay_colors) != len(self.game_mode.active_graph.groups):
            distinct_colors = utils.generate_distinct_colors(len(self.game_mode.active_graph.groups))
            self.image_overlay_colors = dict(zip(self.game_mode.active_graph.groups, distinct_colors))

        if self.game_mode.show_image:
            self.game_mode.body_surface.blit(self.image, self.image_offset)
            # for i, rect in enumerate(self.image_overlay_rects):
            #     color = self.image_overlay_colors[self.game_mode.active_graph.vertices[i].group]
            #     pygame.draw.rect(self.image_overlay_surface, color, rect)
            self.image_overlay_surface.fill(colors.COLOR_KEY)
            for edge in self.game_mode.active_graph.edges:
                if edge.is_cut():
                    utils.draw_thick_aaline(self.image_overlay_surface, *self.edge_line_map[edge.tuple], colors.RED, 2)

            self.game_mode.body_surface.blit(self.image_overlay_surface, self.image_offset)

    def run(self):
        pass

    def is_finished(self):
        is_finished = self.game_mode.active_graph.is_solved()
        if is_finished:
            self.has_finished = True
        return is_finished

    def finish(self):
        self.game_mode.headline = "great, you solved it! click on next"
        self.game_mode.buttons['next'].activate()

    def exit(self):
        self.game_mode.buttons['previous'].activate()


class SegmentationStep2(GameStep):
    def __init__(self, game_mode):
        super().__init__(game_mode)

        self.has_finished = False
        self.image_offset = (200, 20)
        with open('assets/cosmo_instances/frauenkirche_instance.pickle', 'rb') as file:
            file_content = pickle.load(file)
        image_array = file_content['img']
        height, width, _ = image_array.shape
        self.image_size = utils.round_pos(utils.mult_pos((width, height), (0.2, 0.2)))
        self.image = pygame.transform.scale(utils.ndarray_to_surface(image_array), self.image_size)

        self.segmentation_array = file_content['segmentation']
        self.segmentation_array_scaled = numpy.zeros((self.image_size[1], self.image_size[0]))
        for y, row in enumerate(self.segmentation_array):
            for x, vertex_id in enumerate(row):
                scaled_y = round(y * 0.2)
                scaled_x = round(x * 0.2)
                if scaled_y < self.image_size[1] and scaled_x < self.image_size[0]:
                    self.segmentation_array_scaled[scaled_y][scaled_x] = vertex_id

        vertex_positions = file_content['nodes']
        scaled_vertex_positions = {}
        for vertex_id, pos in vertex_positions.items():
            scaled_vertex_positions[vertex_id] = utils.add_pos(utils.round_pos(utils.mult_pos(pos, (0.2, 0.2))),
                                                               self.image_offset)
        edges = file_content['edges']
        self.graph = GraphFactory.generate_graph_from(0.5, scaled_vertex_positions, edges)

        self.image_overlay_colors = {}
        self.node_colors = {}
        self.overlay_image = numpy.zeros((self.image_size[1], self.image_size[0], 3))
        self.overlay_surface = None

        self.edge_line_map = {}

        self.enter_timestamp = None
        self.animation_finished = False
        self.show_image = True
        self.show_overlay = True

    def enter(self):
        self.game_mode.buttons['switch'].switch_mode = False
        self.enter_timestamp = time.time()
        self.animation_finished = False
        self.show_image = True
        self.show_overlay = False

        self.game_mode.headline = "Image Segmentation"
        self.game_mode.active_graph = self.graph
        self.game_mode.active_graph.reset()
        self.game_mode.buttons['previous'].activate()
        self.game_mode.buttons['next'].deactivate()
        self.game_mode.show_points = True

        if self.has_finished:
            self.game_mode.buttons['next'].activate()

    def draw(self):
        if not self.game_mode.show_image and self.animation_finished:
            return

        if len(self.image_overlay_colors) != len(self.game_mode.active_graph.groups):
            distinct_colors = utils.generate_distinct_colors(len(self.game_mode.active_graph.groups))
            self.image_overlay_colors = dict(zip(self.game_mode.active_graph.groups, distinct_colors))
            self.node_colors = {}
            for y, row in enumerate(self.segmentation_array_scaled):
                for x, vertex_id in enumerate(row):
                    color = self.node_colors.get(vertex_id)
                    if color is None:
                        vertex = self.game_mode.active_graph.get_vertex(vertex_id)
                        color = self.image_overlay_colors.get(vertex.group)
                        self.node_colors[vertex_id] = color

                    self.overlay_image[y][x] = color

            self.overlay_surface = pygame.transform.scale(utils.ndarray_to_surface(self.overlay_image), self.image_size)
            self.overlay_surface.set_alpha(200)

        if self.animation_finished or self.show_image:
            self.game_mode.body_surface.blit(self.image, self.image_offset)

        if self.animation_finished or self.show_overlay:
            self.game_mode.body_surface.blit(self.overlay_surface, self.image_offset)

    def run(self):
        if not self.animation_finished:
            time_passed = time.time() - self.enter_timestamp
            if time_passed > 9:
                self.show_image = False
                self.show_overlay = False
                self.animation_finished = True
                self.game_mode.draw_necessary = True
            elif time_passed > 6:
                self.show_image = False
                self.show_overlay = True
                self.game_mode.draw_necessary = True
            elif time.time() - self.enter_timestamp > 3:
                self.show_image = True
                self.show_overlay = True
                self.game_mode.draw_necessary = True

    def is_finished(self):
        is_finished = self.game_mode.active_graph.is_solved()
        if is_finished:
            self.has_finished = True
        return is_finished

    def finish(self):
        self.game_mode.headline = "great, you solved it! click on next"
        self.game_mode.buttons['next'].activate()

    def exit(self):
        self.game_mode.buttons['previous'].activate()
