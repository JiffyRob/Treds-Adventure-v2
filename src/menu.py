import math

import pygame
import pygame_gui
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape
from pygame_gui.core.utility import basic_blit

from bush import event_binding

THEME_PATH = "resources/data/ui_theme.json"
SK_RETURN = "⒅"  # used for end of prompt


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


class ChoiceBox(pygame_gui.elements.UITextBox):
    def __init__(
        self, html_prompt, html_choices, relative_rect, manager, *args, **kwargs
    ):
        self.prompt = html_prompt
        self.choices = html_choices
        self.answer_index = 0
        self.chosen_index = None
        self.prompt_done = False
        self.needs_advanced = False
        super().__init__(self.get_html_text(), relative_rect, manager, *args, **kwargs)
        self.set_active_effect(pygame_gui.TEXT_EFFECT_TYPING_APPEAR)
        self.line_spacing = 0.75
        self.rebuild()

    def advance(self):
        self.needs_advanced = False
        if self.prompt in self.html_text:
            self.prompt_done = True

    def rebuild(self):
        super().rebuild()
        if self.scroll_bar is not None:
            # self.scroll_bar.set_scroll_from_start_percentage(1)
            self.needs_advanced = True
            self.scroll_bar.hide()
            if self.html_text[-1] != SK_RETURN:
                self.update_html()

    def update_html(self):
        self.html_text = self.get_html_text()
        self.rebuild()

    def get_html_text(self):
        # apply text effect to prompt
        text = (
            f"<effect id={pygame_gui.TEXT_EFFECT_TYPING_APPEAR}>{self.prompt}</effect>"
        )
        # add all of the choices
        if self.prompt_done:
            for i, choice in enumerate(self.choices):
                text += "\n"
                if i == self.answer_index:
                    # put a dash before selected answer
                    text += f"-<u>{choice}</u>"
                else:
                    text += f" {choice}"
        if self.needs_advanced:
            text += SK_RETURN
        return text

    def process_event(self, event: pygame.event.Event):
        if not super().process_event(event):
            if event.type == event_binding.BOUND_EVENT:
                print(event.name)
                if event.name == "choice pointer up" and self.prompt_done:
                    self.answer_index = max(self.answer_index - 1, 0)
                    self.update_html()
                if event.name == "choice pointer down" and self.prompt_done:
                    self.answer_index = min(
                        self.answer_index + 1, len(self.choices) - 1
                    )
                    self.update_html()
                if event.name == "choice picked":
                    self.choose()
                if event.name == "dialog advance" and self.needs_advanced:
                    self.advance()
            if event.type == pygame_gui.UI_TEXT_EFFECT_FINISHED:
                if event.ui_element is self:
                    self.needs_advanced = True
                    self.update_html()

    def choose(self):
        self.kill()
        self.chosen_index = self.answer_index

    def get_answer(self):
        if self.chosen_index is None:
            return None
        return self.choices[self.chosen_index]


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
