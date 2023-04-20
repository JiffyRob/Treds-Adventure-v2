import pygame

import menu
from bush import entity, util_load

pygame.font.init()
ITEM_GLOB = util_load.load_json("resources/data/items.json")
ITEM_IMAGES = dict(
    zip(
        ITEM_GLOB["image_order"],
        util_load.load_spritesheet("resources/hud/items.png", (16, 16)),
    )
)
ITEM_DATA = ITEM_GLOB["data"]

BG_IMAGES = [
    util_load.load_image(f"resources/hud/{i}.png")
    for i in ("empty", "empty-hovered", "empty-selected")
]
NUMBER_FONT = pygame.font.Font("resources/hud/TeenyTinyPixls.ttf", 5)

STATE_NORMAL = 0
STATE_HOVERED = 1
STATE_CLICKED = 2


class ItemGUIGroup(pygame.sprite.LayeredDirty):
    def draw_ui(self, surface):
        self.draw(surface)

    def process_events(self, event):
        for sprite in self.sprites():
            sprite.pass_event(event)


class ItemButton(pygame.sprite.DirtySprite):
    def __init__(self, item_name, item_count, on_click, rect, layer, gui_group):
        super().__init__()
        self.name = item_name
        self.count = item_count
        self.on_click = on_click
        self.rect = rect
        self.layer = layer
        # the bug net is not implemented (as of writing this comment), so it will be the debug item image
        self.item_image = pygame.transform.scale(
            ITEM_IMAGES.get(self.name, "bug net"), self.rect.size
        )
        self.count_image = NUMBER_FONT.render(str(self.count), False, (242, 234, 241))
        self.state = STATE_NORMAL
        self.bg_images = [pygame.transform.scale(i, self.rect.size) for i in BG_IMAGES]
        self.image = None
        self.rebuild()
        self.dirty = 2

        self.add(gui_group)

    def rebuild(self):
        self.image = self.bg_images[self.state].copy()
        self.image.blit(self.item_image, (0, 0))
        if self.count:
            number_pos = pygame.Vector2(self.rect.size) - (5, 7)
            self.image.blit(self.count_image, number_pos)
        # self.dirty = 1  # redraw

    def pass_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                if self.state == STATE_NORMAL:
                    self.state = STATE_HOVERED
                    self.rebuild()
            elif self.state == STATE_HOVERED:
                self.state = STATE_NORMAL
                self.rebuild()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and event.button == 1:
                self.state = STATE_CLICKED
                self.on_click()
                self.rebuild()

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.state = STATE_HOVERED
                    self.rebuild()
                else:
                    self.state = STATE_NORMAL
                    self.rebuild()


class BGRect(pygame.sprite.DirtySprite):
    def __init__(self, rect, layer, gui_group):
        super().__init__()
        self.rect = rect
        self.image = pygame.Surface(self.rect.size).convert()
        self.image.fill((20, 27, 27))
        self.layer = layer
        pygame.draw.rect(self.image, (74, 82, 112), ((0, 0), self.rect.size), 1)
        self.add(gui_group)
        self.dirty = 2

    def pass_event(self, event):
        pass


class ItemCallback:
    def __init__(self, player, rebuild_callback, item_name):
        self.player = player
        self.item_name = item_name
        item_data = ITEM_DATA.get(self.item_name, {})
        self.item_data = {
            **ITEM_DATA["default"],  # default item data
            **ITEM_DATA.get(
                item_data.get("type", "default"), {}
            ),  # default item data from item's type
            **item_data,  # item data
        }
        self.item_data["params"] = {
            **ITEM_DATA["default"].get("params", {}),  # default item data
            **ITEM_DATA.get(item_data.get("type", "default"), {}).get(
                "params", {}
            ),  # default item data from item's type
            **item_data.get("params", {}),  # item data
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
        self.player.poison(*hp_aftereffect)

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


def create_item_menu(player, engine, rebuild_callback):
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
            position += (padding, padding)
            yield item, amount, position
            index.x += 1
            if index.x >= rows:
                index.x = 0
                index.y += 1

    menu_rect = pygame.Rect((0, 0), engine.screen_size - (192, 128))
    menu_rect.center = engine.screen_size / 2
    gui = ItemGUIGroup()
    bg = BGRect(menu_rect, 1, gui)
    for name, amount, pos in get_item_button_data(player.items):
        ItemButton(
            name,
            amount,
            ItemCallback(player, rebuild_callback, name),
            pygame.Rect(pos + menu_rect.topleft, (32, 32)),
            2,
            gui,
        )

    return gui
