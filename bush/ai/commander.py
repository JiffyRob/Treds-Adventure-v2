import pygame
from bush import timer, util_load
import lupa
import inspect
import os


class AIGroup(pygame.sprite.AbstractGroup):
    pass


class AI(pygame.sprite.Sprite):
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
        self.sandbox_runtime(self.runtime)

    def sandbox_runtime(self, runtime):
        # remove all functions save those defined in env.lua
        # this should also remove python access
        with util_load.load_text("env.lua") as f:
            runtime.execute(f.read())
        runtime.globals()._G = runtime.globals().env
        # add get_entity() callback to script
        # returns a table of data from the dict from
        runtime.globals().get_entity = self._lua_get_entity
        # add function to load lua modules
        runtime.globals().require = self._require

    def _lua_get_entity(self):
        return self.entity.to_scripting_dict()

    def require(self, modname):
        # scan through working directory for file matching the modname
        for entry in os.path.scandir("."):
            if entry.is_file():
                if entry.name == modname + ".lua":
                    path = entry.path
                    with util_load.load_text(path) as file:
                        script = file.read()
                    runtime = lupa.LuaRuntime()
                    self.sandbox_runtime(runtime)
                    runtime.execute(script)
                    return runtime.globals()

    def run(self):
        self.runtime.execute(self.script)
