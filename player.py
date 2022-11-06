"""
Player.py

Holds the player class
"""
import pygame
import engine.entities as entities


class Player(entities.Entity):
    def __init__(self, id, pos):
        geo_params = {
            "shape": "circle",
            "params": {
                "color": (255, 0, 0),
                "radius": 16,
            },
        }
        bindings = {
            pygame.K_UP: self.up,
            pygame.K_DOWN: self.down,
            pygame.K_LEFT: self.left,
            pygame.K_RIGHT: self.right,
        }
        super().__init__(
            id=id,
            pos=pos,
            components=(
                entities.GeometryRender(self, 0, geo_params),
                entities.BasicKeyInput(self, 1, bindings, dt=True),
            ),
        )
        self.speed = 64 / 1000

    def up(self, dt):
        self.pos.y -= self.speed * dt

    def down(self, dt):
        self.pos.y += self.speed * dt

    def left(self, dt):
        self.pos.x -= self.speed * dt

    def right(self, dt):
        self.pos.x += self.speed * dt
