import os
import pickle
import time

import numpy
import pygame

import colors
import constants
import utils
from button import Switch
from definitions import ROOT_DIR
from graph import GraphFactory
from .walkthrough_game_mode import WalkthroughGameMode, GameStep


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
        self.buttons.update({'switch': Switch(
            pygame.image.load(os.path.join(ROOT_DIR, "assets", "imageOff.png")).convert_alpha(),
            (pos_x - 40 - 10, margin_top + 50), (40, 40), 'blue', constants.GAME_MODE_HEAD_OFFSET,
            second_label=pygame.image.load(os.path.join(ROOT_DIR, "assets", "imageOn.png")).convert_alpha())})

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
        self.image_offset = (245, 20)
        image_size = (490, 490)
        self.image_overlay_surface = pygame.Surface(image_size)
        # self.image_overlay_surface.set_alpha(200)
        self.image_overlay_surface.set_colorkey(colors.COLOR_KEY)
        self.image = pygame.transform.scale(
            pygame.image.load(os.path.join(ROOT_DIR, "assets", "PixelArtTree.png")).convert_alpha(), image_size)
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
        self.game_mode.standard_headline = ("One possible use case for the multicut minimization problem is image "
                                            "segmentation where an image is split into related parts. In the first "
                                            "example we want to split the tree from the sky and the ground. You can see "
                                            "the image and your current progress if you click on the button with the "
                                            "image icon on the right. Try to solve it.")
        self.game_mode.headline = self.game_mode.standard_headline
        self.game_mode.set_active_graph(0)
        self.game_mode.active_graph.reset_to_one_group()
        self.game_mode.change_all_buttons('show')
        self.game_mode.change_all_buttons('activate')
        self.game_mode.buttons['switch'].switch_mode = False
        self.game_mode.buttons['previous'].deactivate()
        self.game_mode.buttons['next'].deactivate()
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
            self.image_overlay_surface.fill(colors.COLOR_KEY)
            for edge in self.game_mode.active_graph.edges:
                if edge.is_cut():
                    utils.draw_thick_aaline(self.image_overlay_surface, *self.edge_line_map[edge.tuple], colors.RED, 2)

            self.game_mode.body_surface.blit(self.image_overlay_surface, self.image_offset)

    def run(self):
        pass

    def is_finished(self):
        is_finished = self.game_mode.active_graph.is_solved()
        if self.has_finished:
            return False
        if is_finished:
            self.has_finished = True
        return is_finished

    def finish(self):
        self.game_mode.headline = ("Great you solved it. You can see below how solving the graph split the image into "
                                   "parts seperated by red lines. Click on next to do the next image.")
        self.game_mode.buttons['switch'].set_mode(True)
        self.game_mode.buttons['next'].activate()
        self.game_mode.active_graph.deactivated = True
        self.game_mode.draw_necessary = True

    def exit(self):
        self.game_mode.buttons['previous'].activate()


