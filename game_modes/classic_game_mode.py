import constants
from button import ActionButton
from graph import GraphFactory
from .game_mode import GameMode


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
        elif graph_type == 'petersen':
            self.active_graph = GraphFactory.generate_petersen_graph()

        self.active_graph.reset_to_one_group()

        # init buttons
        margin_top = constants.GAME_MODE_MARGIN
        margin_right = constants.GAME_MODE_MARGIN
        size = (200, 40)
        pos_x = constants.GAME_MODE_SCREEN_SIZE[0] - margin_right - size[0]
        self.buttons.update({'regenerate': ActionButton('Regenerate', (pos_x, margin_top + 50), size, 'red',
                                                        constants.GAME_MODE_HEAD_OFFSET, self.regenerate_graph)})
        self.headline = 'Try it!'

    def regenerate_graph(self):
        if self.graph_type == 'grid':
            self.active_graph = GraphFactory.generate_grid(self.size_factor, (self.graph_width, self.graph_height))
        elif self.graph_type == 'pentagram':
            self.active_graph = GraphFactory.generate_complete_graph(self.size_factor, 5)
        elif self.graph_type == 'petersen':
            self.active_graph = GraphFactory.generate_petersen_graph()

        self.reset_graph(True)

    def graph_solved_event(self):
        super().graph_solved_event()
        self.headline = 'Great you solved it!'

    def switch_to(self):
        pass

    def draw(self):
        pass

    def run(self):
        pass

    def exit(self):
        pass
