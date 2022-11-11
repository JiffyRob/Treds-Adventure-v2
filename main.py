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
        self.fps = 500
        self.running = False
        self.bgcolor = (57, 57, 57)
        ## game variables
        self.player = player.Player(self.screen_size / 2, 0)
        self.entity_group = entity.EntityGroup(self.player)

    def run(self):
        self.screen = pygame.display.set_mode(util.rvec(self.screen_size))
        self.running = True
        dt = 0
        min_fps = 2000  # pygame limit
        # initial screen setup
        self.screen.fill(self.bgcolor)
        self.entity_group.render(self.screen)
        pygame.display.flip()
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
            rects = self.entity_group.render(self.screen)
            # update ai and state
            self.entity_group.update(dt, ("state_machine", "ai"))
            # update screen
            pygame.display.update(rects)
            # tick and get delta time
            dt = self.clock.tick(self.fps)
            # keep fps data
            fps = self.clock.get_fps()
            if fps != 0:
                min_fps = min(min_fps, fps)

        # after the game loop
        # reset things
        pygame.quit()
        self.screen = None
        # print minimum fps
        print(f"Game terminated successfully (min fps {min_fps})")

    def quit(self):
        self.running = False


Game().run()
