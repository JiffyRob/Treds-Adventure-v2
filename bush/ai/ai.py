import pygame
from bush import timer, util_load
import lupa
class AIGroup(pygame.sprite.AbstractGroup):
    pass
class AI(pygame.Sprite):
    def __init__(self, entity, run_every=1000):
        self.entity = entity
        self.timer = timer.Timer(run_every, self.run, True)

    def get_entity(self):
        return self.entity


    def update(self, dt):
        self.timer.update()

    def run(self):
        # issue commmands here
        print("ai compute...beep boop")
        self.entity.command("idle")

class LuaAI(AI):
    def __init__(self, entity, script, run_every=1000):
        super().__init__(entity, run_every)
        self.script = util_load.load_text(script)
        self.runtime = lupa.LuaRuntime()
        # The following code is meant to help sandbox the lua runtime
        # Else it could mess with things it shouldn't
        # disallow importing of external modules for security purposes
        self.runtime.execute("require = nil")
        # set attribute access callbacks
        # TODO
        ...
        # possibly compile script and then call?

    def run(self):
        self.runtime.execute(self.script)