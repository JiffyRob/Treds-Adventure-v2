import functools
import os

import globals
import gui
import items
import menu
from bush import text_util, util
from game_states import base


class MenuState(base.GameState):
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
        for name in get_save_names(globals.engine.state.loader.base, self.save_ext):
            button_names.append(name)
            button_functions.append(functools.partial(self.save, name))
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
        globals.engine.state.save(name + self.save_ext)


class LoadMenu(MenuState):
    def __init__(self, supermenu):
        self.save_names = []
        super().__init__("LoadMenu", supermenu=supermenu)

    def rebuild(self):
        button_names = []
        button_functions = []
        for name in get_save_names(globals.engine.state.loader.base, self.save_ext):
            button_names.append(name)
            button_functions.append(functools.partial(self.load, name))
        button_names.append("Back")
        self.gui = menu.create_menu(
            "Load", button_names, button_functions, globals.engine.screen_size
        )
        self.save_names = [i for i in button_names if i != "Back"]

    def load(self, name):
        path = name + self.save_ext
        globals.engine.state.load(path)


class MainMenu(MenuState):
    def __init__(self):
        self.button_list = ("New Game", "Load Game", "Quit")
        if util.is_pygbag():
            self.button_list = self.button_list[:-1]
        super().__init__(
            "MainMenu",
            screen_surf=self.loader.load("hud/bg_forest.png"),
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
        path = self.text_input.text + self.save_ext
        globals.engine.state.load("../default_save_values.json")
        globals.engine.state.save(path)


def get_save_names(path, save_ext):
    for dir_entry in os.scandir(path):
        name, ext = dir_entry.name.split(".")
        if ext == save_ext[1:]:
            yield name
