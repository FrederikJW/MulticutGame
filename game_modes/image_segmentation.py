import gettext
import os

import colors
import constants

import pygame

import utils
from button import Button
from graph import GraphFactory
from .walkthrough_game_mode import WalkthroughGameMode, GameStep

localedir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'locale')
de = gettext.translation('base', localedir, languages=['de'])
de.install()

_ = de.gettext


class ImageSegmentation(WalkthroughGameMode):
    def __init__(self, size_factor=1):
        super().__init__(size_factor)

        self.show_image = True

        seed = 3057040375451409601543510203563232304367163140911798783
        self.graphs.update({
            0: GraphFactory.generate_grid(0.7, (10, 10), seed),
        })

        # init buttons
        margin_top = constants.MARGIN
        margin_right = constants.MARGIN
        size = (200, 40)
        pos_x = constants.GAME_MODE_SCREEN_SIZE[0] - margin_right - size[0]
        self.buttons.update({
            'switch': Button(_('switch'), (pos_x - 40 - 10, margin_top + 50), (40, 40), 'blue', self.switch_show_image,
                             constants.GAME_MODE_HEAD_OFFSET)
        })

        # init steps
        self.init_game_steps([
            SegmentationStep1(self),
        ])

        # start with first step
        self.next_step()

        self.buttons['reset'].hide()

    def switch_show_image(self):
        self.show_image = not self.show_image


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
        self.game_mode.buttons['next'].deactivate()
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
