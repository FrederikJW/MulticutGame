import pygame

import colors
from colors import *
from utils import add_pos


class Button:
    def __init__(self, label, pos, size, color_style, action_func=None, offset=(0, 0)):
        if color_style == 'red':
            self.background_color = RED
            self.hover_color = WHITE
            self.border_color = DARK_RED
        elif color_style == 'green':
            self.background_color = GREEN
            self.hover_color = WHITE
            self.border_color = DARK_GREEN
        else:
            self.background_color = BLUE
            self.hover_color = WHITE
            self.border_color = DARK_BLUE

        self.deactive_background_color = GREY
        self.deactive_border_color = DARK_GREY

        self.text_color = WHITE

        self.action_func = action_func
        self.hovers = False
        self.deactivated = False
        self.hidden = False
        self.label = label

        self.font = pygame.font.SysFont('Ariel', 32)
        self.text_surface = self.font.render(label, True, self.text_color)
        self.text_rec = self.text_surface.get_rect()
        self.text_rec.center = (size[0] / 2, size[1] / 2)

        self.offset = offset
        self.surface = pygame.Surface(size)
        # make transparent background, read more here: https://riptutorial.com/pygame/example/23788/transparency
        self.surface.fill(COLOR_KEY)
        self.surface.set_colorkey(COLOR_KEY)
        self.rec = pygame.Rect(*pos, *size)
        self.draw()

    def draw(self):
        if self.hidden:
            self.surface.fill(COLOR_KEY)
            return

        fill_color, border_color, text_color = self.get_colors()

        self.text_surface = self.font.render(self.label, True, text_color)
        rec = self.surface.get_rect()
        rec.move(add_pos((rec.x, rec.y), self.offset))
        center = rec.center
        pygame.draw.rect(self.surface, border_color, rec, border_radius=10)
        rec.width = rec.width - 4
        rec.height = rec.height - 4
        rec.center = center
        pygame.draw.rect(self.surface, fill_color, rec, border_radius=8)
        self.surface.blit(self.text_surface, self.text_rec)

    def get_colors(self):
        if self.deactivated:
            return self.deactive_background_color, self.deactive_border_color, colors.DARK_GREY
        if self.hovers:
            return self.hover_color, self.border_color, BLACK
        return self.background_color, self.border_color, self.text_color

    def hover(self, hovers):
        if hovers and not self.hovers:
            self.hovers = True
            self.draw()
            return True
        elif not hovers and self.hovers:
            self.hovers = False
            self.draw()
            return True
        return False

    def hide(self):
        self.hidden = True
        self.draw()

    def show(self):
        self.hidden = False
        self.draw()

    def deactivate(self):
        self.deactivated = True
        self.draw()

    def activate(self):
        self.deactivated = False
        self.draw()

    def objects(self):
        return self.surface, self.rec

    def collides(self, pos):
        if self.hidden or self.deactivated:
            return False
        return self.rec.collidepoint(pos)

    def action(self):
        if self.action_func is not None:
            self.action_func()
