"""
level
 - basic mapping primitives
"""
import pygame

DUPLICATE_REMOVE = 1
DUPLICATE_OVERWRITE = 2
DUPLICATE_VALUE_ERROR = 3

try:
    import pytmx
except ImportError:
    pytmx = NotImplemented
    print("WARNING: pytmx not found.  Tiled map primitives not available")
from bush import animation, color, entity, physics


class EntityGroup(pygame.sprite.Group):
    def __init__(
        self,
        *sprites,
        on_duplicate=lambda old_sprite, new_sprite, group: group.remove(old_sprite)
    ):
        super().__init__()
        self.ids = {}
        self.on_duplicate = on_duplicate
        self.add(*sprites)

    def add(self, *sprites, on_duplicate=None):
        for spr in sprites:
            if spr.__dict__.get("_id", None) is not None:
                spr_id = spr._id
                if spr_id in self.ids:
                    self.on_duplicate(spr, self.ids[spr_id], self)
                self.ids[spr_id] = spr
        super().add(*sprites)

    def remove(self, *sprites):
        super().remove(*sprites)
        for spr in sprites:
            if spr.__dict__.get("_id", None) is not None:
                self.ids.pop(spr._id)


class CameraGroup(pygame.sprite.LayeredUpdates):
    def __init__(self, cam_size, map_size, pos, follow=None, *sprites):
        super().__init__(*sprites)
        self.cam_rect = pygame.Rect(0, 0, *cam_size)
        self.map_rect = pygame.Rect(0, 0, *map_size)
        self.cam_rect.center = pos
        self.follow = follow

    def draw(self, surface):
        if self.follow is not None:
            self.cam_rect.center = self.follow.pos
            self.limit()
            self.limit_sprites()
        offset = pygame.Vector2(self.cam_rect.topleft)
        for sprite in self.sprites():
            pos = pygame.Vector2(sprite.rect.topleft) - offset
            surface.blit(sprite.image, pos)

    def limit(self):
        if self.cam_rect.height < self.map_rect.height:
            self.cam_rect.top = max(self.cam_rect.top, self.map_rect.top)
            self.cam_rect.bottom = min(self.cam_rect.bottom, self.map_rect.bottom)
        else:
            self.cam_rect.centery = self.map_rect.centery

        if self.cam_rect.width < self.map_rect.width:
            self.cam_rect.left = max(self.cam_rect.left, self.map_rect.left)
            self.cam_rect.right = min(self.cam_rect.right, self.map_rect.right)
        else:
            self.cam_rect.centerx = self.map_rect.centerx

    def limit_sprites(self):
        for sprite in self.sprites():
            sprite.limit(self.map_rect)


class TopDownGroup(CameraGroup):
    def sprites(self):
        def sortkey(sprite):
            return (sprite.layer * 1000) + sprite.rect.bottom

        return sorted(super().sprites(), key=sortkey)


class AnimatedTile(entity.EntityLite):
    def __init__(self, anim, pos, layer):
        super().__init__(anim.image(), pos)
        self._layer = layer
        self.anim = anim

    def update(self, dt):
        super().update()
        self.image = self.anim.image()


def generate_map_sprites(
    pytmx_map,
    cam_size,
    cam_pos=(0, 0),
    entity_generator=lambda obj, layer, layer_ind: None,
    tile_layer_callback=lambda obj, layer, layer_ind: None,
    image_layer_callback=lambda layer, layer_ind: None,
    top_down=False,
):
    # basic map data
    tile_size = pygame.Vector2(pytmx_map.tilewidth, pytmx_map.tileheight)
    map_size = pygame.Vector2(
        pytmx_map.width * tile_size.x, pytmx_map.height * tile_size.y
    )
    # sprite group
    if top_down:
        sprite_group = TopDownGroup(cam_size, map_size, cam_pos)
    else:
        sprite_group = CameraGroup(cam_size, map_size, cam_pos)
    # animation
    anim_gids = {}
    for gid, props in pytmx_map.tile_properties.items():
        frames = []
        lengths = []
        for frame_gid, length in props["frames"]:
            frames.append(pytmx_map.get_tile_image_by_gid(frame_gid))
            lengths.append(length)
        if frames:
            anim_gids[gid] = animation.Animation(frames, lengths)

    for layer_ind, layer in enumerate(pytmx_map.visible_layers()):
        if isinstance(layer, pytmx.TiledTileLayer):
            surface = pygame.Surface(map_size).convert()
            surface.fill(color.MAGENTA)
            surface.set_colorkey(color.MAGENTA)
            for x, y, gid in layer.iter_data():
                pos = tile_size.elementwise() * (x, y)
                if gid in anim_gids:
                    anim_tile = AnimatedTile(
                        anim_gids[gid], pos + tile_size / 2, layer_ind + 0.01
                    )
                    sprite_group.add(anim_tile)
                else:
                    surface.blit(pytmx_map.get_tile_image_by_gid(gid), pos)
            sprite = entity.EntityLite(surface, (0, 0))
            sprite.layer = layer_ind
            sprite_group.add(sprite)
            tile_layer_callback(layer, layer_ind)
        elif isinstance(layer, pytmx.TiledObjectGroup):
            for obj in layer:
                sprite = entity_generator(obj, layer, layer_ind)
                if sprite is None:
                    continue
                sprite_group.add(sprite)
        elif isinstance(layer, pytmx.TiledImageLayer):
            sprite = entity.EntityLite(layer.image, layer.image.get_rect().center)
            sprite._layer = layer_ind
            sprite_group.add(sprite)
            image_layer_callback(layer, layer_ind)
        else:
            raise TypeError("AAAAHHHHHH!!!!  The world exploded!")
    return sprite_group
