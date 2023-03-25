import pygame

from bush import sound_manager, timer

player = sound_manager.glob_player


class Script:
    def __init__(self, engine, entity_group, other_groups):
        self.engine = engine
        self.player = player
        self.entity_group = entity_group
        self.other_groups = other_groups
        self.timer_list = []
        self.sky = self.engine.sky
        self.running = False
        self.complete = False
        self.init()

    def init(self):
        pass

    def reset(self):
        self.complete = False

    def begin(self):
        self.running = True
        self.complete = False

    def end(self):
        self.running = False
        self.complete = True

    def pause(self):
        self.running = False

    def unpause(self):
        self.running = True

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

    def say(self, text, on_finish=lambda: None):
        self.engine.dialog(text, on_finish)

    def ask(self, question, *answers, on_finish=lambda: None):
        self.engine.dialog(question, *answers, on_finish=on_finish)

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

    def update(self, dt):
        if self.running:
            self.script_update(dt)

    def script_update(self, dt):
        for timer_to_update in self.timer_list:
            timer_to_update.update()
        self.timer_list = [i for i in self.timer_list if i.time_left()]


class EntityScript(Script):
    def __init__(self, sprite, engine, entity_group, other_groups=None):
        self.sprite = sprite
        super().__init__(engine, entity_group, other_groups)

    def get_sprite_state(self):
        return self.sprite.state  # TODO?

    def is_finished(self):
        return True