class SegmentationStep2(GameStep):
    def __init__(self, game_mode):
        super().__init__(game_mode)

        self.has_finished = False
        self.image_offset = (200, 20)

        # get image and overlay data from file
        with open(os.path.join(ROOT_DIR, "assets", "cosmo_instances", "frauenkirche_instance.pickle"), 'rb') as file:
            file_content = pickle.load(file)

        # construct image
        image_array = file_content['img']
        height, width, _ = image_array.shape
        self.image_size = utils.round_pos(utils.mult_pos((width, height), (0.2, 0.2)))
        self.image = pygame.transform.scale(utils.ndarray_to_surface(image_array), self.image_size)

        # construct overlay
        self.segmentation_array = file_content['segmentation']
        self.segmentation_array_scaled = numpy.zeros((self.image_size[1], self.image_size[0]))
        for y, row in enumerate(self.segmentation_array):
            for x, vertex_id in enumerate(row):
                scaled_y = round(y * 0.2)
                scaled_x = round(x * 0.2)
                if scaled_y < self.image_size[1] and scaled_x < self.image_size[0]:
                    self.segmentation_array_scaled[scaled_y][scaled_x] = vertex_id

        # construct graph
        vertex_positions = file_content['nodes']
        scaled_vertex_positions = {}
        for vertex_id, pos in vertex_positions.items():
            scaled_vertex_positions[vertex_id] = utils.add_pos(utils.round_pos(utils.mult_pos(pos, (0.2, 0.2))),
                                                               self.image_offset)
        edges = file_content['edges']
        self.graph = GraphFactory.generate_graph_from(0.5, scaled_vertex_positions, edges, centralize=False)

        self.image_overlay_colors = {}
        self.node_colors = {}
        self.overlay_image = numpy.zeros((self.image_size[1], self.image_size[0], 3))
        self.overlay_surface = None

        self.edge_line_map = {}

        self.enter_timestamp = None
        self.prev_timestamp = None
        self.animation_finished = False
        self.animation_stage = None
        self.animation_num_of_vertices = 0
        self.animation_redraw_overlay = True
        self.show_image = True
        self.show_overlay = True

    def enter(self):
        self.game_mode.standard_headline = ("This image is a bit more complicated. The image has already been split "
                                            "into parts, but we seek to group related parts to understand the image "
                                            "better. Try to solve it and don't forget to check your progress with the "
                                            "image button one the right.")
        self.game_mode.headline = self.game_mode.standard_headline

        self.enter_timestamp = time.time()
        self.prev_timestamp = time.time()
        self.animation_finished = False
        self.animation_stage = 1
        self.animation_num_of_vertices = 0
        self.animation_redraw_overlay = True
        self.show_image = True
        self.show_overlay = False

        self.game_mode.active_graph = self.graph
        self.game_mode.active_graph.reset()

        self.game_mode.change_all_buttons('show')
        self.game_mode.change_all_buttons('deactivate')
        self.game_mode.buttons['switch'].switch_mode = False
        self.game_mode.show_points = True

        if self.has_finished:
            self.game_mode.buttons['next'].activate()

    def draw(self):
        if len(self.image_overlay_colors) != len(self.game_mode.active_graph.groups) or self.animation_redraw_overlay:
            self.animation_redraw_overlay = False
            distinct_colors = list(set(utils.generate_distinct_colors(len(self.game_mode.active_graph.groups))))
            self.image_overlay_colors = dict(zip(self.game_mode.active_graph.groups, distinct_colors))
            self.node_colors = {}
            for y, row in enumerate(self.segmentation_array_scaled):
                for x, vertex_id in enumerate(row):
                    if vertex_id > self.animation_num_of_vertices:
                        self.overlay_image[y][x] = colors.COLOR_KEY
                        continue
                    color = self.node_colors.get(vertex_id)
                    if color is None:
                        vertex = self.game_mode.active_graph.get_vertex(vertex_id)
                        color = self.image_overlay_colors.get(vertex.group)
                        self.node_colors[vertex_id] = color

                    self.overlay_image[y][x] = color

            self.overlay_surface = pygame.transform.scale(utils.ndarray_to_surface(self.overlay_image), self.image_size)
            self.overlay_surface.set_colorkey(colors.COLOR_KEY)
            self.overlay_surface.set_alpha(200)

        if not self.game_mode.show_image and self.animation_finished:
            return

        if self.animation_finished or self.show_image:
            self.game_mode.body_surface.blit(self.image, self.image_offset)

        if self.animation_finished or self.show_overlay:
            self.game_mode.body_surface.blit(self.overlay_surface, self.image_offset)

    def run(self):
        if not self.animation_finished:
            time_passed = time.time() - self.prev_timestamp
            if self.animation_stage == 1 and time_passed > 3:
                self.animation_stage = 2
                self.prev_timestamp = time.time()
                self.show_image = True
                self.show_overlay = True
                self.game_mode.draw_necessary = True
            elif self.animation_stage == 2 and time_passed > 0.2:
                self.prev_timestamp = time.time()
                self.animation_num_of_vertices += 1
                if self.animation_num_of_vertices > len(self.game_mode.active_graph.vertices):
                    self.animation_stage = 3
                self.game_mode.draw_necessary = True
                self.animation_redraw_overlay = True
            elif self.animation_stage == 3 and time_passed > 3:
                self.prev_timestamp = time.time()
                self.show_image = False
                self.show_overlay = True
                self.game_mode.draw_necessary = True
                self.animation_stage = 4
            elif self.animation_stage == 4 and time_passed > 3:
                self.prev_timestamp = time.time()
                self.show_image = False
                self.show_overlay = False
                self.animation_finished = True
                self.game_mode.draw_necessary = True
                self.game_mode.change_all_buttons('activate')
                self.game_mode.buttons['next'].deactivate()

    def is_finished(self):
        is_finished = self.game_mode.active_graph.is_solved()
        if self.has_finished:
            return False
        if is_finished:
            self.has_finished = True
        return is_finished

    def finish(self):
        self.game_mode.headline = "Great! That's it with the image segmentation gamemode."
        self.game_mode.buttons['switch'].set_mode(True)
        self.game_mode.active_graph.deactivated = True
        self.game_mode.draw_necessary = True
