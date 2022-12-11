"""
Main - runs game and holds game loop.
Has Access to all other modules
"""
import pygame

import game_objects
import player
from bush import color, entity, level, physics, util

pygame.init()


class Game:
    def __init__(self):
        # Basic Pygame Boilerplate Variables (BPBV)
        self.screen_size = pygame.Vector2(640, 480)
        self.screen = None
        self.clock = pygame.time.Clock()
        self.fps = 500
        self.running = False
        self.bgcolor = color.GREY
        self.screen = pygame.display.set_mode(util.rvec(self.screen_size))
        # game variables
        # sprites
        self.player = player.Player(self.screen_size / 2)
        block = game_objects.Block(self.screen_size * 0.75)
        # groups
        self.entity_group = level.TopDownGroup(
            cam_size=self.screen_size,
            map_size=self.screen_size,
            pos=(0, 0),
            follow=self.player,
        )
        self.entity_group.add(self.player, block)
        self.physics_group = level.PhysicsGroup(self.player, block)
        print(list(self.entity_group.sprites()))
        pygame.quit()

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
            self.physics_group.update(dt / 1000)
            self.entity_group.update(dt / 1000)
            self.entity_group.draw(self.screen)
            for sprite in self.entity_group.sprites():
                self.screen.set_at(util.rvec(sprite.pos), color.RED)
                pygame.draw.rect(self.screen, color.RED, sprite.rect, width=1)
            pygame.display.flip()
            dt = self.clock.tick(60)

        # after the game loop
        # reset things
        pygame.quit()
        self.screen = None

    def quit(self):
        self.running = False


Game().run()
