import pygame

import scripts
from bush import entity


class GameObject(entity.Actor):
    def __init__(
        self,
        pos,
        engine,
        surface=None,
        anim_dict=None,
        groups=(),
        id=None,
        layer=None,
        topleft=False,
        beginning_state=None,
        entity_group=None,
    ):
        super().__init__(pos, surface, groups, id, layer, topleft)
        self.engine = engine
        self.anim_dict = {}
        if anim_dict is not None:
            self.anim_dict = anim_dict
        if beginning_state is not None:
            self.state = beginning_state
        elif self.anim_dict:
            self.state = next(iter(self.anim_dict.keys()))
        else:
            self.state = None
        self.entity_group = entity_group
        self.pushed_state = None
        self.script_queue = []

    @property
    def player(self):
        return self.engine.player

    def run_script(self, script_name, queue=True):
        for script in self.script_queue:
            script.pause()
        if queue:
            for script in self.script_queue:
                script.pause()
        else:
            for script in self.script_queue:
                script.finish()
            self.script_queue = []
        self.script_queue.append(
            scripts.get_script(script_name, self, self.engine, self.entity_group)
        )
        self.script_queue[-1].begin()

    def update_state(self, dt):
        if self.pushed_state:
            self.state = self.pushed_state

    def update_image(self, dt):
        if self.anim_dict:
            self.anim = self.anim_dict[self.state]

    def update_physics(self, dt):
        self.pos += self.velocity * dt
        self.update_rects()

    def update_script(self, dt):
        if self.script_queue:
            self.script_queue[-1].update(dt)
        if self.script_queue[-1].complete:
            self.script_queue = self.script_queue[:-1]
            self.script_queue[-1].unpause()

    def update_rects(self):
        self.rect.center = self.pos

    def update(self, dt):
        self.update_script(dt)
        self.update_state(dt)
        self.update_physics(dt)
        self.update_image(dt)
        super().update(dt)
