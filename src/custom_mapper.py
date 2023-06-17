import pygame

import environment
import globals
from bush import asset_handler, entity, physics
from bush.mapping import group, mapping, registry
from game_objects import npc, plant, teleport
from game_objects.enemies import slime


class MapLoader(mapping.MapLoader):
    def __init__(self):
        self.sprite_classes = {
            "teleport": teleport.Teleport,
            "npc-static": npc.StaticNPC,
            "npc-dynamic": npc.DynamicNPC,
            "throwable": plant.Throwable,
            "slime": slime.Slime,
        }
        self.default_player_layer = 4  # second layer (default sub)
        loader = asset_handler.glob_loader
        self.mask_loader = asset_handler.AssetHandler(
            asset_handler.join(loader.base, "masks")
        )
        self.mask_loader.cache_asset_handler(asset_handler.glob_loader)
        self.aux_cache = {}
        self.map_size = None
        super().__init__(
            asset_handler.join(loader.base, "tiled/maps"),
            sprite_creator=self.create_sprite,
            tile_handler=self.handle_tile,
            registry_creators={
                "main": lambda map_size: group.TopDownGroup(
                    globals.engine.screen_size,
                    map_size,
                    (0, 0),
                    globals.player,
                    debug_physics=False,
                ),
                "player": lambda x: pygame.sprite.GroupSingle(),
                "collision": lambda x: pygame.sprite.Group(),
                "event": lambda x: group.EntityGroup(),
                "interactable": lambda x: pygame.sprite.Group(),
                "attackable": lambda x: pygame.sprite.Group(),
                "farmplants_green": lambda x: pygame.sprite.Group(),
                "farmplants_orange": lambda x: pygame.sprite.Group(),
                "farmplants": lambda x: pygame.sprite.Group(),
            },
        )

    def handle_tile(self, tile, sprite_group):
        terrain = tile.properties.get("terrain", None)
        mask = tile.properties.get("mask", None) or pygame.mask.from_surface(tile.image)
        if terrain:
            if terrain not in self.current_registry.list_masks():
                self.current_registry.add_mask(terrain, pygame.Mask(self.map_size))
            self.current_registry.get_mask(terrain).draw(mask, tile.pos)
        groups = tile.properties.get("groups", "main").split(", ")
        if groups:
            sprite_groups = [
                self.current_registry.get_group(group_key) for group_key in groups
            ]
            sprite = entity.Entity(
                tile.pos,
                pygame.Surface((16, 16), pygame.SRCALPHA),
                [self.current_registry.get_group(group_key) for group_key in groups],
                topleft=True,
                no_debug=True,
            )
            if "collision" in groups:
                sprite.physics_data = physics.PhysicsData(
                    physics.TYPE_STATIC, self.current_registry.get_group("collision")
                )
                sprite.mask = mask

    def create_sprite(self, obj, sprite_group):
        if obj.type is None:
            groups = obj.properties.get("groups", "main").split(", ")
            sprite = entity.Entity(
                pos=obj.pos,
                layer=obj.layer * 3 + 1,
                groups=(*[self.current_registry.get_group(key) for key in groups],),
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
                    physics.TYPE_STATIC, self.current_registry.get_group("collision")
                )
                sprite.mask = mask
            return
        obj.properties.pop("width", None)
        obj.properties.pop("height", None)
        if obj.name is not None:
            obj.properties["id"] = obj.name
        self.sprite_classes[obj.type](
            pos=obj.pos,
            layer=obj.layer * 3 + 1,
            surface=obj.image,
            topleft=True,
            width=obj.width,
            height=obj.height,
            registry=self.current_registry,
            **obj.properties,
        )

    def load_map(self, tmx_path, player_pos):
        globals.player.kill()
        try:
            self.current_registry, properties = self.aux_cache[tmx_path]
            self.current_env_masks = {}
        except KeyError:
            tmx_map = self.loader.load(tmx_path)
            self.map_size = pygame.Vector2(
                tmx_map.width * tmx_map.tilewidth, tmx_map.height * tmx_map.tileheight
            )
            _, properties, cached = super().load(tmx_path)
        sprite_group = self.current_registry.get_group("main")
        globals.player.reset(
            player_pos.copy(),
            properties.get("player_layer", self.default_player_layer),
            self.current_registry,
        )
        self.current_registry.get_group("main").add(sprite_group)
        physics.optimize_for_physics(self.current_registry.get_group("collision"))
        self.aux_cache[tmx_path] = self.current_registry, properties
        for key in environment.TERRAIN_ORDER:
            if key not in self.current_registry.list_masks():
                self.current_registry.add_mask(key, pygame.Mask(self.map_size))
        return (
            self.current_registry,
            properties.get("track", None),
            properties.get("script", None),
        )

    def clear_cache(self):
        super().clear_cache()
        self.aux_cache.clear()
