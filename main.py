"""
    |
    |
----------
    |
    |
    |
Main.py:

Holds main game loop
Runs and coordinates all else
"""
import pygame

import engine.entities as entities
import engine.util as util
import player

pygame.init()


class TredsAdventure:
    """
    Main Game class
    Init then call run() to run the game
    """

    def __init__(self):
        self.screen = None
        self.screen_size = pygame.Vector2(480, 270)
        self.running = False
        self.physics_engine = None
        self.clock = pygame.time.Clock()
        self.registry = entities.ComponentRegistry()
        self.player = player.Player(None, self.screen_size / 2)
        self.registry.add_entity(self.player)

    def run(self):
        self.screen = pygame.display.set_mode(
            util.round_vector(self.screen_size), pygame.SCALED, vsync=True
        )
        self.running = True
        dt = 0
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                else:
                    self.send_event(event)

            self.registry.update(dt, "input")
            self.registry.update(dt, "physics")
            self.screen.fill((0, 255, 0))
            self.registry.update(dt, "state")
            self.registry.update(dt, "render")
            self.registry.render(self.screen)
            pygame.display.update()
            dt = self.clock.tick(60)
        pygame.quit()

    def quit(self):
        self.running = False

    def send_event(self, event):
        pass  # print(event)


if __name__ == "__main__":
    game = TredsAdventure()
    game.run()
