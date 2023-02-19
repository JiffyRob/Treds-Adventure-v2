import pygame


class JoyCursor(pygame.sprite.Sprite):
    def __init__(self, surface, hotspot):
        super().__init__()
        self.hotspot = hotspot
        self.surface = surface
        self.rect = self.surface.get_rect()
        self.visible = False
        self.blank_surf = pygame.Surface((0, 0))
        self.image = self.blank_surf
        self.layer = 1000

    def enable(self):
        self.visible = True
        pygame.mouse.set_visible(False)

    def disable(self):
        self.visible = False
        pygame.mouse.set_visible(True)

    def hide(self):
        self.visible = False
        pygame.mouse.set_visible(False)

    def move_to(self, pos):
        pygame.mouse.set_pos(pos)

    def move_by(self, amount):
        pygame.mouse.set_pos(pygame.mouse.get_pos() + amount)

    def update(self, dt):
        if self.visible:
            self.image = self.surface
        else:
            self.image = self.blank_surf
        self.rect.topleft = pygame.mouse.get_pos() - self.hotspot

    def limit(self, map_rect):
        pass
