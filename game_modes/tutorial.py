from .walkthrough_game_mode import WalkthroughGameMode, GameStep

from graph import GraphFactory


class Tutorial(WalkthroughGameMode):
    def __init__(self):
        super().__init__()

        # init steps
        self.init_game_steps([
            TutorialStep1(self),
            TutorialStep2(self),
        ])

        # start with first step
        self.next_step()

        self.buttons['reset'].hide()

    # TODO: delete this function and use is_finished from steps only
    def graph_solved_event(self):
        self.current_step.finish()


class TutorialStep1(GameStep):
    def __init__(self, game_mode):
        super().__init__(game_mode)

        self.graph = GraphFactory.generate_grid((2, 2))

    def enter(self):
        self.game_mode.headline = "entered first step; only show headline; 2x2 Grid"
        self.game_mode.active_graph = self.graph
        self.game_mode.buttons['previous'].deactivate()
        self.game_mode.buttons['next'].deactivate()
        self.game_mode.show_points = False

    def run(self):
        pass

    def is_finished(self):
        return self.graph.is_solved()

    def finish(self):
        self.game_mode.buttons['next'].activate()

    def exit(self):
        self.game_mode.buttons['previous'].activate()


class TutorialStep2(GameStep):
    def __init__(self, game_mode):
        super().__init__(game_mode)

        self.graph = GraphFactory.generate_grid((3, 3))

    def enter(self):
        self.game_mode.headline = "entered second step; show points; 3x3 Grid"
        self.game_mode.active_graph = self.graph
        self.game_mode.buttons['previous'].activate()
        self.game_mode.buttons['next'].deactivate()
        self.game_mode.buttons['reset'].show()
        self.game_mode.show_points = True

    def run(self):
        pass

    def is_finished(self):
        pass

    def finish(self):
        self.game_mode.buttons['next'].activate()

    def exit(self):
        pass
