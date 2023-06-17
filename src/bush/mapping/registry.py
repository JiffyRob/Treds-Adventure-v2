import pygame

from bush import collision


class MaskRegistry(dict):
    def __setitem__(self, key, value):
        if not isinstance(value, pygame.Mask):
            raise TypeError("MaskRegistry only accepts pygame.Mask objects")
        super().__setitem__(key, value)

    def collides(self, thing, *keys):
        for key in keys:
            if collision.collides(self[key], thing):
                return key

    def collide_rect(self, rect, *keys):
        for key in keys:
            if collision.collide_rect_mask(rect, self[key]):
                return key

    def collide_mask(self, mask, offset, *keys):
        for key in keys:
            if self[key].overlap(mask, offset):
                return key


class RectListRegistry(dict):
    def __setitem__(self, key, value):
        if not isinstance(value, (list, tuple, set)):
            raise TypeError("RectListRegistry only takes sequences")
        super().__setitem__(key, value)

    def collides(self, thing, *keys):
        for key in keys:
            for rect in self[key]:
                if collision.collides(rect, thing):
                    return key

    def collide_rect(self, rect, *keys):
        for key in keys:
            if rect.collidelist(self[key]):
                return key

    def collide_mask(self, mask, offset, *keys):
        for key in keys:
            for rect in self[key]:
                if collision.collide_rect_mask(rect, mask, offset):
                    return key


class GroupRegistry(dict):
    def __setitem__(self, key, value):
        if not isinstance(value, pygame.sprite.AbstractGroup):
            raise TypeError("GroupRegistry only takes pygame sprite groups")
        super().__setitem__(key, value)

    def collides(self, thing, *keys):
        for key in keys:
            for sprite in self[key].sprites():
                if collision.collides(sprite, thing):
                    return key

    def collide_sprite(self, sprite, callback, *keys):
        for key in keys:
            if pygame.sprite.spritecollideany(sprite, self[key], callback):
                return key


class MapRegistry:
    def __init__(self):
        self.groups = GroupRegistry()
        self.masks = MaskRegistry()
        self.rect_lists = RectListRegistry()

    def add_group(self, key, group):
        self.groups[key] = group

    def add_mask(self, key, mask):
        self.masks[key] = mask

    def add_rect_list(self, key, rect_list):
        self.rect_lists[key] = rect_list

    def get_group(self, key, fallback=None):
        return self.groups.get(key, fallback)

    def get_mask(self, key, fallback=None):
        return self.masks.get(key, fallback)

    def get_rect_list(self, key, fallback=None):
        return self.rect_lists.get(key, fallback)

    def list_groups(self):
        return list(self.groups.keys())

    def list_masks(self):
        return list(self.masks.keys())

    def list_rect_lists(self):
        return list(self.rect_lists.keys())
