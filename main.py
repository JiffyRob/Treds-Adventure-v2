"""
Main - runs game and holds game loop.
Has Access to all other modules
"""
import pygame

import player
from bush import entity, util, level, color

pygame.init()


class Game:
    def __init__(self):
        ## Basic Pygame Boilerplate Variables (BPBV)
        self.screen_size = pygame.Vector2(640, 480)
        self.screen = None
        self.clock = pygame.time.Clock()
        self.fps = 500
        self.running = False
        self.bgcolor = color.GREY
        ## game variables
        self.player = player.Player(self.screen_size / 2, self.screen_size * 2)
        self.entity_group = level.TopDownGroup(
            cam_size=self.screen_size,
            map_size=self.screen_size * 2,
            pos=(0, 0),
            follow=self.player,
        )
        self.entity_group.add(self.player)

    def run(self):
        self.screen = pygame.display.set_mode(util.rvec(self.screen_size))
        self.running = True
        dt = 0
        # initial screen setup
        self.screen.fill(self.bgcolor)
        running = True
        while True:
            if not running:
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.screen.fill(self.bgcolor)
            self.entity_group.update(dt / 1000)
            self.entity_group.draw(self.screen)
            pygame.display.flip()
            dt = self.clock.tick(60)

        # after the game loop
        # reset things
        pygame.quit()
        self.screen = None

    def quit(self):
        self.running = False


Game().run()
