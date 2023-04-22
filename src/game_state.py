import os
from functools import partial

import pygame
import pygame_gui

import gui
import items
import menu
from bush import asset_handler, event_binding, sound_manager, text_util
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
        hud = gui.UIGroup()
        gui.HeartMeter(engine.player, pygame.Rect(8, 8, 1, 1), 1, hud)
        get_player_mana = (
            lambda: engine.player.current_mana / engine.player.mana_capacity
        )
        rect = pygame.Rect(0, 4, 64, 9)
        rect.right = engine.screen_size.x - 4
        gui.MagicMeter(engine.player, rect, 1, hud)
        super().__init__(map_name, engine, gui=hud)
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
        pygame.draw.rect(
            surface,
            (255, 0, 0),
            self.engine.player.get_interaction_rect().move(
                self.main_group.cam_rect.topleft
            ),
            1,
        )
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

    def run_submenu(self, menu_type, **kwargs):
        self._stack.push(menu_type(engine=self.engine, supermenu=self, **kwargs))


class PauseMenu(MenuState):
    def __init__(self, engine, screen_surf):
        super().__init__(
            "PauseMenu",
            engine,
            screen_surf=screen_surf,
        )

    def rebuild(self):
        self.gui = menu.create_menu(
            "PauseMenu",
            ["Resume", "Items", "Load/Save", "Quit"],
            [self.pop, self.run_item_menu, self.run_loadsave_menu, self.engine.quit],
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
        self.gui = items.create_item_menu(self.engine.player, self.engine, self.rebuild)


class LoadSaveMenu(MenuState):
    def __init__(self, engine, supermenu):
        super().__init__(
            "LoadSaveMenu",
            engine,
            supermenu=supermenu,
        )

    def rebuild(self):
        self.gui = menu.create_menu(
            "Load/Save",
            ["Load", "Save", "Back"],
            [self.run_load_menu, self.run_save_menu, self.pop],
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
            supermenu=supermenu,
        )

    def rebuild(self):
        button_names = []
        button_functions = []
        for name in get_save_names(self.engine.state.loader.base):
            button_names.append(name)
            button_functions.append(partial(self.save, name))
        button_names.append("Back")
        self.gui = menu.create_menu(
            "Save", button_names, button_functions, self.engine.screen_size
        )
        self.save_names = [i for i in button_names if i != "Back"]

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
        super().__init__("LoadMenu", engine, supermenu=supermenu)

    def rebuild(self):
        button_names = []
        button_functions = []
        for name in get_save_names(self.engine.state.loader.base):
            button_names.append(name)
            button_functions.append(partial(self.load, name))
        button_names.append("Back")
        self.gui = menu.create_menu(
            "Load", button_names, button_functions, self.engine.screen_size
        )
        self.save_names = [i for i in button_names if i != "Back"]

    def load(self, name):
        print("Loading", name)
        path = name + EXT
        self.engine.state.load(path)


class MainMenu(MenuState):
    def __init__(self, engine):
        super().__init__(
            "MainMenu",
            engine,
            screen_surf=loader.load("hud/bg_forest.png"),
        )

    def rebuild(self):
        self.gui = menu.create_menu(
            "Tred's Adventure",
            ["New Game", "Load Game", "Quit"],
            [self.run_newmenu, self.run_loadmenu, self.pop],
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
            supermenu=supermenu,
        )

    def rebuild(self):
        self.gui, container, skipped = menu.create_menu(
            "New Game",
            [":SKIP", "Confirm", "Back"],
            [None, self.save, self.pop],
            self.engine.screen_size,
            return_container=True,
            return_skipped=True,
        )
        self.text_input = gui.TextInput("", text_util.filename, skipped[0], 2, self.gui)

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
