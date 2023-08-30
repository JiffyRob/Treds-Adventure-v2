import pygame

import globals
import sky
import snek
from bush import asset_handler, util

loader = asset_handler.AssetHandler("scripts")


class Dialog(snek.SnekCommand):
    def __init__(self, prompt, *answers):
        globals.engine.dialog(prompt, answers, on_finish=self.finish)
        self.value = snek.UNFINISHED

    def get_value(self):
        return self.value

    def finish(self, answer):
        print(answer)
        self.value = answer


class Script:
    def __init__(self, this, registry, script):
        self.registry = registry
        const = sky.WeatherCycle
        namespace = {
            "THIS": this,  # will be an entity id or a whatever the script is run on
            "WEATHER_DNCYCLE": const.WEATHERTYPE_DNCYCLE,
            "WEATHER_RAINY": const.WEATHERTYPE_RAINY,
            "WEATHER_SNOWING": const.WEATHERTYPE_SNOWING,
            "WEATHER_FOGGY": const.WEATHERTYPE_FOGGY,
            "WEATHER_DARK": const.WEATHERTYPE_DARK,
            "WEATHER_THUNDER": const.WEATHERTYPE_THUNDER,
        }
        api = {  # TODO: add a lot to this!
            # game environment
            "weatherset": snek.snek_command(globals.engine.sky.set_weather),
            "give": snek.snek_command(globals.player.get),
            "take": snek.snek_command(globals.player.lose),
            "dialog": Dialog,
            "trackset": lambda track: None,  # TODO
            "get": snek.snek_command(globals.engine.state.get),
            "set": snek.snek_command(globals.engine.state.set),
            # vector operation
            "vec": snek.snek_command(lambda *args: pygame.Vector2(*args)),
            "norm": snek.snek_command(lambda vec: vec.copy() or vec.normalize()),
            "randinrect": snek.snek_command(util.randinrect),
            "randincircle": snek.snek_command(util.randincircle),
            "direc": snek.snek_command(util.direction),
            # sprite operation
            "move": self.move,
            "immobilize": self.immobilize,
            "mobilize": self.mobilize,
            "face": self.face,
            "get_velocity": snek.snek_command(
                lambda sprite_id: self.get_sprite(sprite_id).velocity
            ),
        }
        self.program = snek.SNEKProgram(loader.load(script), namespace, api)

    def get_sprite(self, sprite_id):
        return self.registry.get_group("scriptable").get_by_id(sprite_id)

    @snek.snek_command
    def move(self, sprite_id, veloc):
        self.get_sprite(sprite_id).desired_velocity = veloc

    @snek.snek_command
    def immobilize(self, sprite_id):
        self.get_sprite(sprite_id).immobilize()

    @snek.snek_command
    def mobilize(self, sprite_id):
        self.get_sprite(sprite_id).mobilize()

    @snek.snek_command
    def face(self, sprite_id, direction):
        self.get_sprite(sprite_id).face(direction)

    def update(self, dt):
        self.program.cycle()

    def finished(self):
        return not self.program.running
