import pygame
from pygame_menu import Menu, font, themes, widgets

from bush import asset_handler, event_binding
from bush.ai import scripting, state

loader = asset_handler.glob_loader

menu_theme = themes.Theme(
    # all colors match the NinjaAdventure palette
    background_color=(20, 27, 27),
    border_color=(45, 105, 123),
    border_width=1,
    cursor_color=(255, 255, 255),
    cursor_selection_color=(242, 234, 241),
    cursor_switch_ms=550,
    focus_background_color=(142, 124, 115),
    fps=30,
    readonly_color=(78, 72, 74),
    readonly_selected_color=(142, 124, 115),
    scrollbar_shadow=False,
    scrollbar_slider_color=(78, 72, 74),
    scrollbar_thick=6,
    selection_color=(255, 255, 255),
    surface_clear_color=(20, 27, 27),
    title=True,
    title_background_color=(45, 105, 123),
    title_bar_style=widgets.MENUBAR_STYLE_UNDERLINE,
    title_close_button=False,
    title_fixed=False,
    title_floating=True,
    title_font=font.FONT_8BIT,
    title_font_antialias=False,
    title_font_color=(255, 255, 255),
    title_font_shadow=False,
    title_font_size=16,
    title_offset=(4, 4),
    title_updates_pygame_display=True,
    widget_font=font.FONT_MUNRO,
    widget_font_size=31,
    # widget_selection_effect=widgets.LeftArrowSelection((15, 15)),
)


class GameState(state.StackState):
    def __init__(self, value, engine, on_push=lambda: None, on_pop=lambda: None):
        self.engine = engine
        self.input_handler = event_binding.EventHandler()
        self.input_handler.update_bindings(loader.load("data/game_bindings.json"))
        super().__init__(value, on_push, on_pop)

    def handle_events(self):
        for event in pygame.event.get():
            self.handle_event(event)

    def handle_event(self, event):
        self.input_handler.process_event(event)
        if event.type == event_binding.BOUND_EVENT:
            print(event.name)
            if event.name == "pop state":
                print("pop!")
                self.pop()
            if event.name == "toggle fullscreen":
                self.engine.toggle_fullscreen()
            if event.name == "pause":
                self._stack.push(PausemenuState(self.engine))
            if event.name == "quit":
                self.engine.quit()

    def draw(self, surface):
        pass

    def update(self, dt=0.03):
        super().update()


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
        super().__init__(map_name, engine)

    def update(self, dt=0.03):
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


class ScriptedMapState(GameState):
    def __init__(self, map_name, groups, engine, script, state_once_finished=None):
        self.groups = groups
        self.sky = self.engine.sky
        self.main_group = groups["main"]
        self.player = groups["player"].sprite
        self.state_once_finished = state_once_finished
        scripting_api = {"command-player": engine.player_command}
        self.interpreter = scripting.EJECSController(script, scripting_api)
        super().__init__(map_name, engine, lambda: None)

    def update(self, dt=0.03):
        self.interpreter.run()
        self.main_group.update()
        self.sky.update()
        if self.interpreter.finished():
            self.pop()
            if self.state_once_finished:
                self._stack.push(self.state_once_finished)

    def draw(self, surface):
        self.main_group.draw(surface)
        self.sky.render(surface)


class PausemenuState(GameState):
    def __init__(self, engine):
        self.menu = Menu(
            "Paused",
            engine.screen_size.x * 0.7,
            engine.screen_size.y - 64,
            theme=menu_theme,
            mouse_visible=False,
        )
        self.menu.add.button("Resume", self.pop)
        self.menu.add.button("Quit", engine.quit)
        self.menu.set_onclose(self.pop)
        self.menu.disable()

        def enable_menu():
            if not self.menu.is_enabled():
                self.menu.enable()

        def disable_menu():
            if self.menu.is_enabled():
                self.menu.disable()

        super().__init__("Pausemenu", engine, enable_menu, disable_menu)

    def handle_events(self):
        events = list(pygame.event.get())
        for event in events:
            super().handle_event(event)
        self.menu.update(events)

    def draw(self, surface):
        self.menu.draw(surface)
