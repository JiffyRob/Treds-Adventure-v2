import os

import pygame

import environment
import event_objects
import game_objects
import player
from bush import asset_handler, entity, physics
from bush.mapping import group, mapping


class MapLoader(mapping.MapLoader):
    def __init__(self, engine, state):
        self.collision_group = pygame.sprite.Group()
        self.group_creators = {
            "main": lambda map_size: group.TopDownGroup(
                engine.screen_size, map_size, (0, 0), self.get_player()
            ),
            "player": lambda x: pygame.sprite.GroupSingle(),
            "collision": lambda x: pygame.sprite.Group(),
            "event": lambda x: group.EntityGroup(),
            "farmplants_green": lambda x: pygame.sprite.Group(),
            "farmplants_orange": lambda x: pygame.sprite.Group(),
            "farmplants": lambda x: pygame.sprite.Group(),
        }
        self.current_sprite_groups = None
        self.current_env_masks = None
        self.current_player = None
        self.engine = engine
        self.sprite_classes = {
            "bush": game_objects.Throwable,
            "teleport": event_objects.Teleport,
        }
        self.sprite_groups = {
            "bush": (
                "main",
                "collision",
            ),
            "teleport": (
                "main",
                "collision",
            ),
        }
        self.player_groups = ("main", "player")
        self.default_groups = ("main",)
        self.default_player_layer = 4  # second layer (default sub)
        self.mask_loader = asset_handler.AssetHandler("resources/masks")
        self.aux_cache = {}
        super().__init__(
            "tiled/maps",
            sprite_creator=self.create_sprite,
            tile_handler=self.handle_tile,
        )

    def get_player(self):
        return self.current_player

    def handle_tile(self, tile, sprite_group):
        terrain = tile.properties.get("terrain", None)
        mask = tile.properties.get("mask", None) or pygame.mask.from_surface(tile.image)
        if terrain:
            self.current_env_masks[terrain].draw(mask, tile.pos)
        groups = tile.properties.get("groups", None)
        if groups:
            sprite = entity.Entity(
                tile.pos,
                pygame.Surface((16, 16), pygame.SRCALPHA),
                (self.current_sprite_groups[i] for i in groups.split(", ")),
                topleft=True,
            )
            sprite.physics_data = physics.PhysicsData(
                physics.TYPE_STATIC, self.current_sprite_groups["collision"]
            )
            sprite.mask = mask

    def create_sprite(self, obj, sprite_group):
        if obj.type is None:
            groups = obj.properties.get("groups", ", ".join(self.default_groups)).split(
                ", "
            )
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
        groups = [
            self.current_sprite_groups[key]
            for key in self.sprite_groups.get(obj.type, self.default_groups)
        ]
        print(groups)
        self.sprite_classes[obj.type](
            pos=obj.pos,
            layer=obj.layer * 3 + 1,
            groups=(
                sprite_group,
                *groups,
            ),
            id=obj.name,
            surface=obj.image,
            topleft=True,
            engine=self.engine,
            **obj.properties,
            **{
                f"{key}_group": value
                for key, value in self.current_sprite_groups.items()
            },
        )

    def load_map(self, tmx_path, engine, player_pos):
        self.current_player = player.Player(
            player_pos,
            4,
            environment.EnvironmentHandler(self.current_env_masks),
            engine,
        )
        try:
            self.current_sprite_groups, properties = self.aux_cache[tmx_path]
            sprite_group = self.current_sprite_groups["main"]
        except KeyError:
            tmx_map = self.loader.load(tmx_path)
            map_size = pygame.Vector2(
                tmx_map.width * tmx_map.tilewidth, tmx_map.height * tmx_map.tileheight
            )
            self.current_sprite_groups = {
                key: value(map_size) for key, value in self.group_creators.items()
            }
            self.current_env_masks = {
                key: pygame.Mask(
                    (
                        tmx_map.tilewidth * tmx_map.width,
                        tmx_map.tileheight * tmx_map.height,
                    )
                )
                for key in environment.TERRAIN_ORDER
            }
            for key in environment.TERRAIN_ORDER:
                self.current_env_masks[key] = pygame.Mask(
                    (
                        tmx_map.tilewidth * tmx_map.width,
                        tmx_map.tileheight * tmx_map.height,
                    )
                )
            sprite_group, properties, cached = super().load(tmx_path)
        script = properties.get("script", None)
        player_layer = properties.get("player_layer", 0) or self.default_player_layer
        for key in self.player_groups:
            self.current_sprite_groups[key].add(self.current_player)
        self.current_player.change_layer(player_layer)
        self.current_player.change_collision_group(
            self.current_sprite_groups["collision"]
        )
        self.current_sprite_groups["main"].follow = self.current_player
        self.current_sprite_groups["main"].add(sprite_group)
        physics.optimize_for_physics(self.current_sprite_groups["collision"])
        groups = self.current_sprite_groups
        self.current_sprite_groups = None
        self.current_env_masks = None
        self.current_player = None
        self.aux_cache[tmx_path] = groups, properties
        return groups, properties.get("script", None)
