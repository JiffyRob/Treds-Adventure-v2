from bush import entity, color, util, physics


class Block(entity.Entity):
    def __init__(self, pos, groups, body_group):
        surface = util.rect_surf((0, 0, 32, 32), color.BLUE)
        super().__init__(surface, pos, groups)
        self.body = physics.Body(pos, 10, physics.Rect(32, 32, (0, 0)), body_group)
        self.physics_update = lambda dt: physics.entity_update(self, dt)
