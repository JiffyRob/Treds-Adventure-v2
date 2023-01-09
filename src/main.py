"""
Main - runs game and holds game loop.
Has Access to all other modules
"""
# normal imports
import pygame

import mapping
from bush import color, util, event_binding, asset_handler

loader = asset_handler.glob_loader
from bush.ai import controller

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
        # game control state
        self.state = "map"
        self.controller = event_binding.EventHandler({})
        self.controller.update_bindings(loader.load("data/input_bindings.json"))
        # initial map load
        self.groups = None
        self.main_group = None
        self.player = None
        self.load_map("tiled/test_map.tmx")

    def load_map(self, path):
        self.groups = mapping.load_map(path, self.screen_size)
        self.main_group = self.groups["main"]
        self.player = self.groups["player"].sprite

    def update_sprites(self, dt):
        self.main_group.update(dt)

    def draw_sprites(self):
        self.main_group.draw(self.screen)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            self.controller.process_event(event)
            self.player.event(event)

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
            dt = self.clock.tick(self.fps) / 1000

        pygame.quit()
        self.screen = None

    def quit(self):
        self.running = False


Game().run()
