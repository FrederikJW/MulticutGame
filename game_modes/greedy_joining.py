import gettext
import os

from graph import GraphFactory
from .game_mode import GameMode

localedir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'locale')
de = gettext.translation('base', localedir, languages=['de'])
de.install()

_ = de.gettext


class GreedyJoining(GameMode):
    def __init__(self, size_factor=1):
        super().__init__(size_factor)

        self.active_graph = GraphFactory.generate_grid(self.size_factor, (5, 5), state_saving=True)

    def graph_solved_event(self):
        pass

    def switch_to(self):
        pass

    def draw(self):
        pass

    def run(self):
        if self.active_graph.has_changed:
            if self.active_graph.get_score() >= self.active_graph.prev_state.get_score():
                self.active_graph = self.active_graph.prev_state
                self.move_vertex = None
                self.move_group = None
            self.active_graph.save_state()

    def exit(self):
        pass
