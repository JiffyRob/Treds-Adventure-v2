"""
level
 - basic mapping primitives
"""
import pygame

DUPLICATE_REMOVE = 1
DUPLICATE_OVERWRITE = 2
DUPLICATE_VALUE_ERROR = 3


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

    def add_internal(self, sprite):
        sprite_id = sprite.get_id()
        if sprite_id in self.ids:
            self.on_duplicate(sprite, self.ids[sprite_id], self)
        self.ids[sprite_id] = sprite
        super().add_internal(sprite)

    def remove(self, *sprites):
        super().remove(*sprites)
        for spr in sprites:
            if spr.__dict__.get("_id", None) is not None:
                self.ids.pop(spr._id)

    def get_by_id(self, id):
        return self.ids.get(id, None)


class CameraGroup(pygame.sprite.LayeredUpdates):
    def __init__(
        self,
        cam_size,
        map_size,
        pos,
        follow=None,
        only_upate_visible_sprites=True,
        border_overshoot=0,
        debug_physics=False,
        *sprites
    ):
        super().__init__(*sprites)
        self.cam_rect = pygame.Rect(0, 0, *cam_size)
        self.map_rect = pygame.Rect(0, 0, *map_size)
        self.cam_rect.center = pos
        self.follow = follow
        self.update_all = not only_upate_visible_sprites
        self.border_overshoot = border_overshoot
        self.visible_rect = self.cam_rect.inflate(
            self.border_overshoot * 2, self.border_overshoot * 2
        )
        self.debug_physics = debug_physics

    def is_visible(self, sprite):
        if sprite in self:
            return sprite.rect.colliderect(self.visible_rect) or (
                sprite.rect.size == (0, 0)
                and self.visible_rect.collidepoint(sprite.rect.topleft)
            )
        return False

    def update(self, *args, **kwargs):
        self.visible_rect = self.cam_rect.inflate(
            self.border_overshoot * 2, self.border_overshoot * 2
        )
        if self.update_all:
            return super().update(*args, **kwargs)
        updated = []
        for sprite in self.sprites():
            if self.is_visible(sprite):
                sprite.update(*args, **kwargs)
                updated.append(sprite)
        return updated

    def draw(self, surface, offset=(0, 0)):
        self.visible_rect = self.cam_rect.inflate(
            self.border_overshoot * 2, self.border_overshoot * 2
        )
        if self.follow is not None:
            self.cam_rect.center = self.follow.pos
            self.limit()
            self.limit_sprites()
        offset = pygame.Vector2(self.cam_rect.topleft) - offset
        for sprite in self.sprites():
            if self.is_visible(sprite) or self.update_all:
                pos = pygame.Vector2(sprite.rect.topleft) - offset
                surface.blit(sprite.image, pos)
        if self.debug_physics:
            for sprite in self.sprites():
                if not sprite.no_debug and (self.is_visible(sprite) or self.update_all):
                    pygame.draw.rect(surface, (0, 255, 0), sprite.rect.move(-offset), 1)
                    if hasattr(sprite, "collision_rect"):
                        pygame.draw.rect(
                            surface, (0, 0, 255), sprite.collision_rect.move(-offset), 1
                        )

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

    def cam_rect_centered(self, center):
        new_rect = self.cam_rect.copy()
        self.cam_rect.center = center
        self.limit()
        return_rect = self.cam_rect
        self.cam_rect = new_rect
        return return_rect


class TopDownGroup(CameraGroup):
    def sprites(self):
        def sortkey(sprite):
            return (sprite.layer * 1000) + sprite.rect.bottom

        return sorted(super().sprites(), key=sortkey)
