import math

import pygame
import pygame_gui

THEME_PATH = "data/ui_theme.json"


class HeartMeter(pygame_gui.elements.UIImage):
    def __init__(
        self,
        relative_rect,
        heart_images,
        sprite_to_monitor,
        manager=None,
        image_is_alpha_premultiplied=False,
        container=None,
        parent_element=None,
        object_id=None,
        anchors=None,
        visible=1,
    ):
        self.heart_images = heart_images
        self.sprite_to_monitor = sprite_to_monitor
        self.heart_size = pygame.Vector2(self.heart_images[0].get_size())
        surface = self.get_image()
        relative_rect.size = surface.get_size()
        super().__init__(
            relative_rect,
            surface,
            manager,
            image_is_alpha_premultiplied,
            container,
            parent_element,
            object_id,
            anchors,
            visible,
        )

    def get_image(self):
        heart_count = math.ceil(
            self.sprite_to_monitor.health_capacity / len(self.heart_images)
        )
        surface = pygame.Surface(
            self.heart_size.elementwise() * (heart_count, 1), pygame.SRCALPHA
        )
        health_consumed = 0
        for i in range(heart_count):
            heart_index = min(
                self.sprite_to_monitor.health_capacity - health_consumed,
                len(self.heart_images) - 1,
            )
            surface.blit(self.heart_images[heart_index], (i * self.heart_size.y, 0))
        return surface

    def update(self, time_delta):
        surface = self.get_image()
        size = surface.get_size()
        self.set_dimensions(size)
        self.set_image(surface)
        super().update(time_delta)


def create_menu(
    menu_name, button_names, screen_size, return_container=False, return_skipped=False
):
    menu = pygame_gui.UIManager(screen_size, theme_path=THEME_PATH)
    container_rect = pygame.Rect(
        (0, 0),
        (screen_size.x * 0.4, screen_size.y * 0.7),
    )
    container_rect.center = screen_size / 2
    container = pygame_gui.elements.UIPanel(container_rect, 3, menu)
    height = 30
    rect = pygame.Rect(0, 10, 100, height)
    rect.centerx = container_rect.width / 2
    pygame_gui.elements.UILabel(rect, menu_name, menu, container)
    skipped = []
    for i, button_name in enumerate(button_names):
        rect = pygame.Rect((0, (i + 1) * (height + 2) + 10, 100, 30))
        rect.centerx = container_rect.width / 2
        if button_name == ":SKIP":
            skipped.append(rect)
            continue
        pygame_gui.elements.UIButton(
            rect,
            button_name,
            menu,
            container,
            generate_click_events_from=(pygame.BUTTON_LEFT, pygame.BUTTON_RIGHT),
        )
    return_values = [menu]
    if return_container:
        return_values.append(container)
    if return_skipped:
        return_values.append(skipped)
    if len(return_values) == 1:
        return return_values[0]
    return return_values
