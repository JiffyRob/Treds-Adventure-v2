import pygame
import pygame_gui


def create_menu(menu_name, button_names, screen_size):
    menu = pygame_gui.UIManager(screen_size)
    menu.add_font_paths("silver", "resources/misc/silver.ttf")
    menu.preload_fonts(["silver"])
    rect = pygame.Rect(0, 100, 100, 50)
    rect.centerx = screen_size[0] / 2
    pygame_gui.elements.UILabel(rect, menu_name, menu)
    for i, button_name in enumerate(button_names):
        rect = pygame.Rect((0, (i + 1) * 55 + 100, 100, 50))
        rect.centerx = screen_size[0] / 2
        button = pygame_gui.elements.UIButton(rect, button_name, menu)
    return menu
