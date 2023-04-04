import pygame


class Button:
    def __init__(self, label, x, y, width, height, fill_color, outline_color, action_func=None):
        self.label = label
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fill_color = fill_color
        self.outline_color = outline_color
        self.action_func = action_func

        self.font = pygame.font.SysFont('Ariel', 32)
        self.text_surface = self.font.render(label, True, (0, 0, 0))
        self.text_rec = self.text_surface.get_rect()
        self.text_rec.center = ((self.x+(self.width/2)), (self.y+(self.height/2)))

        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(self.fill_color)  # white color
        self.surface.blit(self.text_surface, self.text_rec)
        self.rec = pygame.Rect(self.x, self.y, self.width, self.height)

    def objects(self):
        return self.surface, self.rec

    def collides(self, pos):
        return self.rec.collidepoint(pos)

    def action(self):
        if self.action_func is None:
            return
        self.action_func()
