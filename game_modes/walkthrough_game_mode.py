import constants
import pygame
import os

from definitions import ROOT_DIR
from button import ActionButton
from .game_mode import GameMode


class WalkthroughGameMode(GameMode):
    def __init__(self, size_factor=1):
        super().__init__(size_factor)

        self.game_mode_offset = (self.rec[0], self.rec[1])

        # init buttons
        margin_top = constants.GAME_MODE_MARGIN
        margin_right = constants.GAME_MODE_MARGIN
        size = (40, 40)
        pos_x = constants.GAME_MODE_SCREEN_SIZE[0] - margin_right - size[0]
        self.buttons.update({'previous': ActionButton('<', (pos_x - size[0] - 120, margin_top + 50), size, 'red',
                                                      self.game_mode_offset, self.previous_step),
                             'reenter': ActionButton(pygame.image.load(os.path.join(ROOT_DIR, "assets", "repeat.png")).convert_alpha(), (pos_x - size[0] - 40, margin_top + 50), size, 'red',
                                                      self.game_mode_offset, self.reenter),
                             'next': ActionButton('>', (pos_x, margin_top + 50), size, 'green',
                                                  self.game_mode_offset, self.next_step), })

        # init graphs
        self.graphs = {}

        # init game steps
        self.game_step_iterator = None
        self.current_step = None

    def set_active_graph(self, graph_id):
        self.active_graph = self.graphs.get(graph_id)

    def init_game_steps(self, game_steps):
        self.game_step_iterator = GameStepIterator(game_steps)

    def next_step(self):
        if self.current_step is not None:
            self.current_step.exit()

        self.current_step = self.game_step_iterator.next()
        self.current_step.enter()

    def previous_step(self):
        if self.current_step is not None:
            self.current_step.exit()

        self.current_step = self.game_step_iterator.previous()
        self.current_step.enter()

    def graph_solved_event(self):
        pass

    def switch_to(self):
        pass

    def draw(self):
        self.current_step.draw()

    def run(self):
        self.current_step.run()

        if self.current_step.is_finished():
            self.current_step.finish()

    def exit(self):
        pass

    def reenter(self):
        if self.current_step is not None:
            self.current_step.enter()


class GameStepIterator:
    def __init__(self, game_steps):
        self.steps = game_steps
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if -1 >= self.index >= len(self.steps):
            raise StopIteration
        step = self.steps[self.index]
        self.index += 1
        return step

    def next(self):
        return next(self)

    def previous(self):
        self.index -= 1
        if 0 >= self.index >= len(self.steps):
            raise StopIteration

        step = self.steps[self.index - 1]
        return step


class GameStep:
    def __init__(self, game_mode):
        self.game_mode = game_mode

    def enter(self):
        pass

    def draw(self):
        pass

    def run(self):
        pass

    def is_finished(self):
        pass

    def finish(self):
        pass

    def exit(self):
        pass
