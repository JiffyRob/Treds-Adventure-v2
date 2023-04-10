import pygame
import pygame_gui

import menu
from bush import util, util_load

pygame.font.init()
ITEM_DATA = util_load.load_json("resources/data/items.json")
ITEM_IMAGES = dict(
    zip(
        ITEM_DATA.pop("image-order"),
        util_load.load_spritesheet("resources/hud/items.png", (16, 16)),
    )
)
NUMBER_FONT = pygame.font.Font("resources/hud/TeenyTinyPixls.ttf", 5)


def create_item_menu(items, engine):
    gui = pygame_gui.UIManager(engine.screen_size)
    padding = 3
    index = pygame.Vector2()
    item_surface = pygame.Surface(engine.screen_size - (192, 64)).convert()
    item_surface.fill((255, 255, 0))
    item_surface.set_colorkey((255, 255, 0))
    bg_surface = item_surface.copy()
    bg_surface.fill((78, 72, 74))
    menu_rect = item_surface.get_rect(center=engine.screen_size / 2)
    pygame_gui.elements.UIImage(menu_rect, bg_surface, gui)
    button_dict = {}
    for name, amount in items.items():
        img = pygame.transform.scale(ITEM_IMAGES[name], (32, 32))
        relative_pos = index.elementwise() * (32 + padding, 32 + padding)
        rect = pygame.Rect(relative_pos + menu_rect.topleft, (32, 32))
        button_dict[name] = pygame_gui.elements.UIButton(
            rect,
            "",
            gui,
            object_id=pygame_gui.core.ObjectID(
                class_id="@item_button", object_id=f"#item_button"
            ),
        )
        item_surface.blit(img, relative_pos)
        index.x += 1
        if index.x >= 6:
            index.x = 0
            index.y += 1
    pygame_gui.elements.UIImage(menu_rect, item_surface, gui)
    return gui, button_dict
