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


class ItemButton(pygame_gui.elements.UIButton):
    def __init__(self, pos, q):
        pass
