import pygame
import pygame_gui


def create_menu(menu_name, button_names, screen_size):
    menu = pygame_gui.UIManager(screen_size, theme_path="data/ui_theme.json")
    container_rect = pygame.Rect(
        (0, 0),
        (screen_size.x * 0.4, screen_size.y - 160),
    )
    container_rect.center = screen_size / 2
    container = pygame_gui.elements.UIPanel(container_rect, 3, menu)
    rect = pygame.Rect(0, 10, 100, 50)
    rect.centerx = container_rect.width / 2
    pygame_gui.elements.UILabel(rect, menu_name, menu, container)
    for i, button_name in enumerate(button_names):
        rect = pygame.Rect((0, (i + 1) * 55 + 10, 100, 50))
        rect.centerx = container_rect.width / 2
        pygame_gui.elements.UIButton(rect, button_name, menu, container)
    return menu
