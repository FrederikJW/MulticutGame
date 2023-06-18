import gettext
import os
import constants

import pygame

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
            0: GraphFactory.generate_grid(0.5, (10, 10), seed),
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
        self.image = pygame.transform.scale(pygame.image.load("assets/PixelArtTree.png").convert_alpha(), (500, 500))

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
        if self.game_mode.show_image:
            self.game_mode.body_surface.blit(self.image, (10, 10))

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
