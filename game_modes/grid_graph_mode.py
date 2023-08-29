import os

import pygame

import constants
from button import Switch
from definitions import ROOT_DIR
from graph import GraphFactory
from .walkthrough_game_mode import WalkthroughGameMode, GameStep


class GridGraphMode(WalkthroughGameMode):
    def __init__(self, size_factor=1):
        super().__init__(size_factor)

        seed = 3057040375451409601543510203563232304367163140911798783
        self.graphs.update({0: GraphFactory.generate_grid(0.7, (10, 10), seed), })

        # init buttons
        margin_top = constants.GAME_MODE_MARGIN
        margin_right = constants.GAME_MODE_MARGIN
        size = (200, 40)
        pos_x = constants.GAME_MODE_SCREEN_SIZE[0] - margin_right - size[0]
        self.buttons.update({'switch': Switch(pygame.image.load(os.path.join(ROOT_DIR, "assets", "imageOff.png")).convert_alpha(),
                                              (pos_x - 40 - 10, margin_top + 50), (40, 40), 'blue',
                                              constants.GAME_MODE_HEAD_OFFSET,
                                              second_label=pygame.image.load(os.path.join(ROOT_DIR, "assets", "imageOn.png")).convert_alpha())})

        # init steps
        self.init_game_steps([GridStep1(self, (5, 5), 0),
                              GridStep1(self, (6, 6), 1),
                              GridStep1(self, (7, 7), 2),
                              GridStep1(self, (8, 8), 3)])

        # start with first step
        self.next_step()


class GridStep1(GameStep):
    def __init__(self, game_mode, graph_size, step):
        super().__init__(game_mode)
        self.step = step
        self.has_finished = False
        self.size_factor = 1
        self.graph_size = graph_size
        if graph_size[1] > 5:
            self.size_factor = 0.7
        self.graph = GraphFactory.generate_grid(self.size_factor, self.graph_size)

    def enter(self):
        self.game_mode.standard_headline = "Headline1"
        self.game_mode.headline = self.game_mode.standard_headline
        self.game_mode.active_graph = self.graph
        self.game_mode.active_graph.reset_to_one_group()
        self.game_mode.change_all_buttons('show')
        self.game_mode.change_all_buttons('activate')
        if self.step == 0:
            self.game_mode.buttons['previous'].deactivate()
        self.game_mode.buttons['next'].deactivate()
        self.game_mode.show_points = True

        if self.has_finished and self.step < 3:
            self.game_mode.buttons['next'].activate()

    def is_finished(self):
        is_finished = self.game_mode.active_graph.is_solved()
        if self.has_finished:
            return False
        if is_finished:
            self.has_finished = True
        return is_finished

    def finish(self):
        self.game_mode.headline = "Success1"
        if self.step < 3:
            self.game_mode.buttons['next'].activate()
        self.game_mode.active_graph.deactivated = True
        self.game_mode.draw_necessary = True