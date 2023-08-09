import pygame

import colors
from colors import *
from utils import add_pos


class Button:
    def __init__(self, label, pos, size, color_style, offset=(0, 0)):
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

        self.hovers = False
        self.deactivated = False
        self.hidden = False
        self.label = label
        self.is_icon = False
        if label.__class__ != str:
            self.is_icon = True

        font_size = 32
        self.font = pygame.font.SysFont('Ariel', font_size)
        self.text_surface = self.font.render(self.label if not self.is_icon else '', True, self.text_color)
        self.text_rec = self.text_surface.get_rect()
        # if text is too big reduce font_size until it fits
        while self.text_rec.width > size[0] or self.text_rec.height > size[1]:
            font_size -= 1
            self.font = pygame.font.SysFont('Ariel', font_size)
            self.text_surface = self.font.render(self.label if not self.is_icon else '', True, self.text_color)
            self.text_rec = self.text_surface.get_rect()

        self.text_rec.center = (size[0] / 2, size[1] / 2)

        self.offset = offset
        self.surface = pygame.Surface(size)
        # make transparent background, read more here: https://riptutorial.com/pygame/example/23788/transparency
        self.surface.fill(COLOR_KEY)
        self.surface.set_colorkey(COLOR_KEY)
        self.rec = pygame.Rect(*pos, *size)

        if self.is_icon:
            self.is_icon = True
            rec = self.surface.get_rect()
            center = rec.center
            rec.size = (rec.width - 6, rec.height - 6)
            rec.center = center
            self.label = pygame.transform.scale(self.label, rec.size)

        self.draw_necessary = True

    def draw(self):
        if self.hidden:
            self.surface.fill(COLOR_KEY)
            return

        fill_color, border_color, text_color = self.get_colors()

        self.text_surface = self.font.render(self.label if not self.is_icon else '', True, text_color)
        rec = self.surface.get_rect()
        rec.move(add_pos((rec.x, rec.y), self.offset))
        center = rec.center
        pygame.draw.rect(self.surface, border_color, rec, border_radius=10)
        rec.width = rec.width - 4
        rec.height = rec.height - 4
        rec.center = center
        pygame.draw.rect(self.surface, fill_color, rec, border_radius=8)
        if not self.is_icon:
            self.surface.blit(self.text_surface, self.text_rec)
        else:
            self.surface.blit(self.label, rec)

    def get_colors(self):
        if self.deactivated:
            return self.deactive_background_color, self.deactive_border_color, colors.DARK_GREY
        if self.hovers:
            return self.hover_color, self.border_color, BLACK
        return self.background_color, self.border_color, self.text_color

    def hover(self, hovers):
        if hovers and not self.hovers:
            self.hovers = True
            self.draw_necessary = True
            return True
        elif not hovers and self.hovers:
            self.hovers = False
            self.draw_necessary = True
            return True
        return False

    def hide(self):
        self.hidden = True
        self.draw_necessary = True

    def show(self):
        self.hidden = False
        self.draw_necessary = True

    def deactivate(self):
        self.deactivated = True
        self.draw_necessary = True

    def activate(self):
        self.deactivated = False
        self.draw_necessary = True

    def objects(self):
        if self.draw_necessary:
            self.draw()
            self.draw_necessary = False
        return self.surface, self.rec

    def collides(self, pos):
        if self.hidden or self.deactivated:
            return False
        return self.rec.collidepoint(pos)

    def action(self):
        raise NotImplementedError


class ActionButton(Button):
    def __init__(self, label, pos, size, color_style, offset=(0, 0), action_func=None):
        super().__init__(label, pos, size, color_style, offset)
        self.action_func = action_func

    def action(self):
        if self.action_func is not None:
            self.action_func()


class Switch(Button):
    def __init__(self, label, pos, size, color_style, offset=(0, 0), second_label=None):
        super().__init__(label, pos, size, color_style, offset)
        self.switch_mode = False

        self.second_label = second_label
        if self.is_icon and second_label is not None:
            self.is_icon = True
            rec = self.surface.get_rect()
            center = rec.center
            rec.size = (rec.width - 6, rec.height - 6)
            rec.center = center
            self.second_label = pygame.transform.scale(second_label, rec.size)

    def switch(self):
        self.switch_mode = not self.switch_mode
        self.draw_necessary = True

    def set_mode(self, switch_mode):
        self.switch_mode = switch_mode

    def get_mode(self):
        return self.switch_mode

    def action(self):
        self.switch()

    def draw(self):
        if self.hidden:
            self.surface.fill(COLOR_KEY)
            return

        fill_color, border_color, text_color = self.get_colors()

        self.text_surface = self.font.render(self.label if not self.is_icon else '', True, text_color)
        rec = self.surface.get_rect()
        rec.move(add_pos((rec.x, rec.y), self.offset))
        center = rec.center
        pygame.draw.rect(self.surface, border_color, rec, border_radius=10)
        rec.width = rec.width - 4
        rec.height = rec.height - 4
        rec.center = center
        pygame.draw.rect(self.surface, fill_color, rec, border_radius=8)
        if not self.is_icon:
            self.surface.blit(self.text_surface, self.text_rec)
        else:
            rec = self.surface.get_rect()
            center = rec.center
            rec.size = (rec.width - 6, rec.height - 6)
            rec.center = center
            if self.get_mode() and self.second_label is not None:
                self.surface.blit(self.second_label, rec)
            else:
                self.surface.blit(self.label, rec)
