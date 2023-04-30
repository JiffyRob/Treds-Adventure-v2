import pygame

from bush import sound_manager, util

player = sound_manager.glob_player
STATE_RUNNING = 0
STATE_PAUSED = 1
STATE_FINISHED = 2


class Script:
    def __init__(self, engine, entity_group, other_groups):
        self.engine = engine
        self.player = engine.player
        self.entity_group = entity_group
        self.other_groups = other_groups
        self.timer_list = []
        self.sky = self.engine.sky
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
        self.entity_group.get_by_id(name)

    def get_time(self):
        return ("night", "day")[self.sky.is_day()]

    def get_group(self, name):
        return self.other_groups.get(name, None)

    def add_timer(self, new_timer):
        self.timer_list.append(new_timer)

    def clear_timers(self):
        self.timer_list = []

    def say(self, text, on_finish=lambda interrupted: None):
        self.engine.dialog(text, (), on_finish)

    def ask(self, question, answers, on_finish=lambda interrupted, answer: None):
        self.engine.dialog(question, answers, on_finish)

    def play_sound(self, sound_name):
        player.play(sound_name)

    def spawn_particles(self):
        # TODO
        pass

    def give_player(self, *things):
        for thing in things:
            self.player.get(thing)

    def take_from_player(self, *things):
        for thing in things:
            self.player.lose(thing)

    def freeze_player(self):
        self.player.immobilize()

    def unfreeze_player(self):
        self.player.unimmobilize()


class EntityScript(Script):
    def __init__(self, sprite, engine, entity_group, other_groups=None):
        self.sprite = sprite
        super().__init__(engine, entity_group, other_groups)

    def get_sprite_state(self):
        return self.sprite.state  # TODO?

    def face(self, sprite):
        self.sprite.facing = util.round_string_direction(
            util.string_direction(sprite.pos - self.sprite.pos)
        )
