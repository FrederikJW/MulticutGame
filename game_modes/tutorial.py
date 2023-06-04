from .walkthrough_game_mode import WalkthroughGameMode, GameStep


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


class TutorialStep1(GameStep):
    def enter(self):
        self.game_mode.headline = "entered first step; only show headline"
        self.game_mode.buttons['previous'].deactivate()
        self.game_mode.buttons['next'].activate()
        self.game_mode.show_points = False

    def run(self):
        pass

    def is_finished(self):
        pass

    def finish(self):
        self.game_mode.buttons['next'].activate()

    def exit(self):
        self.game_mode.buttons['previous'].activate()


class TutorialStep2(GameStep):
    def enter(self):
        self.game_mode.headline = "entered second step; show points"
        self.game_mode.buttons['previous'].activate()
        self.game_mode.buttons['next'].deactivate()
        self.game_mode.show_points = True

    def run(self):
        pass

    def is_finished(self):
        pass

    def finish(self):
        self.game_mode.buttons['next'].activate()

    def exit(self):
        pass
