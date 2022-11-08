"""
Main - runs game and holds game loop.
Has Access to all other modules
"""
import pygame

import player
from bush import entity, util

pygame.init()


class Game:
    def __init__(self):
        ## Basic Pygame Boilerplate Variables (BPBV)
        self.screen_size = pygame.Vector2(640, 480)
        self.screen = None
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = False
        self.bgcolor = (57, 57, 57)
        ## game variables
        self.player = player.Player(self.screen_size / 2, 0)
        self.entity_group = entity.EntityGroup(self.player)

    def run(self):
        self.screen = pygame.display.set_mode(util.rvec(self.screen_size))
        self.running = True
        dt = 0
        while self.running:
            # get events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

            # clear screen
            self.screen.fill(self.bgcolor)
            # update input, physics
            self.entity_group.update(dt, ("input", "physics"))
            # render
            self.entity_group.render(self.screen)
            # update ai and state
            self.entity_group.update(dt, ("state_machine", "ai"))
            # update screen
            pygame.display.update()
            # tick and get delta time
            dt = self.clock.tick(self.fps)

        # after the game loop
        # reset things
        pygame.quit()
        self.screen = None

    def quit(self):
        self.running = False


Game().run()
