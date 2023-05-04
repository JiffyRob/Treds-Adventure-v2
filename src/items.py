import pygame

import globals
import gui

ITEM_DATA = gui.ITEM_DATA

pygame.font.init()


class ItemCallback:
    def __init__(self, player, rebuild_callback, item_name):
        self.player = player
        self.item_name = item_name
        item_data = ITEM_DATA.get(self.item_name, {})
        self.item_data = {
            **ITEM_DATA["default"],  # default item data
            **ITEM_DATA.get(
                item_data.get("type", "default"), {}
            ),  # default item data based off item type
            **item_data,  # item data
            "params": {
                **ITEM_DATA["default"].get("params", {}),  # default item params
                **ITEM_DATA.get(item_data.get("type", "default"), {}).get(
                    "params", {}
                ),  # default item params based on type
                **item_data.get("params", {}),  # item params
            },
        }
        # print(self.item_name, self.item_data)
        self.item_callback = {
            "food": self.food_item,
            "tool": self.tool_item,
        }.get(self.item_data.get("type", "default"), self.nothing_item)
        self.item_kwargs = self.item_data.get("params", {})
        self.consume_to = self.item_data.get("consume_to", None)
        self.rebuild_callback = rebuild_callback

    def food_item(self, hp, mp, hp_aftereffect):
        self.player.heal(hp)
        self.player.heal_mp(mp)

    def tool_item(self, tool_id):
        self.player.equip(tool_id)

    def nothing_item(self, *args, **kwargs):
        print("This item does nothning, so here is some debug info:")
        print(self.player.items, args, kwargs)

    def __call__(self):
        self.item_callback(**self.item_kwargs)
        if self.consume_to is not None:
            if self.item_name in self.player.items:
                self.player.items[self.item_name] = (
                    self.player.items[self.item_name] - 1
                )
                if self.player.items[self.item_name] < 1:
                    self.player.items.pop(self.item_name)
            if self.consume_to == "empty":
                print("bye bye item!")
            elif self.consume_to in self.player.items:
                self.player.items[self.consume_to] += 1
            else:
                self.player.items[self.consume_to] = 1
            self.rebuild_callback()


def create_item_menu(player, rebuild_callback):
    def get_item_button_data(items, rows=6, size=(32, 32), n=24):
        item_iter = iter(items.items())
        index = pygame.Vector2()
        padding = 0
        w, h = size
        for _ in range(n):
            try:
                item, amount = next(item_iter)
            except StopIteration:
                item, amount = "empty", 0
            position = index.elementwise() * (w + padding, h + padding)
            position += (1, 1)
            yield item, amount, position
            index.x += 1
            if index.x >= rows:
                index.x = 0
                index.y += 1

    menu_rect = pygame.Rect((0, 0), globals.engine.screen_size - (192, 128))
    menu_rect.center = globals.engine.screen_size / 2
    gui_group = gui.UIGroup()
    bg = gui.BGRect(menu_rect, 1, gui_group)

    bottom_rect = pygame.Rect(menu_rect.left, 0, menu_rect.width, 100)
    dbox = gui.Descriptionbox(bottom_rect, 1, gui_group)
    right_rect = pygame.Rect(0, menu_rect.top, 0, menu_rect.height)

    bottom = 0
    right = 0
    for name, amount, pos in get_item_button_data(player.items):
        button_rect = pygame.Rect(pos + menu_rect.topleft, (32, 32))
        gui.ItemButton(
            name,
            amount,
            ItemCallback(player, rebuild_callback, name),
            dbox,
            button_rect,
            2,
            gui_group,
        )
        bottom = button_rect.bottom
        right = button_rect.right

    dbox.rect = pygame.Rect(
        bottom_rect.left,
        bottom,
        bottom_rect.width,
        menu_rect.top + (menu_rect.height - bottom),
    )
    dbox.rebuild()

    right_rect.left = right
    right_rect.width = menu_rect.right - right
    gui.HeartMeter(globals.player, right_rect, 2, gui_group)

    return gui_group
