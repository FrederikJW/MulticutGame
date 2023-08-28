import sys
from functools import partial

import pygame

import colors
import constants
import utils
from button import ActionButton
from game_modes import ClassicGameMode, Tutorial, ImageSegmentation, GreedyJoining
from utils import sub_pos


class MulticutGame:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()

        # Set up font
        self.font = pygame.font.SysFont('Ariel', 32)
        loading_text = self.font.render("Loading... Please wait!", True, colors.BLACK)
        loading_text_rec = loading_text.get_rect()
        loading_text_rec.center = utils.round_pos(utils.div_pos(constants.SCREEN_SIZE, (2, 2)))

        # Set up screen
        self.screen_size = constants.SCREEN_SIZE
        self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
        pygame.display.set_caption("Multicut Game")

        self.screen.fill(colors.WHITE)
        self.screen.blit(loading_text, loading_text_rec)
        self.surface = pygame.Surface(self.screen_size)
        self.surface.fill(colors.WHITE)
        pygame.display.update()

        # Set up buttons
        self.buttons = []
        self.current_game_mode = None
        self.init_buttons()

        self.game_modes = {'tutorial': Tutorial(), 'level1': ClassicGameMode('grid', 4, 4),
                           'level2': ClassicGameMode('grid', 5, 5), 'level3': ClassicGameMode('pentagram'),
                           'stresstest': ClassicGameMode('grid', 10, 10, 0.5), 'imagesegmentation': ImageSegmentation(),
                           'greedyjoining': GreedyJoining(), }

    def init_buttons(self):
        margin_left = constants.MENU_MARGIN
        margin_right = constants.MENU_MARGIN
        size = (constants.GAME_MODE_SCREEN_OFFSET[0] - (margin_right + margin_left), 40)
        self.buttons.append(ActionButton('Tutorial', (margin_left, 190), size, 'blue',
                                         action_func=partial(self.change_game_mode, 'tutorial')))
        self.buttons.append(ActionButton('Level' + " 1", (margin_left, 240), size, 'blue',
                                         action_func=partial(self.change_game_mode, 'level1')))
        self.buttons.append(ActionButton('Level' + " 2", (margin_left, 290), size, 'blue',
                                         action_func=partial(self.change_game_mode, 'level2')))
        self.buttons.append(ActionButton('Level' + " 3", (margin_left, 340), size, 'blue',
                                         action_func=partial(self.change_game_mode, 'level3')))
        self.buttons.append(ActionButton('Stresstest', (margin_left, 390), size, 'blue',
                                         action_func=partial(self.change_game_mode, 'stresstest')))
        self.buttons.append(ActionButton('Image Segmentation', (margin_left, 440), size, 'blue',
                                         action_func=partial(self.change_game_mode, 'imagesegmentation')))
        self.buttons.append(ActionButton('Greedy Joining', (margin_left, 490), size, 'blue',
                                         action_func=partial(self.change_game_mode, 'greedyjoining')))
        self.buttons.append(ActionButton('', (margin_left, 540), size, 'blue'))
        self.buttons[-1].deactivate()
        self.buttons.append(ActionButton('', (margin_left, 590), size, 'blue'))
        self.buttons[-1].deactivate()
        self.buttons.append(ActionButton('Quit', (margin_left, 640), size, 'red', action_func=self.quit))

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
            self.surface.fill(colors.WHITE)

            screen_size_ratio = (
                constants.SCREEN_SIZE[0] / self.screen_size[0], constants.SCREEN_SIZE[1] / self.screen_size[1])

            mouse_pos = utils.round_pos(utils.mult_pos(pygame.mouse.get_pos(), screen_size_ratio))
            events = pygame.event.get()
            # Handle events
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.VIDEORESIZE:
                    self.screen_size = event.dict['size']
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons:
                        if button.collides(mouse_pos):
                            button.action()

            # draw buttons
            for button in self.buttons:
                button.hover(button.collides(mouse_pos))
                self.surface.blit(*button.objects())

            # run game mode
            if self.current_game_mode is not None:
                game_mode = self.game_modes[self.current_game_mode]
                game_mode.main(events, mouse_pos)
                self.surface.blit(*game_mode.objects())

            # draw border
            rec = pygame.Rect(sub_pos(constants.GAME_MODE_SCREEN_OFFSET, (2, 0)), (2, constants.SCREEN_SIZE[1]))
            pygame.draw.rect(self.surface, colors.GREY, rec)

            self.screen.blit(pygame.transform.scale(self.surface, self.screen_size), (0, 0))
            pygame.display.update()
            self.clock.tick(constants.FRAMES_PER_SECOND)

    def quit(self):
        pygame.quit()
        sys.exit()
