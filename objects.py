"""
Objects.py

Basic stationary game objects
"""
import pygame
import engine.entities as entities


class Wall(entities.Entity):
    def __init__(self, id: int, rect: pygame.Rect):
        geo_params = {"shape": "rect", "params": {"color": (100, 100, 100)}}

        super().__init__(
            id=id,
            pos=rect.topleft,
            components={"rendering": entities.GeometryRender(self, 12, geo_params)},
        )
