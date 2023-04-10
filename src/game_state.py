import os

import pygame
import pygame_gui

import items
import menu
from bush import asset_handler, event_binding, sound_manager, timer
from bush.ai import state

# defining variables like this allows to flip out to specific ones later
# the audio player is by default linked to the asset loader
loader = asset_handler.glob_loader
# Don't make a new music player.  Only 1 should exist
music_player = sound_manager.music_player
EXT = ".json"


class GameState(state.StackState):
    def __init__(
        self,
        value,
        engine,
        on_push=lambda: None,
        on_pop=lambda: None,
        gui=None,
        enable_cursor=False,
    ):
        self.engine = engine
        self.cursor = engine.cursor
        self.input_handler = event_binding.EventHandler()
        self.input_handler.update_bindings(loader.load("data/game_bindings.json"))
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
            if event.name == "pop state":
                print("pop!")
                self.pop()
            if event.name == "toggle fullscreen":
                self.engine.toggle_fullscreen()
            if event.name == "pause":
                self._stack.push(
                    PauseMenu(
                        self.engine, screen_surf=pygame.display.get_surface().convert()
                    )
                )
            if event.name == "quit":
                self.engine.quit()
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


class MapState(GameState):
    def __init__(self, map_name, groups, engine, soundtrack=None):
        self.groups = groups
        self.sky = engine.sky
        self.main_group = groups["main"]
        self.player = groups["player"].sprite
        self.soundtrack = soundtrack
        if self.soundtrack is not None:
            music_player.play(self.soundtrack)
        gui = pygame_gui.UIManager(engine.screen_size, menu.THEME_PATH)
        heart_images = loader.load(
            "hud/heart.png",
            loader=asset_handler.load_spritesheet,
            frame_size=(16, 16),
        )
        menu.HeartMeter(pygame.Rect(8, 8, -1, -1), heart_images, engine.player, gui)
        get_player_mana = (
            lambda: engine.player.current_mana / engine.player.mana_capacity
        )
        pygame_gui.elements.UIStatusBar(
            pygame.Rect(-68, 4, 64, 9),
            gui,
            percent_method=get_player_mana,
            anchors={"top": "top", "right": "right"},
        )
        super().__init__(map_name, engine, gui=gui)
        self.input_handler.update_bindings(loader.load("data/player_bindings.json"))

    def update(self, dt=0.03):
        super().update(dt)
        self.sky.update(dt)
        self.main_group.update(dt)

    def handle_events(self):
        for event in pygame.event.get():
            super().handle_event(event)
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
        self.interpreter = None  # TODO
        super().__init__(map_name, engine)

    def update(self, dt=0.03):
        # self.interpreter.run()
        self.main_group.update(dt)
        self.sky.update(dt)
        # if self.interpreter.finished():
        #     self.pop()

    def handle_event(self, event):
        if event.type == event_binding.BOUND_EVENT and event.name == "pop state":
            return
        super().handle_event(event)

    def draw(self, surface):
        self.main_group.draw(surface)
        self.sky.render(surface)


class MenuState(GameState):
    def __init__(
        self,
        value,
        engine,
        on_push=None,
        on_pop=None,
        button_bindings=None,
        supermenu=None,
        screen_surf=None,
    ):
        if on_push is None:
            on_push = lambda: None
        if on_pop is None:
            if supermenu is None:
                on_pop = lambda: None
            else:
                on_pop = lambda: supermenu.rebuild()
        super().__init__(value, engine, on_push, on_pop, enable_cursor=True)
        self.screen_surf = screen_surf
        if supermenu is not None and self.screen_surf is None:
            self.screen_surf = supermenu.screen_surf
        self.button_bindings = button_bindings or {}
        self.nothing_func = lambda: None
        self.rebuild()
        self.input_handler.disable_event("pause")
        self.supermenu = supermenu

    def rebuild(self):
        self.gui = None

    def draw(self, surface):
        if self.screen_surf is not None:
            surface.blit(self.screen_surf, (0, 0))
        super().draw(surface)

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self.button_bindings.get(event.ui_element.text, self.nothing_func)()

    def run_submenu(self, menu_type, **kwargs):
        self._stack.push(menu_type(engine=self.engine, supermenu=self, **kwargs))


class PauseMenu(MenuState):
    def __init__(self, engine, screen_surf):
        super().__init__(
            "PauseMenu",
            engine,
            button_bindings={
                "Resume": self.pop,
                "Items": self.run_item_menu,
                "Load/Save": self.run_loadsave_menu,
                "Quit": engine.quit,
            },
            screen_surf=screen_surf,
        )

    def rebuild(self):
        self.gui = menu.create_menu(
            "PauseMenu",
            ["Resume", "Items", "Load/Save", "Quit"],
            self.engine.screen_size,
        )

    def run_item_menu(self):
        self.run_submenu(ItemMenu)

    def run_loadsave_menu(self):
        self.run_submenu(LoadSaveMenu)


