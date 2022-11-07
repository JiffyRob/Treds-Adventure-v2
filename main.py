"""
Main - runs game and holds game loop.
Has Access to all other modules
"""
import pygame

from bush import util

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

    def run(self):
        self.screen = pygame.display.set_mode(util.rvec(self.screen_size))
        self.running = True
        dt = 0
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

            self.screen.fill(self.bgcolor)
            pygame.display.update()

            dt = self.clock.tick(self.fps)


Game().run()
