"""
Main - runs game and holds game loop.
Has Access to all other modules
"""
# normal imports
import pygame

import mapping
from bush import color, util

pygame.init()


class Game:
    def __init__(self):
        # Basic Pygame Boilerplate Variables (BPBV)
        self.screen_size = pygame.Vector2(640, 480)
        self.screen = None
        self.clock = pygame.time.Clock()
        self.fps = 30
        self.running = False
        self.bgcolor = color.GREY
        self.screen = pygame.display.set_mode(util.rvec(self.screen_size))
        # initial map load
        self.groups = None
        self.main_group = None
        self.load_map("tiled/test_map.tmx")

    def load_map(self, path):
        self.groups = mapping.load_map(path, self.screen_size)
        self.main_group = self.groups["main"]

    def update_sprites(self, dt):
        for sprite in self.main_group.sprites():
            sprite.update(dt)

    def draw_sprites(self):
        self.main_group.draw(self.screen)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

    def run(self):
        self.screen = pygame.display.set_mode(util.rvec(self.screen_size))
        self.screen.fill(self.bgcolor)

        self.running = True
        dt = 0
        while self.running:
            self.handle_events()
            self.screen.fill(self.bgcolor)
            self.update_sprites(dt)
            self.draw_sprites()
            pygame.display.flip()
            dt = self.clock.tick(self.fps)

        pygame.quit()
        self.screen = None

    def quit(self):
        self.running = False


Game().run()
