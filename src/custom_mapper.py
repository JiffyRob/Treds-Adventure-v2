import os

import pygame

import game_objects
from bush import asset_handler, entity, physics
from bush.mapping import group, mapping


class MapLoader(mapping.MapLoader):
    def __init__(self, screen_size, player):
        self.collision_group = pygame.sprite.Group()
        self.group_creators = {
            "main": lambda map_size: group.TopDownGroup(
                screen_size, map_size, (0, 0), player
            ),
            "player": lambda x: pygame.sprite.GroupSingle(),
            "collision": lambda x: pygame.sprite.Group(),
            "event": lambda x: group.EntityGroup(),
            "farmplants_green": lambda x: pygame.sprite.Group(),
            "farmplants_orange": lambda x: pygame.sprite.Group(),
            "farmplants": lambda x: pygame.sprite.Group(),
        }
        self.current_sprite_groups = None
        self.sprite_classes = {"bush": game_objects.Throwable}
        self.sprite_groups = {
            game_objects.Throwable: (
                "main",
                "collision",
            )
        }
        self.player_groups = ("main", "player")
        self.default_groups = ("main",)
        self.default_player_layer = 4  # second layer (default sub)
        self.mask_loader = asset_handler.AssetHandler("resources/masks")
        super().__init__("tiled/maps", sprite_creator=self.create_sprite)

    def create_sprite(self, obj, sprite_group):
        if obj.type is None:
            groups = obj.properties.get("groups", ", ".join(self.default_groups)).split(
                ", "
            )
            print(groups)
            sprite = entity.Entity(
                pos=obj.pos,
                layer=obj.layer * 3 + 1,
                groups=(*[self.current_sprite_groups[key] for key in groups],),
                id=obj.name,
                surface=obj.image,
                topleft=True,
            )
            if "collision" in groups:
                mask = obj.properties.get("mask", None)
                if mask is None:
                    mask = pygame.mask.from_surface(sprite.image)
                else:
                    mask = pygame.mask.from_surface(self.mask_loader.load(mask))
                sprite.physics_data = physics.PhysicsData(
                    physics.TYPE_STATIC, self.current_sprite_groups["collision"]
                )
                sprite.mask = mask
            return
        self.sprite_classes[obj.type](
            pos=obj.pos,
            layer=obj.layer * 3 + 1,
            groups=(
                sprite_group,
                *[
                    self.current_sprite_groups[key]
                    for key in self.sprite_groups.get(obj.type, self.default_groups)
                ],
            ),
            id=obj.name,
            surface=obj.image,
            topleft=True,
            **{
                f"{key}_group": value
                for key, value in self.current_sprite_groups.items()
            },
        )

    def load_map(self, tmx_path, engine, player_pos):
        tmx_map = self.loader.load(tmx_path)
        map_size = pygame.Vector2(
            tmx_map.width * tmx_map.tilewidth, tmx_map.height * tmx_map.tileheight
        )
        self.current_sprite_groups = {
            key: value(map_size) for key, value in self.group_creators.items()
        }
        sprite_group, properties = super().load(tmx_path)
        current_player = engine.player
        current_player.kill()
        player_layer = properties.get("player_layer", 0) or self.default_player_layer
        for key in self.player_groups:
            self.current_sprite_groups[key].add(current_player)
        current_player.change_layer(player_layer)
        current_player.change_collision_group(self.current_sprite_groups["collision"])
        current_player.change_environment(None)
        current_player.rect.center = current_player.pos = pygame.Vector2(player_pos)
        self.current_sprite_groups["main"].follow = current_player
        self.current_sprite_groups["main"].add(sprite_group)
        physics.optimize_for_physics(self.current_sprite_groups["collision"])
        groups = self.current_sprite_groups
        self.current_sprite_groups = None
        return groups, properties.get("script", None)
