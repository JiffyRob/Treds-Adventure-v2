import os
from functools import partial

import pygame

import globals
import gui
import items
import menu
from bush import asset_handler, event_binding, sound_manager, text_util, util
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
        on_push=lambda: None,
        on_pop=lambda: None,
        gui=None,
        enable_cursor=False,
    ):
        self.cursor = globals.engine.cursor
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
                globals.engine.toggle_fullscreen()
            if event.name == "pause":
                self._stack.push(
                    PauseMenu(screen_surf=pygame.display.get_surface().convert())
                )
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


class MapState(GameState):
    def __init__(self, map_name, registry, soundtrack=None):
        self.registry = registry
        self.sky = globals.engine.sky
        self.main_group = self.registry.get_group("main")
        self.player = registry.get_group("player").sprite
        self.soundtrack = soundtrack
        if self.soundtrack is not None:
            music_player.play(self.soundtrack)
        hud = gui.UIGroup()
        gui.HeartMeter(globals.player, pygame.Rect(8, 8, 192, 64), 1, hud)
        get_player_mana = (
            lambda: globals.player.current_mana / globals.player.mana_capacity
        )
        rect = pygame.Rect(0, 4, 64, 9)
        rect.right = globals.engine.screen_size.x - 4
        gui.MagicMeter(globals.player, rect, 1, hud)
        super().__init__(map_name, gui=hud)
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
        if self.main_group.debug_physics:
            pygame.draw.rect(
                surface,
                (255, 0, 0),
                globals.player.get_interaction_rect().move(
                    -pygame.Vector2(self.main_group.cam_rect.topleft)
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
        super().__init__(value, on_push, on_pop, enable_cursor=True)
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
        self._stack.push(menu_type(supermenu=self, **kwargs))


class PauseMenu(MenuState):
    def __init__(self, screen_surf):
        super().__init__(
            "PauseMenu",
            screen_surf=screen_surf,
        )

    def rebuild(self):
        self.gui = menu.create_menu(
            "PauseMenu",
            ["Resume", "Items", "Load/Save", "Quit"],
            [self.pop, self.run_item_menu, self.run_loadsave_menu, globals.engine.quit],
            globals.engine.screen_size,
        )

    def run_item_menu(self):
        self.run_submenu(ItemMenu)

    def run_loadsave_menu(self):
        self.run_submenu(LoadSaveMenu)


class ItemMenu(MenuState):
    def __init__(self, supermenu):
        super().__init__("ItemMenu", supermenu=supermenu)
        self.button_dict = {}

    def rebuild(self):
        self.gui = items.create_item_menu(globals.player, self.rebuild)


class LoadSaveMenu(MenuState):
    def __init__(self, supermenu):
        super().__init__(
            "LoadSaveMenu",
            supermenu=supermenu,
        )

    def rebuild(self):
        self.gui = menu.create_menu(
            "Load/Save",
            ["Load", "Save", "Back"],
            [self.run_load_menu, self.run_save_menu, self.pop],
            globals.engine.screen_size,
        )

    def run_load_menu(self):
        self.run_submenu(LoadMenu)

    def run_save_menu(self):
        self.run_submenu(SaveMenu)


class SaveMenu(MenuState):
    def __init__(self, supermenu):
        self.save_names = []
        super().__init__(
            "SaveMenu",
            supermenu=supermenu,
        )

    def rebuild(self):
        button_names = []
        button_functions = []
        for name in get_save_names(globals.engine.state.loader.base):
            button_names.append(name)
            button_functions.append(partial(self.save, name))
        button_names.append("Back")
        self.gui = menu.create_menu(
            "Save", button_names, button_functions, globals.engine.screen_size
        )
        self.save_names = [i for i in button_names if i != "Back"]

    def run_newsave(self):
        pass

    def delete_save(self):
        pass

    def save(self, name):
        globals.engine.state.save(name + EXT)


class LoadMenu(MenuState):
    def __init__(self, supermenu):
        self.save_names = []
        super().__init__("LoadMenu", supermenu=supermenu)

    def rebuild(self):
        button_names = []
        button_functions = []
        for name in get_save_names(globals.engine.state.loader.base):
            button_names.append(name)
            button_functions.append(partial(self.load, name))
        button_names.append("Back")
        self.gui = menu.create_menu(
            "Load", button_names, button_functions, globals.engine.screen_size
        )
        self.save_names = [i for i in button_names if i != "Back"]

    def load(self, name):
        path = name + EXT
        globals.engine.state.load(path)


class MainMenu(MenuState):
    def __init__(self):
        self.button_list = ("New Game", "Load Game", "Quit")
        if util.is_pygbag():
            self.button_list = self.button_list[:-1]
        super().__init__(
            "MainMenu",
            screen_surf=loader.load("hud/bg_forest.png"),
        )

    def rebuild(self):
        self.gui = menu.create_menu(
            "Tred's Adventure",
            self.button_list,
            [self.run_newmenu, self.run_loadmenu, self.pop],
            globals.engine.screen_size,
        )

    def pop(self):
        if util.is_pygbag():
            return  # No quit in pygbag
        super().pop()

    def run_newmenu(self):
        self.run_submenu(NewSaveMenu)

    def run_loadmenu(self):
        self.run_submenu(LoadMenu)


class NewSaveMenu(MenuState):
    def __init__(self, supermenu):
        self.text_input = None
        super().__init__(
            "NewSaveMenu",
            supermenu=supermenu,
        )

    def rebuild(self):
        self.gui, container, skipped = menu.create_menu(
            "New Game",
            [":SKIP", "Confirm", "Back"],
            [None, self.save, self.pop],
            globals.engine.screen_size,
            return_container=True,
            return_skipped=True,
        )
        self.text_input = gui.TextInput("", text_util.filename, skipped[0], 2, self.gui)

    def save(self):
        path = self.text_input.text + EXT
        globals.engine.state.load("../default_save_values.json")
        globals.engine.state.save(path)


def get_save_names(path):
    for dir_entry in os.scandir(path):
        name, ext = dir_entry.name.split(".")
        if ext == EXT[1:]:
            yield name
