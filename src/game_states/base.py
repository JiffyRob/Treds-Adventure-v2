import pygame

import globals
from bush import asset_handler, event_binding, sound
from bush.ai import state


class GameState(state.StackState):
    loader = asset_handler.glob_loader
    save_ext = ".json"

    def __init__(
        self,
        value,
        on_push=lambda: None,
        on_pop=lambda: None,
        gui=None,
        enable_cursor=False,
    ):
        self.cursor = globals.engine.cursor
        self.input_handler = event_binding.EventHandler()
        self.input_handler.update_bindings(self.loader.load("data/game_bindings.json"))
        self.screen_surf = None
        self.gui = gui
        self.enable_cursor = enable_cursor
        super().__init__(value, on_push, on_pop)

    def reset_cursor(self):
        if self.enable_cursor:
            self.cursor.enable()
        else:
            self.cursor.hide()

    def handle_events(self):
        for event in pygame.event.get():
            self.handle_event(event)

    def handle_event(self, event):
        if self.gui:
            self.gui.process_events(event)
        self.cursor.event(event)
        self.input_handler.process_event(event)
        if event.type == event_binding.BOUND_EVENT:
            if event.name == "toggle fullscreen":
                globals.engine.toggle_fullscreen()
            if event.name == "quit":
                globals.engine.quit()
            if event.name == "add joystick":
                self.input_handler.add_joystick(event.original_event.device_index)
            if event.name == "remove joystick":
                self.input_handler.remove_joystick(event.original_event.device_index)
            if event.name == "screenshot":
                surface = pygame.display.get_surface()
                pygame.image.save(surface, "screenshot.png")

    def cache_screen(self):
        self.screen_surf = pygame.display.get_surface().copy()

    def draw(self, surface):
        if self.gui:
            self.gui.draw_ui(surface)

    def update(self, dt=0.03):
        super().update()
        if self.gui is not None:
            self.gui.update(dt)
        if self.cursor.visible != self.enable_cursor:
            self.reset_cursor()
