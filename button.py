import pygame

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
        self.text_color = WHITE

        self.action_func = action_func
        self.hovers = False
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
        self.draw(self.background_color, self.border_color, self.text_color)

    def draw(self, fill_color, border_color, text_color):
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

    def hover(self, hovers):
        if hovers and not self.hovers:
            self.hovers = True
            self.draw(self.hover_color, self.border_color, BLACK)
            return True
        elif not hovers and self.hovers:
            self.hovers = False
            self.draw(self.background_color, self.border_color, self.text_color)
            return True
        return False

    def objects(self):
        return self.surface, self.rec

    def collides(self, pos):
        return self.rec.collidepoint(pos)

    def action(self):
        if self.action_func is not None:
            self.action_func()
