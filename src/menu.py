import math

import pygame
import pygame_gui
from pygame_gui.core.drawable_shapes import RectDrawableShape, RoundedRectangleShape
from pygame_gui.core.utility import basic_blit

import gui
from bush import event_binding, timer

THEME_PATH = "resources/data/ui_theme.json"


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


class Dialog(pygame_gui.elements.UITextBox):
    STATE_WRITING_PROMPT = 0
    STATE_GETTING_ANSWER = 2
    STATE_COMPLETE = 3

    def __init__(
        self,
        html_prompt,
        html_choices,
        on_kill,
        relative_rect,
        manager,
        *args,
        **kwargs,
    ):
        self.prompt = html_prompt
        self.word_queue = self.prompt.split(" ")
        self.prompt_so_far = ""
        self.choices = html_choices
        self.answer_index = 0
        self.chosen_index = None
        self.state = self.STATE_WRITING_PROMPT
        self.on_kill = on_kill
        self.kill_timer = timer.Timer()
        self.add_letter_timer = timer.Timer(20, self.add_letter, True)
        super().__init__("", relative_rect, manager, *args, **kwargs)
        self.line_spacing = 0.75
        self.update_html()

    def add_letter(self):
        if not self.prompt:
            self.state = self.STATE_GETTING_ANSWER
            self.update_html()
            if not self.choices:
                self.kill_timer = timer.Timer(1500, self.choose)
                self.state = self.STATE_COMPLETE
            self.add_letter_timer = timer.Timer()
        else:
            self.prompt_so_far += self.prompt[0]
            self.prompt = self.prompt[1:]
            self.update_html()

    def rebuild(self):
        """
        Rebuild whatever needs building. (Modified to automatically scroll to the bottom)
        """
        if self.scroll_bar is not None:
            self.scroll_bar.kill()
            self.scroll_bar = None

        # The text_wrap_area is the part of the text box that we try to keep the text inside
        # of so that none  of it overlaps. Essentially we start with the containing box,
        # subtract the border, then subtract the padding, then if necessary subtract the width
        # of the scroll bar
        self.rounded_corner_offset = int(
            self.shape_corner_radius
            - (math.sin(math.pi / 4) * self.shape_corner_radius)
        )
        self.text_wrap_rect = pygame.Rect(
            (
                self.rect[0]
                + self.padding[0]
                + self.border_width
                + self.shadow_width
                + self.rounded_corner_offset
            ),
            (
                self.rect[1]
                + self.padding[1]
                + self.border_width
                + self.shadow_width
                + self.rounded_corner_offset
            ),
            max(
                1,
                (
                    self.rect[2]
                    - (self.padding[0] * 2)
                    - (self.border_width * 2)
                    - (self.shadow_width * 2)
                    - (2 * self.rounded_corner_offset)
                ),
            ),
            max(
                1,
                (
                    self.rect[3]
                    - (self.padding[1] * 2)
                    - (self.border_width * 2)
                    - (self.shadow_width * 2)
                    - (2 * self.rounded_corner_offset)
                ),
            ),
        )
        if self.wrap_to_height or self.rect[3] == -1:
            self.text_wrap_rect.height = -1
        if self.rect[2] == -1:
            self.text_wrap_rect.width = -1

        drawable_area_size = (self.text_wrap_rect[2], self.text_wrap_rect[3])

        # This gives us the height of the text at the 'width' of the text_wrap_area
        self.parse_html_into_style_data()
        if self.text_box_layout is not None:
            if self.wrap_to_height or self.rect[3] == -1 or self.rect[2] == -1:
                final_text_area_size = self.text_box_layout.layout_rect.size
                new_dimensions = (
                    (
                        final_text_area_size[0]
                        + (self.padding[0] * 2)
                        + (self.border_width * 2)
                        + (self.shadow_width * 2)
                        + (2 * self.rounded_corner_offset)
                    ),
                    (
                        final_text_area_size[1]
                        + (self.padding[1] * 2)
                        + (self.border_width * 2)
                        + (self.shadow_width * 2)
                        + (2 * self.rounded_corner_offset)
                    ),
                )
                self.set_dimensions(new_dimensions)

                # need to regen this because it was dynamically generated
                drawable_area_size = (
                    max(
                        1,
                        (
                            self.rect[2]
                            - (self.padding[0] * 2)
                            - (self.border_width * 2)
                            - (self.shadow_width * 2)
                            - (2 * self.rounded_corner_offset)
                        ),
                    ),
                    max(
                        1,
                        (
                            self.rect[3]
                            - (self.padding[1] * 2)
                            - (self.border_width * 2)
                            - (self.shadow_width * 2)
                            - (2 * self.rounded_corner_offset)
                        ),
                    ),
                )

        theming_parameters = {
            "normal_bg": self.background_colour,
            "normal_border": self.border_colour,
            "border_width": self.border_width,
            "shadow_width": self.shadow_width,
            "shape_corner_radius": self.shape_corner_radius,
        }

        if self.shape == "rectangle":
            self.drawable_shape = RectDrawableShape(
                self.rect, theming_parameters, ["normal"], self.ui_manager
            )
        elif self.shape == "rounded_rectangle":
            self.drawable_shape = RoundedRectangleShape(
                self.rect, theming_parameters, ["normal"], self.ui_manager
            )

        self.background_surf = self.drawable_shape.get_fresh_surface()

        if self.rect.width <= 0 or self.rect.height <= 0:
            return

        drawable_area = pygame.Rect((0, 0), drawable_area_size)
        drawable_area.bottom = self.text_box_layout.layout_rect.height
        new_image = pygame.surface.Surface(
            self.rect.size, flags=pygame.SRCALPHA, depth=32
        )
        new_image.fill(pygame.Color(0, 0, 0, 0))
        basic_blit(new_image, self.background_surf, (0, 0))

        basic_blit(
            new_image,
            self.text_box_layout.finalised_surface,
            (
                self.padding[0]
                + self.border_width
                + self.shadow_width
                + self.rounded_corner_offset,
                self.padding[1]
                + self.border_width
                + self.shadow_width
                + self.rounded_corner_offset,
            ),
            drawable_area,
        )

        self._set_image(new_image)
        self.link_hover_chunks = []
        self.text_box_layout.add_chunks_to_hover_group(self.link_hover_chunks)

        self.should_trigger_full_rebuild = False
        self.full_rebuild_countdown = self.time_until_full_rebuild_after_changing_size

    def update_html(self):
        self.html_text = self.get_html_text()
        self.rebuild()

    def get_html_text(self):
        text = self.prompt_so_far
        # add all of the choices
        if self.state == self.STATE_GETTING_ANSWER:
            for i, choice in enumerate(self.choices):
                text += "\n"
                if i == self.answer_index:
                    # put a dash before selected answer
                    text += f"-<u>{choice}</u>"
                else:
                    text += f" {choice}"
        return text

    def process_event(self, event: pygame.event.Event):
        if not super().process_event(event):
            if self.state == self.STATE_GETTING_ANSWER:
                if event.type == event_binding.BOUND_EVENT:
                    if event.name == "dialog pointer up":
                        self.answer_index = max(self.answer_index - 1, 0)
                        self.update_html()
                    if event.name == "dialog pointer down":
                        self.answer_index = min(
                            self.answer_index + 1, len(self.choices) - 1
                        )
                        self.update_html()
                    if event.name == "dialog select":
                        self.choose()
            if self.state == self.STATE_COMPLETE and not self.choices:
                if event.type == event_binding.BOUND_EVENT:
                    if event.name == "dialog select":
                        self.choose()

    def choose(self):
        print("chosen")
        self.chosen_index = self.answer_index
        self.state = self.STATE_COMPLETE
        self.kill()
        self.on_kill(self.get_answer())

    def get_answer(self):
        if not self.choices or self.chosen_index is None:
            return None
        return self.choices[self.chosen_index]

    def update(self, time_delta: float):
        super().update(time_delta)
        self.kill_timer.update()
        self.add_letter_timer.update()


