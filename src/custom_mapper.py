import pygame

import environment
import globals
from bush import asset_handler, entity, physics
from bush.mapping import group, mapping, registry
from game_objects import npc, plant, player, teleport


class MapLoader(mapping.MapLoader):
    def __init__(self):
        self.collision_group = pygame.sprite.Group()
        self.group_creators = {
            "main": lambda map_size: group.TopDownGroup(
                globals.engine.screen_size,
                map_size,
                (0, 0),
                self.get_player(),
                debug_physics=True,
            ),
            "player": lambda x: pygame.sprite.GroupSingle(),
            "collision": lambda x: pygame.sprite.Group(),
            "event": lambda x: group.EntityGroup(),
            "interactable": lambda x: pygame.sprite.Group(),
            "farmplants_green": lambda x: pygame.sprite.Group(),
            "farmplants_orange": lambda x: pygame.sprite.Group(),
            "farmplants": lambda x: pygame.sprite.Group(),
            "throwable": lambda x: pygame.sprite.Group(),
        }
        self.registry = None
        self.current_player = None
        self.sprite_classes = {
            "teleport": teleport.Teleport,
            "npc-static": npc.StaticNPC,
            "npc-dynamic": npc.DynamicNPC,
            "throwable": plant.Throwable,
        }
        self.sprite_groups = {
            "teleport": (
                "main",
                "collision",
            ),
            "npc-static": (
                "main",
                "collision",
                "event",
                "interactable",
            ),
            "npc-dynamic": (
                "main",
                "collision",
                "event",
                "interactable",
            ),
            "throwable": (
                "main",
                "throwable",
            ),
        }
        self.player_groups = ("main", "player")
        self.default_groups = ("main",)
        self.default_player_layer = 4  # second layer (default sub)
        loader = asset_handler.glob_loader
        self.mask_loader = asset_handler.AssetHandler(
            asset_handler.join(loader.base, "masks")
        )
        self.mask_loader.cache_asset_handler(asset_handler.glob_loader)
        self.aux_cache = {}
        super().__init__(
            asset_handler.join(loader.base, "tiled/maps"),
            sprite_creator=self.create_sprite,
            tile_handler=self.handle_tile,
        )

    def get_player(self):
        return self.current_player

    def handle_tile(self, tile, sprite_group):
        terrain = tile.properties.get("terrain", None)
        mask = tile.properties.get("mask", None) or pygame.mask.from_surface(tile.image)
        if terrain:
            self.registry.get_mask(terrain).draw(mask, tile.pos)
        groups = tile.properties.get("groups", None)
        if groups:
            sprite = entity.Entity(
                tile.pos,
                pygame.Surface((16, 16), pygame.SRCALPHA),
                [self.registry.get_group(i) for i in self.default_groups],
            )
            sprite.physics_data = physics.PhysicsData(
                physics.TYPE_STATIC, self.registry.get_group("collision")
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
                groups=(*[self.registry.get_group(key) for key in groups],),
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
                    physics.TYPE_STATIC, self.registry.get_group("collision")
                )
                sprite.mask = mask
            return
        groups = [
            self.registry.get_group(key)
            for key in self.sprite_groups.get(obj.type, self.default_groups)
        ]
        obj.properties.pop("width", None)
        obj.properties.pop("height", None)
        if obj.name is not None:
            obj.properties["id"] = obj.name
        self.sprite_classes[obj.type](
            pos=obj.pos,
            layer=obj.layer * 3 + 1,
            groups=(
                sprite_group,
                *groups,
            ),
            surface=obj.image,
            topleft=True,
            width=obj.width,
            height=obj.height,
            registry=self.registry,
            **obj.properties,
        )

    def load_map(self, tmx_path, player_pos):
        try:
            self.registry, properties = self.aux_cache[tmx_path]
            sprite_group = self.registry.get_group("main")
            self.current_env_masks = {}
            self.registry.get_group("player").sprite.kill()
        except KeyError:
            tmx_map = self.loader.load(tmx_path)
            map_size = pygame.Vector2(
                tmx_map.width * tmx_map.tilewidth, tmx_map.height * tmx_map.tileheight
            )
            self.registry = registry.MapRegistry()
            for key, value in self.group_creators.items():
                self.registry.add_group(key, value(map_size))
            for key in environment.TERRAIN_ORDER:
                self.registry.add_mask(key, pygame.Mask((map_size)))
            sprite_group, properties, cached = super().load(tmx_path)
        self.current_player = player.Player(
            player_pos,
            4,
            self.registry,
        )
        player_layer = properties.get("player_layer", 0) or self.default_player_layer
        for key in self.player_groups:
            self.registry.get_group(key).add(self.current_player)
        self.current_player.change_layer(player_layer)
        self.current_player.change_collision_group(self.registry.get_group("collision"))
        self.registry.get_group("main").follow = self.current_player
        self.registry.get_group("main").add(sprite_group)
        physics.optimize_for_physics(self.registry.get_group("collision"))
        groups = self.registry
        self.registry = None
        self.current_player = None
        self.aux_cache[tmx_path] = groups, properties
        return groups, properties.get("track", None), properties.get("script", None)
