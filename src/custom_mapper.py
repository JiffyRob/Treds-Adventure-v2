import os

import pygame

import game_objects
from bush import asset_handler, level, mapping


class MapLoader(mapping.MapLoader):
    def __init__(self, screen_size, player):
        self.collision_group = pygame.sprite.Group()
        group_creators = {
            "main": lambda map_size: level.TopDownGroup(
                screen_size, map_size, (0, 0), player
            ),
            "player": lambda x: pygame.sprite.GroupSingle(),
            "collision": lambda x: pygame.sprite.Group(),
            "event": lambda x: level.EntityGroup(),
            "farmplants_green": lambda x: pygame.sprite.Group(),
            "farmplants_orange": lambda x: pygame.sprite.Group(),
            "farmplants": lambda x: pygame.sprite.Group(),
        }
        sprite_creators = {"bush": game_objects.Throwable}
        self.sprite_groups = {
            game_objects.Throwable: (
                "main",
                "collision",
            )
        }
        self.player_groups = ("main", "player")
        self.default_player_layer = 4  # second layer (default sub)
        super().__init__(
            sprite_creators,
            group_creators,
            self.get_sprite_groups,
            mask_load_path=os.path.join(
                asset_handler.glob_loader.base, "./resources/masks"
            ),
            map_load_path=os.path.join(asset_handler.glob_loader.base, "./tiled/maps"),
        )

    def get_sprite_groups(self, sprite, is_nonsprite):
        if is_nonsprite:
            return ("main",)
        return self.sprite_groups[type(sprite)]

    def load_map(self, tmx_path, engine, player_pos):
        groups, properties = super().load_map(tmx_path)
        current_player = engine.player
        current_player.kill()
        player_layer = properties.get("player_layer", 0) or self.default_player_layer
        for key in self.player_groups:
            groups[key].add(current_player)
        current_player.change_layer(player_layer)
        current_player.change_collision_group(groups["collision"])
        current_player.change_environment(None)
        current_player.rect.center = current_player.pos = pygame.Vector2(player_pos)
        groups["main"].follow = current_player
        return groups, properties.get("script", None)
