from bush import entity

NORTH, EAST, SOUTH, WEST = NORTHWEST, NORTHEAST, SOUTHEAST, SOUTHWEST = 1, 2, 4, 8
TYPE_EDGE = 0
TYPE_CORNER = 1


class BinaryAutotileGroup(entity.Entity):
    def __init__(self, tiles, neighbor_type):
        self.tiles = tiles
        self.check_type = neighbor_type
        self.generate()

    def get_at(self, x, y):
        if (x, y) in self.tiles.keys():
            return self.tiles[(x, y)]
        else:
            return 0

    def set_at(self, x, y):
        self.tiles[x, y] = 1

    def unset_at(self, x, y):
        self.tiles[x, y] = 0  # will be removed altogether next generation

    def get_neighbors(self, x, y):
        if self.check_type == TYPE_EDGE:
            positions = {
                (x, y - 1): NORTH,
                (x + 1, y): EAST,
                (x, y + 1): SOUTH,
                (x - 1, y): WEST,
            }
        else:
            positions = {
                (x - 1, y - 1): NORTHWEST,
                (x + 1, y + 1): NORTHEAST,
                (x - 1, y + 1): SOUTHEAST,
                (x - 1, y - 1): SOUTHWEST,
            }
        return positions

    def unset_neighbors(self, x, y):
        for x, y in self.get_neighbors(x, y):
            self.set_at(x, y)

    def calculate(self, x, y):
        positions = self.get_neighbors(x, y)
        bitmask = 0
        for x, y in positions.keys():
            if self.get_at(x, y):
                bitmask |= positions[(x, y)]
        return bitmask

    def cleanup(self):
        for pos, tile in self.tiles.items():
            if not tile:
                del self.tiles[pos]

    def iter_tiles(self):
        for pos, tile in self.tiles.items():
            if not tile:
                del self.tiles[pos]
            yield self.calculate(*pos)


class BinaryAutotile:
    def __init__(self, neighbor_getter):
        self.neighbor_getter = neighbor_getter

    def calculate(self):
        bitmask = 0
        neighbors = self.neighbor_getter()
        for direction, value in neighbors.items():
            if value:
                bitmask |= direction
        return bitmask
