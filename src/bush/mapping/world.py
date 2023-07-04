import pygame


class World:
    def __init__(self, world_dict, map_loader=None):
        self.rect_to_map = {}
        self.name_to_map = {}
        self.rect_to_name = {}
        self.name_to_rect = {}
        self.map_loader = map_loader
        for name, data in world_dict.items():
            rect, tmx_map = data
            rect = tuple(rect)
            self.rect_to_map[rect] = tmx_map
            self.name_to_map[name] = tmx_map
            self.rect_to_name[rect] = name
            self.name_to_rect[name] = rect

    def load_map(self, tmx_map):
        if self.map_loader is not None and tmx_map is not None:
            return self.map_loader(tmx_map)
        return tmx_map

    def get_map_by_name(self, name):
        return self.load_map(self.name_to_map.get(name, None))

    def get_map_by_rect(self, rect):
        return self.load_map(self.rect_to_map.get(rect, None))

    def get_name_by_rect(self, rect):
        return self.rect_to_name.get(rect, None)

    def get_rect_by_name(self, name):
        return self.name_to_rect.get(name, None)

    def map_collidepoint(self, point):
        for rect, tmx_map in self.rect_to_map.items():
            if pygame.Rect(rect).collidepoint(point):
                return self.load_map(tmx_map)
        return None

    def name_collidepoint(self, point):
        for rect, name in self.rect_to_name.items():
            if pygame.Rect(rect).collidepoint(point):
                return name
