import time

from graph import GraphFactory
from .game_mode import GameMode


class GreedyJoining(GameMode):
    def __init__(self, size_factor=1):
        super().__init__(size_factor)

        self.active_graph = GraphFactory.generate_grid(self.size_factor, (5, 5), state_saving=True)
        self.standard_headline = 'In greedy joining you join those groups that improve your score the most. Try it!'
        self.headline_change_timestamp = None
        self.draw_necessary = True
        self.free_mode = False
        self.change_all_buttons('show')
        self.change_all_buttons('activate')
        self.buttons['reset2'].hide()

    def reset_graph(self, one_group=False):
        self.standard_headline = 'In greedy joining you join those groups that improve your score the most. Try it!'
        self.headline = self.standard_headline
        self.free_mode = False
        super().reset_graph(one_group)

    def graph_solved_event(self):
        pass

    def switch_to(self):
        pass

    def draw(self):
        pass

    def run(self):
        if self.active_graph.has_changed:
            if self.active_graph.get_score() == self.active_graph.optimal_score:
                self.active_graph.deactivated = True
                self.headline = 'Great! You solved it.'
            elif self.active_graph.get_best_score_improvement() == 0:
                self.standard_headline = ('Great! You followed the algorithm correctly and there is no more joining '
                                          'move left that could improve your score. Note that in this case the '
                                          'algorithm could not find the optimal solution. Can you find it?')
                self.headline = self.standard_headline
                self.headline_change_timestamp = time.time()
                self.free_mode = True
                self.draw_necessary = True
            elif ((not self.free_mode) and
                  self.active_graph.get_score() - self.active_graph.prev_state.get_score() >
                  self.active_graph.prev_state.get_best_score_improvement()):
                self.active_graph = self.active_graph.prev_state
                self.headline = 'That is not the best move.'
                self.headline_change_timestamp = time.time()
                self.move_vertex = None
                self.move_group = None
            self.active_graph.save_state()
        if self.headline_change_timestamp is not None and time.time() - self.headline_change_timestamp > 3:
            self.headline_change_timestamp = None
            self.headline = self.standard_headline
            self.draw_necessary = True

    def exit(self):
        pass
