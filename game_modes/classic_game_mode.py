import gettext
import os

import constants
from button import Button
from graph import GraphFactory
from .game_mode import GameMode

localedir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'locale')
de = gettext.translation('base', localedir, languages=['de'])
de.install()

_ = de.gettext


class ClassicGameMode(GameMode):
    def __init__(self, graph_type, graph_width=4, graph_height=4, size_factor=1):
        super().__init__(size_factor)

        self.graph_type = graph_type
        self.graph_width = graph_width
        self.graph_height = graph_height
        if graph_type == 'grid':
            self.active_graph = GraphFactory.generate_grid(self.size_factor, (self.graph_width, self.graph_height))
        elif graph_type == 'pentagram':
            self.active_graph = GraphFactory.generate_complete_graph(self.size_factor, 5)

        # init buttons
        margin_top = constants.MARGIN
        margin_right = constants.MARGIN
        size = (200, 40)
        pos_x = constants.GAME_MODE_SCREEN_SIZE[0] - margin_right - size[0]
        self.buttons.update({'regenerate': Button(_('Regenerate'), (pos_x, margin_top + 50), size, 'red',
                                                  self.regenerate_graph, constants.GAME_MODE_HEAD_OFFSET)})
        self.headline = 'Try it!'

    def regenerate_graph(self):
        if self.graph_type == 'grid':
            self.active_graph = GraphFactory.generate_grid(self.size_factor, (self.graph_width, self.graph_height))
        elif self.graph_type == 'pentagram':
            self.active_graph = GraphFactory.generate_complete_graph(self.size_factor, 5)
        self.score_drawn = False

    def graph_solved_event(self):
        self.headline = 'Great you solved it!'

    def switch_to(self):
        pass

    def draw(self):
        pass

    def run(self):
        pass

    def exit(self):
        pass
