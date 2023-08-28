from graph import GraphFactory
from .walkthrough_game_mode import WalkthroughGameMode, GameStep


class Tutorial(WalkthroughGameMode):
    def __init__(self, size_factor=1):
        super().__init__(size_factor)

        self.graphs.update({
            0: GraphFactory.generate_grid(self.size_factor, (2, 2), 22),
            1: GraphFactory.generate_grid(self.size_factor, (3, 3), 5548),
            2: GraphFactory.generate_grid(self.size_factor, (5, 5)),
        })

        # init steps
        self.init_game_steps([
            TutorialStep1(self),
            TutorialStep2(self),
            TutorialStep3(self),
            TutorialStep4(self),
        ])

        # start with first step
        self.next_step()

        self.buttons['reset'].hide()


class TutorialStep1(GameStep):
    def __init__(self, game_mode):
        super().__init__(game_mode)

        self.has_finished = False

    def enter(self):
        self.game_mode.standard_headline = ("Welcome to the Multicut Game. The goal of the minimal multicut problem is "
                                            "to cut the edges of a graph "
                                            "such that the sum of the weight of the cut edges is minimal. In this game "
                                            "a red edge has a weight of -1 and a green edge has a weight of 1. This "
                                            "means you should prefer cutting red edges as their weight is negative and "
                                            "smaller than the weight of green edges. Click on next. (\">\")")
        self.game_mode.set_active_graph(0)
        self.game_mode.reset_graph(True)
        self.game_mode.active_graph.deactivated = True
        self.game_mode.change_all_buttons('hide')
        self.game_mode.buttons['solution'].set_mode(False)
        self.game_mode.buttons['movegroup'].set_mode(False)
        self.game_mode.buttons['previous'].deactivate()
        self.game_mode.buttons['previous'].show()
        self.game_mode.buttons['next'].activate()
        self.game_mode.buttons['next'].show()
        self.game_mode.show_points = False

        if self.has_finished:
            self.game_mode.buttons['next'].activate()


class TutorialStep2(GameStep):
    def __init__(self, game_mode):
        super().__init__(game_mode)

        self.has_finished = False

    def enter(self):
        self.game_mode.standard_headline = ("Try to cut the given graph by clicking holding and dragging your mouse "
                                            "over the edges you want to cut such that the score is minimized. A cut is "
                                            "only made if it is valid, which means that if an edge between two "
                                            "vertices is cut those vertices can't be connected by any other path.")
        self.game_mode.set_active_graph(0)
        self.game_mode.reset_graph(True)
        self.game_mode.active_graph.deactivated = False
        self.game_mode.change_all_buttons('hide')
        self.game_mode.buttons['solution'].set_mode(False)
        self.game_mode.buttons['movegroup'].set_mode(False)
        self.game_mode.buttons['previous'].show()
        self.game_mode.buttons['previous'].activate()
        self.game_mode.buttons['previous'].show()
        self.game_mode.buttons['next'].deactivate()
        self.game_mode.buttons['next'].show()
        self.game_mode.show_points = True
        self.game_mode.draw_necessary = True

    def is_finished(self):
        is_finished = self.game_mode.active_graph.is_solved()
        if is_finished:
            self.has_finished = True
        return is_finished

    def finish(self):
        self.game_mode.headline = "Great you solved it. Click on next or click on reset to try again."
        self.game_mode.active_graph.deactivated = True
        self.game_mode.buttons['reset2'].show()
        self.game_mode.buttons['reset2'].activate()
        self.game_mode.buttons['next'].activate()
        self.game_mode.draw_necessary = True


class TutorialStep3(GameStep):
    def __init__(self, game_mode):
        super().__init__(game_mode)

        self.has_finished = False

    def enter(self):
        self.game_mode.standard_headline = ("You can also start solving with all edges cut initially and moving the "
                                            "vertices into groups. Try to solve this graph.")
        self.game_mode.set_active_graph(1)
        self.game_mode.reset_graph(False)
        self.game_mode.active_graph.deactivated = False
        self.game_mode.change_all_buttons('hide')
        self.game_mode.buttons['solution'].set_mode(False)
        self.game_mode.buttons['movegroup'].set_mode(False)
        self.game_mode.buttons['previous'].activate()
        self.game_mode.buttons['previous'].show()
        self.game_mode.buttons['next'].deactivate()
        self.game_mode.buttons['next'].show()
        self.game_mode.show_points = True
        self.game_mode.draw_necessary = True

    def is_finished(self):
        is_finished = self.game_mode.active_graph.is_solved()
        if is_finished:
            self.has_finished = True
        return is_finished

    def finish(self):
        self.game_mode.headline = "Great you solved it. Click on next or click on reset to try again."
        self.game_mode.active_graph.deactivated = True
        self.game_mode.buttons['reset'].show()
        self.game_mode.buttons['reset'].activate()
        self.game_mode.buttons['next'].activate()
        self.game_mode.draw_necessary = True


class TutorialStep4(GameStep):
    def __init__(self, game_mode):
        super().__init__(game_mode)

        self.has_finished = False

    def enter(self):
        self.game_mode.standard_headline = ("The one button on the right lets you switch to group mode where you can "
                                            "move and merge whole groups instead of single vertices. If you can't "
                                            "solve a graph there is the other button which shows the solution. Try "
                                            "them out by solving this graph.")
        self.game_mode.set_active_graph(2)
        self.game_mode.reset_graph(True)
        self.game_mode.active_graph.deactivated = False
        self.game_mode.change_all_buttons('show')
        self.game_mode.change_all_buttons('activate')
        self.game_mode.buttons['next'].deactivate()
        self.game_mode.show_points = True
        self.game_mode.draw_necessary = True

    def is_finished(self):
        is_finished = self.game_mode.active_graph.is_solved()
        if is_finished:
            self.has_finished = True
        return is_finished

    def finish(self):
        self.game_mode.headline = "Great this is the end of the tutorial. You can now try out other gamemodes."
        self.game_mode.active_graph.deactivated = True
        self.game_mode.draw_necessary = True