class ItemMenu(MenuState):
    def __init__(self, engine, supermenu):
        super().__init__("ItemMenu", engine, supermenu=supermenu)
        self.button_dict = {}

    def rebuild(self):
        self.gui, self.button_dict = items.create_item_menu(
            self.engine.player.items, self.engine
        )


class LoadSaveMenu(MenuState):
    def __init__(self, engine, supermenu):
        super().__init__(
            "LoadSaveMenu",
            engine,
            button_bindings={
                "Load": self.run_load_menu,
                "Save": self.run_save_menu,
                "Back": self.pop,
            },
            supermenu=supermenu,
        )

    def rebuild(self):
        self.gui = menu.create_menu(
            "Load/Save",
            ["Load", "Save", "Back"],
            self.engine.screen_size,
        )

    def run_load_menu(self):
        self.run_submenu(LoadMenu)

    def run_save_menu(self):
        self.run_submenu(SaveMenu)


class SaveMenu(MenuState):
    def __init__(self, engine, supermenu):
        self.save_names = []
        super().__init__(
            "SaveMenu",
            engine,
            button_bindings={"New!": self.run_newsave, "Back": self.pop},
            supermenu=supermenu,
        )

    def rebuild(self):
        button_names = []
        for name in get_save_names(self.engine.state.loader.base):
            button_names.append(name)
        button_names.append("Back")
        self.gui = menu.create_menu("Save", button_names, self.engine.screen_size)
        button_names = [i for i in button_names if i != "Back"]
        self.save_names = button_names

    def handle_events(self):
        for event in pygame.event.get():
            self.handle_event(event)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element.text in self.save_names:
                    self.save(event.ui_element.text)

    def run_newsave(self):
        pass

    def delete_save(self):
        pass

    def save(self, name):
        print("Saving", name)
        self.engine.state.save(name + EXT)


class LoadMenu(MenuState):
    def __init__(self, engine, supermenu):
        self.save_names = []
        super().__init__(
            "LoadMenu", engine, button_bindings={"Back": self.pop}, supermenu=supermenu
        )

    def rebuild(self):
        button_names = []
        for name in get_save_names(self.engine.state.loader.base):
            button_names.append(name)
        button_names.append("Back")
        self.gui = menu.create_menu("Load", button_names, self.engine.screen_size)
        button_names = [i for i in button_names if i != "Back"]
        self.save_names = button_names

    def handle_events(self):
        for event in pygame.event.get():
            self.handle_event(event)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element.text in self.save_names:
                    self.load(event.ui_element.text)

    def load(self, name):
        print("Loading", name)
        path = name + EXT
        self.engine.state.load(path)


class MainMenu(MenuState):
    def __init__(self, engine):
        super().__init__(
            "MainMenu",
            engine,
            button_bindings={
                "New Game": self.run_newmenu,
                "Load Game": self.run_loadmenu,
                "Quit": engine.quit,
            },
            screen_surf=loader.load("hud/bg_forest.png"),
        )

    def rebuild(self):
        self.gui = menu.create_menu(
            "Tred's Adventure",
            ["New Game", "Load Game", "Quit"],
            self.engine.screen_size,
        )

    def run_newmenu(self):
        self.run_submenu(NewSaveMenu)

    def run_loadmenu(self):
        self.run_submenu(LoadMenu)


class NewSaveMenu(MenuState):
    def __init__(self, engine, supermenu):
        self.text_input = None
        super().__init__(
            "NewSaveMenu",
            engine,
            button_bindings={"Confirm": self.save, "Back": self.pop},
            supermenu=supermenu,
        )

    def rebuild(self):
        self.gui, container, skipped = menu.create_menu(
            "New Game",
            [":SKIP", "Confirm", "Back"],
            self.engine.screen_size,
            return_container=True,
            return_skipped=True,
        )
        self.text_input = pygame_gui.elements.UITextEntryLine(
            skipped[0], self.gui, container, placeholder_text="Save Name"
        )

    def handle_events(self):
        for event in pygame.event.get():
            self.handle_event(event)
            if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                print(event.text)
            if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                self.save()

    def save(self):
        print("Saving", self.text_input.text)
        path = self.text_input.text + EXT
        self.engine.state.load("../default_save_values.json")
        self.engine.state.save(path)


def get_save_names(path):
    for dir_entry in os.scandir(path):
        name, ext = dir_entry.name.split(".")
        print(name, ext)
        if ext == EXT[1:]:
            yield name
