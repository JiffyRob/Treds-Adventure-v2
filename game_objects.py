from bush import entity, color, util


class Block(entity.Entity):
    def __init__(self, pos, groups):
        surface = util.rect_surf((0, 0, 32, 32), color.BLUE)
        super().__init__(surface, pos, groups)
