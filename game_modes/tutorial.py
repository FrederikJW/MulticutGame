from graph import GraphFactory
from .walkthrough_game_mode import WalkthroughGameMode, GameStep


class Tutorial(WalkthroughGameMode):
    def __init__(self, size_factor=1):
        super().__init__(size_factor)

        self.graphs.update({
            0: GraphFactory.generate_grid(self.size_factor, (2, 2), "0110"),
            1: GraphFactory.generate_grid(self.size_factor, (3, 3), "010110101100"),
        })

        # init steps
        self.init_game_steps([
            TutorialStep1(self),
            TutorialStep2(self),
        ])

        # start with first step
        self.next_step()

        self.buttons['reset'].hide()


class TutorialStep1(GameStep):
    def __init__(self, game_mode):
        super().__init__(game_mode)

        self.has_finished = False

    def enter(self):
        self.game_mode.headline = "entered first step; only show headline; 2x2 Grid"
        self.game_mode.set_active_graph(0)
        self.game_mode.active_graph.reset()
        self.game_mode.buttons['previous'].deactivate()
        self.game_mode.buttons['next'].deactivate()
        self.game_mode.show_points = False

        if self.has_finished:
            self.game_mode.buttons['next'].activate()

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


class TutorialStep2(GameStep):
    def __init__(self, game_mode):
        super().__init__(game_mode)

        self.has_finished = False

    def enter(self):
        self.game_mode.headline = "entered second step; show points; 3x3 Grid"
        self.game_mode.set_active_graph(1)
        self.game_mode.active_graph.reset()
        self.game_mode.buttons['previous'].activate()
        self.game_mode.buttons['next'].deactivate()
        self.game_mode.buttons['reset'].show()
        self.game_mode.show_points = True

    def run(self):
        pass

    def is_finished(self):
        is_finished = self.game_mode.active_graph.is_solved()
        if is_finished:
            self.has_finished = True
        return is_finished

    def finish(self):
        self.game_mode.headline = "great, you solved it! That is the end"

    def exit(self):
        self.game_mode.buttons['reset'].hide()
