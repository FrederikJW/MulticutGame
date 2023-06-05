from graph import GraphFactory
from .walkthrough_game_mode import WalkthroughGameMode, GameStep


class ImageSegmentation(WalkthroughGameMode):
    def __init__(self):
        super().__init__()

        self.graphs.update({
            0: GraphFactory.generate_grid((5, 5)),
        })

        # init steps
        self.init_game_steps([
            SegmentationStep1(self),
        ])

        # start with first step
        self.next_step()

        self.buttons['reset'].hide()


class SegmentationStep1(GameStep):
    def __init__(self, game_mode):
        super().__init__(game_mode)

        self.has_finished = False

    def enter(self):
        self.game_mode.headline = "Image Segmentation"
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
