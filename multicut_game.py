import gettext
import os
import sys
from enum import Enum
from functools import partial


import pygame

import colors
import constants
from button import Button
from game_modes import ClassicGameMode
from utils import sub_pos

localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
de = gettext.translation('base', localedir, languages=['de'])
de.install()

_ = de.gettext


class MulticutGame:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()

        # Set up font
        self.font = pygame.font.SysFont('Ariel', 32)
        self.text = self.font.render("0", True, colors.BLACK)

        # Set up screen
        self.screen = pygame.display.set_mode(constants.SCREEN_SIZE, pygame.SCALED)
        pygame.display.set_caption("Multicut Game")

        self.screen.fill(colors.WHITE)
        pygame.display.update()

        # Set up buttons
        self.buttons = []
        self.current_game_mode = None
        self.init_buttons()

        self.game_modes = {
            'level1': ClassicGameMode(*constants.GAME_MODE_SCREEN_OFFSET, *constants.SCREEN_SIZE, 'grid', 4, 4),
            'level2': ClassicGameMode(*constants.GAME_MODE_SCREEN_OFFSET, *constants.SCREEN_SIZE, 'grid', 5, 5),
            'level3': ClassicGameMode(*constants.GAME_MODE_SCREEN_OFFSET, *constants.SCREEN_SIZE, 'pentagram'),
            'stresstest': ClassicGameMode(*constants.GAME_MODE_SCREEN_OFFSET, *constants.SCREEN_SIZE, 'grid', 10, 10),
        }

    def init_buttons(self):
        margin_left = constants.MARGIN
        margin_right = constants.MARGIN
        size = (constants.GAME_MODE_SCREEN_OFFSET[0] - (margin_right + margin_left), 40)
        self.buttons.append(Button(_('Tutorial'), (margin_left, 190), size, 'blue', None))
        self.buttons.append(
            Button(f"{_('Level')} 1", (margin_left, 240), size, 'blue', partial(self.change_game_mode, 'level1')))
        self.buttons.append(
            Button(f"{_('Level')} 2", (margin_left, 290), size, 'blue', partial(self.change_game_mode, 'level2')))
        self.buttons.append(
            Button(f"{_('Level')} 3", (margin_left, 340), size, 'blue', partial(self.change_game_mode, 'level3')))
        self.buttons.append(
            Button(f"Stresstest", (margin_left, 390), size, 'blue', partial(self.change_game_mode, 'stresstest')))
        self.buttons.append(Button('Empty', (margin_left, 440), size, 'blue', None))
        self.buttons.append(Button('Empty', (margin_left, 490), size, 'blue', None))
        self.buttons.append(Button('Empty', (margin_left, 540), size, 'blue', None))
        self.buttons.append(Button('Empty', (margin_left, 590), size, 'blue', None))
        self.buttons.append(Button(_('Quit'), (margin_left, 640), size, 'red', self.quit))

    def change_game_mode(self, game_mode):
        if self.current_game_mode == game_mode:
            return
        if game_mode not in self.game_modes.keys():
            return
        if self.current_game_mode is not None:
            self.game_modes[self.current_game_mode].exit()
        if game_mode is not None:
            self.game_modes[game_mode].switch_to()
        self.current_game_mode = game_mode

    def run(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()
            events = pygame.event.get()
            # Handle events
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons:
                        if button.collides(mouse_pos):
                            button.action()

            # draw buttons
            for button in self.buttons:
                button.hover(button.collides(mouse_pos))
                self.screen.blit(*button.objects())

            # run game mode
            if self.current_game_mode is not None:
                game_mode = self.game_modes[self.current_game_mode]
                game_mode.run(events)
                self.screen.blit(*game_mode.objects())

            # draw border
            rec = pygame.Rect(sub_pos(constants.GAME_MODE_SCREEN_OFFSET, (2, 0)), (2, constants.SCREEN_SIZE[1]))
            pygame.draw.rect(self.screen, colors.GREY, rec)

            pygame.display.update()
            self.clock.tick(constants.FRAMES_PER_SECOND)

    def quit(self):
        pygame.quit()
        sys.exit()
