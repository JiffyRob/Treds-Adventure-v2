import pygame
import pygame_gui

import menu
from bush import asset_handler, event_binding
from bush.ai import scripting, state

loader = asset_handler.glob_loader


class GameState(state.StackState):
    def __init__(
        self, value, engine, on_push=lambda: None, on_pop=lambda: None, gui=None
    ):
        self.engine = engine
        self.cursor = engine.cursor
        self.cursor.hide()
        self.input_handler = event_binding.EventHandler()
        self.input_handler.update_bindings(loader.load("data/game_bindings.json"))
        self.screen_surf = None
        self.gui = gui
        print(self.gui, self.gui.get_sprite_group())
        super().__init__(value, on_push, on_pop)

    def handle_events(self):
        for event in pygame.event.get():
            self.handle_event(event)

    def handle_event(self, event):
        if self.gui:
            self.gui.process_events(event)
        self.input_handler.process_event(event)
        if event.type == event_binding.BOUND_EVENT:
            if event.name == "pop state":
                print("pop!")
                self.pop()
            if event.name == "toggle fullscreen":
                self.engine.toggle_fullscreen()
            if event.name == "pause":
                self._stack.push(PausemenuState(self.engine))
            if event.name == "quit":
                self.engine.quit()
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
        self.gui.update(dt)


class MapState(GameState):
    def __init__(self, map_name, groups, engine):
        self.groups = groups
        self.sky = engine.sky
        self.main_group = groups["main"]
        self.player = groups["player"].sprite
        self.player_input_handler = event_binding.EventHandler({})
        self.player_input_handler.update_bindings(
            loader.load("data/player_bindings.json")
        )
        gui = pygame_gui.UIManager(engine.screen_size, menu.THEME_PATH)
        heart_images = loader.load(
            "resources/hud/heart.png",
            loader=asset_handler.load_spritesheet,
            frame_size=(16, 16),
        )
        menu.HeartMeter(pygame.Rect(8, 8, -1, -1), heart_images, engine.player, gui)
        super().__init__(map_name, engine, gui=gui)

    def update(self, dt=0.03):
        super().update(dt)
        self.sky.update(dt)
        self.main_group.update(dt)

    def handle_events(self):
        for event in pygame.event.get():
            super().handle_event(event)
            self.player_input_handler.process_event(event)
            self.player.event(event)

    def draw(self, surface):
        self.main_group.draw(surface)
        self.sky.render(surface)
        super().draw(surface)


class ScriptedMapState(GameState):
    def __init__(self, map_name, groups, engine, script):
        self.groups = groups
        self.sky = engine.sky
        self.main_group = groups["main"]
        self.player = groups["player"].sprite
        scripting_api = {"command-player": engine.player_command}
        self.interpreter = scripting.EJECSController(script, scripting_api)
        super().__init__(map_name, engine)

    def update(self, dt=0.03):
        self.interpreter.run()
        self.main_group.update(dt)
        self.sky.update(dt)
        if self.interpreter.finished():
            self.pop()

    def handle_event(self, event):
        if event.type == event_binding.BOUND_EVENT and event.name == "pop state":
            return
        super().handle_event(event)

    def draw(self, surface):
        self.main_group.draw(surface)
        self.sky.render(surface)


class PausemenuState(GameState):
    def __init__(self, engine):
        self.menu = menu.create_menu("Paused", ("Resume", "Quit"), engine.screen_size)
        super().__init__(
            "Pausemenu",
            engine,
            on_push=lambda: (self.cursor.enable(), self.cache_screen()),
            on_pop=lambda: self.cursor.hide(),
        )
        self.input_handler.disable_event("pause")
        self.cursor.enable()

    def handle_events(self):
        for event in pygame.event.get():
            super().handle_event(event)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element.text == "Quit":
                    self.engine.quit()
                if event.ui_element.text == "Resume":
                    self.pop()
            self.menu.process_events(event)

    def draw(self, surface):
        surface.blit(self.screen_surf, (0, 0))
        self.menu.draw_ui(surface)

    def update(self, dt=0.03):
        super().update(dt)
        self.menu.update(dt)
