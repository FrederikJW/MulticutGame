import gettext
import os

import constants
from button import Button
from .game_mode import GameMode

localedir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'locale')
de = gettext.translation('base', localedir, languages=['de'])
de.install()

_ = de.gettext


class WalkthroughGameMode(GameMode):
    def __init__(self):
        super().__init__()

        self.game_mode_offset = (self.rec[0], self.rec[1])

        # init buttons
        self.buttons = []
        margin_top = constants.MARGIN
        margin_right = constants.MARGIN
        size = (200, 40)
        pos_x = constants.GAME_MODE_SCREEN_SIZE[0] - margin_right - size[0]
        self.buttons.extend([
            Button(_('Previous'), (pos_x, margin_top), size, 'red', self.reset_graph, self.gamemode_offset),
            Button(_('Next'), (pos_x, margin_top + 50), size, 'red', self.regenerate_graph, self.gamemode_offset)
        ])

    def switch_to(self):
        pass

    def draw(self):
        self.graph.draw(highlight_group)
        self.print_score()
        self.surface.blit(*self.graph.objects())

    def run(self, events):
        pass

    def exit(self):
        pass
