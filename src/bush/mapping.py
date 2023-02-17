import pygame
import pytmx

from bush import animation, asset_handler, entity, physics

PRERENDER_NONE = 0
PRERENDER_NORMAL = 1
PRERENDER_DOUBLEDRAW = 2


class MapLoader:
    def __init__(
        self,
        sprite_creators,
        sprite_group_creators,
        sprite_kwargs,
        sprite_group_key_function=lambda sprite, is_nonsprite: ("main",),
        colorkey=(255, 255, 0),
        mask_load_path=".",
        map_load_path=".",
        after_load_callback=lambda sprite_groups, map_properties: None,
        prerender_mode=PRERENDER_NORMAL,
    ):
        self.sprite_creators = sprite_creators
        self.sprite_group_creators = sprite_group_creators
        self.sprite_kwargs = sprite_kwargs
        self.colorkey = colorkey
        self.sprite_groups_of = sprite_group_key_function
        self.mask_loader = asset_handler.AssetHandler(mask_load_path)
        self.map_loader = asset_handler.AssetHandler(map_load_path)
        self.after_load_callback = after_load_callback
        self.prerender_mode = prerender_mode

    def load_map(self, tmx_path, prerender_mode=PRERENDER_NORMAL):
        """Take a pytmx map path (or TiledMap) and return a series of sprite groups, to be rendered in order"""

        def get_anim():
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

        def add_to_groups(sprite, is_nonsprite):
            for key in self.sprite_groups_of(sprite, is_nonsprite):
                sprite_groups[key].add(sprite)

        def add_to_masks(pos, mask, groups):
            for key in groups:
                masks[key].draw(mask, pos)

        def static_sprite(pos, gid):
            anim = get_anim()
            if isinstance(anim, animation.Animation):
                sprite = entity.Entity(pos, anim, layer=sprite_layer, topleft=True)
                add_to_groups(sprite, True)
            else:
                surface.blit(anim, pos)

        if isinstance(tmx_path, pytmx.TiledMap):
            tmx_map = tmx_path
        else:
            tmx_map = self.map_loader.load(tmx_path)

        map_size = pygame.Vector2(
            tmx_map.width * tmx_map.tilewidth, tmx_map.height * tmx_map.tileheight
        )
        tile_size = pygame.Vector2(tmx_map.tilewidth, tmx_map.tileheight)
        sprite_groups = {
            key: callback(map_size)
            for key, callback in self.sprite_group_creators.items()
        }
        masks = {key: pygame.mask.Mask(map_size) for key in sprite_groups.keys()}
        for index, layer in enumerate(tmx_map.layers):
            sprite_layer = index * 3 + 1  # 3 sub layers per layer
            if isinstance(layer, pytmx.TiledImageLayer):
                sprite = entity.Entity((0, 0), layer.image, layer=sprite_layer)
                add_to_groups(sprite, True)
                continue
            if isinstance(layer, pytmx.TiledTileLayer):
                surface = pygame.Surface(map_size)
                surface.fill(self.colorkey)
                surface.set_colorkey(self.colorkey)
                for x, y, gid in layer.iter_data():
                    if not gid:
                        continue
                    props = tmx_map.get_tile_properties_by_gid(gid) or {}
                    tile_pos = tile_size.elementwise() * (x, y)
                    tile_mask = pygame.mask.from_surface(
                        tmx_map.get_tile_image_by_gid(gid)
                    )
                    if props.get("groups", False):
                        add_to_masks(tile_pos, tile_mask, props["groups"].split(", "))
                    static_sprite(tile_pos, gid)
                sprite = entity.Entity(
                    (0, 0), surface, layer=sprite_layer, topleft=True
                )
                add_to_groups(sprite, True)
                continue
            if isinstance(layer, pytmx.TiledObjectGroup):
                for obj in layer:
                    obj.y += (
                        obj.height
                    )  # I don't know why, but objects are always up on height unit
                    gid = obj.gid
                    anim = pygame.Surface((obj.width, obj.height)).convert()
                    anim.set_colorkey(self.colorkey)
                    anim.fill(self.colorkey)
                    if obj.type is None:
                        if gid:
                            static_sprite((obj.x, obj.y), gid)
                            props = obj.properties
                            if obj.properties.get("groups", False):
                                if "mask" in props:
                                    mask = pygame.mask.from_surface(
                                        self.mask_loader.load(props["mask"])
                                    )
                                else:
                                    mask = pygame.mask.from_surface(obj.image)
                                add_to_masks(
                                    pygame.Vector2(obj.x, obj.y),
                                    mask,
                                    props["groups"].split(", "),
                                )
                        else:
                            print(
                                f"Object with no image or type ignored at ({obj.x}, {obj.y}) on layer '{layer.name}'"
                            )
                        continue
                    if gid:
                        anim = get_anim()
                    sprite = self.sprite_creators[obj.type](
                        pygame.Vector2(obj.x, obj.y),
                        anim,
                        layer=sprite_layer,
                        topleft=True,
                        **obj.properties,
                        **{
                            key + "_group": value
                            for key, value in sprite_groups.items()
                        },
                        **self.sprite_kwargs,
                    )
                    add_to_groups(sprite, False)
        for key, mask in masks.items():
            sprite = entity.Entity((0, 0), groups=(sprite_groups[key],))
            sprite.physics_data = physics.PhysicsData(
                physics.TYPE_STATIC, sprite_groups[key]
            )
            sprite.mask = mask
        self.after_load_callback(sprite_groups, tmx_map.properties)
        return sprite_groups, tmx_map.properties
