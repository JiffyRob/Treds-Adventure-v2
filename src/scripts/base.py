import globals
from bush import sound_manager, util

player = sound_manager.glob_player
STATE_RUNNING = 0
STATE_PAUSED = 1
STATE_FINISHED = 2


class Script:
    def __init__(self, registry):
        self.registry = registry
        self.timer_list = []
        self.sky = globals.engine.sky
        self.talking = False
        self.state = STATE_RUNNING
        self.init()

    def init(self):
        pass

    def update(self, dt):
        if self.state == STATE_RUNNING:
            self.script_update(dt)

    def script_update(self, dt):
        for timer_to_update in self.timer_list:
            timer_to_update.update()
        self.timer_list = [i for i in self.timer_list if i.time_left()]

    def pause(self):
        self.state = STATE_PAUSED

    def unpause(self):
        self.state = STATE_RUNNING

    def finish(self):
        self.state = STATE_FINISHED

    def finished(self):
        return self.state == STATE_FINISHED

    def get_entity(self, name):
        self.registry.get_group("event").get_by_id(name)

    def get_time(self):
        return ("night", "day")[self.sky.is_day()]

    def add_timer(self, new_timer):
        self.timer_list.append(new_timer)

    def clear_timers(self):
        self.timer_list = []

    def say(self, text, on_finish=lambda interrupted: None):
        globals.engine.dialog(text, (), on_finish)

    def ask(self, question, answers, on_finish=lambda interrupted, answer: None):
        globals.engine.dialog(question, answers, on_finish)

    def play_sound(self, sound_name):
        player.play(sound_name)

    def spawn_particles(self, particles):
        globals.engine.stack.get_current().add_particles(particles)

    def give_player(self, *things):
        for thing in things:
            globals.player.get(thing)

    def take_from_player(self, *things):
        for thing in things:
            globals.player.lose(thing)

    def freeze_player(self):
        globals.player.immobilize()

    def unfreeze_player(self):
        globals.player.unimmobilize()


class EntityScript(Script):
    def __init__(self, sprite, registry):
        self.sprite = sprite
        super().__init__(registry)

    def get_sprite_state(self):
        return self.sprite.state  # TODO?

    def face(self, sprite):
        self.sprite.facing = util.round_string_direction(
            util.string_direction(sprite.pos - self.sprite.pos)
        )