def create_menu(
    menu_name,
    button_names,
    button_functions,
    screen_size,
    return_container=False,
    return_skipped=False,
):
    menu = gui.UIGroup()
    container_rect = pygame.Rect(
        (0, 0),
        (screen_size.x * 0.4, screen_size.y * 0.7),
    )
    container_rect.center = screen_size / 2
    container = gui.BGRect(container_rect, 1, menu)
    height = 30
    rect = pygame.Rect(0, 10, 100, height)
    rect.centerx = container_rect.width / 2
    # pygame_gui.elements.UILabel(rect, menu_name, menu, container)
    skipped = []
    for i, button_name, on_click in zip(
        range(len(button_names)), button_names, button_functions
    ):
        rect = pygame.Rect((0, (i + 1) * (height + 2) + 10, 100, 30))
        rect.centerx = container_rect.width / 2
        rect.topleft += pygame.Vector2(container_rect.topleft)
        if button_name == ":SKIP":
            skipped.append(rect)
            continue
        gui.Button(button_name, on_click, rect, 2, menu)
    return_values = [menu]
    if return_container:
        return_values.append(container)
    if return_skipped:
        return_values.append(skipped)
    if len(return_values) == 1:
        return return_values[0]
    return return_values


def get_dialog_rect(screen_size):
    rect = pygame.Rect(0, 0, screen_size.x * 0.75, screen_size.y * 0.3)
    rect.bottom = screen_size.y - 4
    rect.centerx = screen_size.x // 2
    return rect
