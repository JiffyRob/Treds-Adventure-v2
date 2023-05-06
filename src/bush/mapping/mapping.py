from collections import namedtuple
from itertools import chain

import pygame

import pytmx
from bush import animation, asset_handler, entity, util

TYPE_TILE = "tile"
TYPE_OBJECT = "object"
TYPE_IMAGE = "image"
LAYERTYPE_TILE = "tile layer"
LAYERTYPE_IMAGE = "image layer"
LAYERTYPE_OBJECT = "object layer"
Layer = namedtuple(
    "Layer",
    ["layer", "pos", "image", "properties", "type", "name", "size", "items"],
    defaults=[
        0,
        pygame.Vector2(),
        pygame.Surface((0, 0)),
        {},
        None,
        None,
        pygame.Vector2(),
        [],
    ],
)
Tile = namedtuple(
    "Tile",
    ["layer", "pos", "image", "properties", "type"],
    defaults=[0, pygame.Vector2(), pygame.Surface((0, 0)), {}, "tile"],
)
Image = namedtuple(
    "Image",
    ["layer", "pos", "image", "properties", "type", "name"],
    defaults=[0, pygame.Vector2(), pygame.Surface((0, 0)), {}, None, None],
)
Object = namedtuple(
    "Object",
    ["layer", "pos", "image", "properties", "type", "name", "width", "height"],
    defaults=[0, pygame.Vector2(), pygame.Surface((0, 0)), {}, None, None, 0, 0],
)


class MapLoader:
    def __init__(
        self,
        base_dir,
        cache_maps=True,
        cache_files=True,
        sprite_creator=lambda obj, sprite_group: entity.Entity(
            obj.pos,
            obj.image,
            groups=[sprite_group],
            id=obj.name,
            layer=obj.layer * 3 + 1,
            topleft=True,
        ),
        tile_handler=lambda tile, sprite_group: None,
        colorkey=(255, 255, 0),
    ):
        self.loader = asset_handler.AssetHandler(base_dir)
        self.cache = {}
        self.cache_maps = cache_maps
        self.cache_files = cache_files
        self.sprite_creator = sprite_creator
        self.tile_handler = tile_handler
        self.colorkey = colorkey

    def parse(self, map):
        def get_anim(tmx_map, gid):
            props = tmx_map.get_tile_properties_by_gid(gid)
            anim = tmx_map.get_tile_image_by_gid(gid)
            if props is not None and props["frames"]:
                frames = []
                durations = []
                for frame in props["frames"]:
                    frames.append(tmx_map.get_tile_image_by_gid(frame.gid))
                    durations.append(frame.duration)
                anim = animation.Animation(frames, durations)
            return anim

        def tile_generator(tmx_map, layer_index):
            layer = tmx_map.layers[layer_index]
            for x, y, gid in layer.iter_data():
                yield Tile(
                    layer_index,
                    pygame.Vector2(x * map.tilewidth, y * map.tilewidth),
                    get_anim(tmx_map, gid),
                    map.get_tile_properties_by_gid(gid) or {},
                )

        def image_generator(tmx_map, layer_index):
            layer = tmx_map.layers[layer_index]
            yield Image(
                layer_index,
                image=layer.image,
                properties=layer.properties,
                name=layer.name,
            )

        def object_generator(tmx_map, layer_index):
            layer = tmx_map.layers[layer_index]
            for obj in layer:
                if obj.gid:
                    yield Object(
                        layer_index,
                        pygame.Vector2(obj.x, obj.y + obj.height),
                        get_anim(tmx_map, obj.gid),
                        obj.properties,
                        obj.type,
                        obj.name,
                        obj.width,
                        obj.height,
                    )
                    continue
                yield Object(
                    layer_index,
                    pygame.Vector2(obj.x, obj.y),
                    properties=obj.properties,
                    type=obj.type,
                    name=obj.name,
                    width=obj.width,
                    height=obj.height,
                )

        if isinstance(map, str):
            map: pytmx.TiledMap = self.loader.load(map, self.cache_files)
        map_size = pygame.Vector2(
            map.tilewidth * map.width, map.tileheight * map.height
        )
        type_dict = {
            pytmx.TiledTileLayer: LAYERTYPE_TILE,
            pytmx.TiledImageLayer: LAYERTYPE_IMAGE,
            pytmx.TiledObjectGroup: LAYERTYPE_OBJECT,
        }
        parser_dict = {
            pytmx.TiledTileLayer: tile_generator,
            pytmx.TiledImageLayer: image_generator,
            pytmx.TiledObjectGroup: object_generator,
        }
        for index, layer in enumerate(map.layers):
            layer_type = type(layer)
            yield Layer(
                index,
                properties=layer.properties,
                type=type_dict[layer_type],
                items=parser_dict[layer_type](map, index),
                name=layer.name,
                size=map_size.copy(),
            )

    def load(
        self,
        map,
    ):
        if not isinstance(map, pytmx.TiledMap):
            map = self.loader.load(map, self.cache_files)
        filepath = map.filename
        if filepath in self.cache:
            return self.cache[filepath]

        layers = self.parse(map)
        sprite_group = pygame.sprite.Group()
        for layer in layers:
            if layer.type == LAYERTYPE_TILE:
                surface = pygame.Surface(layer.size).convert()
                surface.fill(self.colorkey)
                surface.set_colorkey(self.colorkey)
                for tile in layer.items:
                    self.tile_handler(tile, sprite_group)
                    try:
                        surface.blit(tile.image, tile.pos)
                    except TypeError:
                        sprite_group.add(
                            entity.Entity(
                                tile.pos,
                                tile.image,
                                layer=layer.layer * 3 + 1,
                                topleft=True,
                            )
                        )

                sprite = entity.Entity(
                    (0, 0), surface, layer=layer.layer * 3 + 1, topleft=True
                )
                sprite_group.add(sprite)
            if layer.type == LAYERTYPE_IMAGE:
                sprite_group.add(
                    entity.Entity(
                        (0, 0), layer.image, layer=layer.layer * 3 + 1, id=layer.name
                    )
                )
            if layer.type == LAYERTYPE_OBJECT:
                for obj in layer.items:
                    self.sprite_creator(obj, sprite_group)
        if self.cache_maps:
            self.cache[filepath] = (sprite_group, map.properties, True)
        return sprite_group, map.properties, False

    def clear_cache(self):
        self.cache.clear()
