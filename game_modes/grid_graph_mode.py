import constants
from button import ActionButton
from graph import GraphFactory
from .walkthrough_game_mode import WalkthroughGameMode, GameStep


class GridGraphMode(WalkthroughGameMode):
    def __init__(self, size_factor=1):
        super().__init__(size_factor)

        # init buttons
        margin_top = constants.GAME_MODE_MARGIN
        margin_right = constants.GAME_MODE_MARGIN
        size = (200, 40)
        pos_x = constants.GAME_MODE_SCREEN_SIZE[0] - margin_right - size[0]
        self.buttons.update({'regenerate': ActionButton('Regenerate', (pos_x, margin_top + 100), size, 'red',
                                                        constants.GAME_MODE_HEAD_OFFSET, self.regenerate_graph)})

        # init steps
        self.init_game_steps([GridStep1(self, (5, 5), 0), GridStep1(self, (6, 6), 1), GridStep1(self, (7, 7), 2),
                              GridStep1(self, (8, 8), 3)])

        # start with first step
        self.next_step()

    def regenerate_graph(self):
        self.current_step.regenerate_graph()


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

    def regenerate_graph(self):
        self.graph = GraphFactory.generate_grid(self.size_factor, self.graph_size)
        self.game_mode.active_graph = self.graph
        self.game_mode.active_graph.reset_to_one_group()
        self.game_mode.headline = self.game_mode.standard_headline
        self.has_finished = False
        self.game_mode.draw_necessary = True

    def enter(self):
        self.set_headline()

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

    def set_headline(self):
        if self.step == 0:
            self.game_mode.standard_headline = ("This a 5x5 grid graph. It resembles the streets of Manhattan or "
                                                "you can imagine it being pixels connected by edges with their direct "
                                                "neighbors. Try to solve it.")
        elif self.step == 1:
            self.game_mode.standard_headline = ("This a 6x6 grid graph. Grid graphs can have any size. Therefore we are"
                                                " increasing the size to give you a harder task to solve.")
        elif self.step == 2:
            self.game_mode.standard_headline = "This grid graph already has the size 7x7."
        elif self.step == 3:
            self.game_mode.standard_headline = ("This is a 8x8 grid graph and the biggest graph in this game mode. "
                                                "See if you can solve this.")

    def is_finished(self):
        is_finished = self.game_mode.active_graph.is_solved()
        if self.has_finished:
            return False
        if is_finished:
            self.has_finished = True
        return is_finished

    def finish(self):
        if self.step < 3:
            self.game_mode.buttons['next'].activate()
            self.game_mode.headline = "That's it. Good job!"
        else:
            self.game_mode.headline = "You solved them all. Try out another game mode!"
        self.game_mode.active_graph.deactivated = True
        self.game_mode.draw_necessary = True
