import pygame

from bush import util_load

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

UI_FONT = pygame.font.Font("resources/hud/silver.ttf")

NUMBER_FONT = pygame.font.Font("resources/hud/TeenyTinyPixls.ttf", 5)

STATE_NORMAL = 0
STATE_HOVERED = 1
STATE_CLICKED = 2


class UIGroup(pygame.sprite.LayeredDirty):
    def draw_ui(self, surface):
        self.draw(surface)

    def process_events(self, event):
        for sprite in self.sprites():
            if sprite.pass_event(event):
                break


class UIElement(pygame.sprite.DirtySprite):
    def __init__(self, rect, layer, group):
        super().__init__()
        self.rect = rect
        self.layer = layer
        self.add(group)  # have to add to group after setting layer
        self.image = pygame.Surface(self.rect.size).convert()
        self.image.set_colorkey((0, 0, 0))
        self.dirty = 2  # dirty sprite function not currently implemented

    def pass_event(self, event):
        pass

    def rebuild(self):
        pass

    def update(self, dt):
        pass


class BGRect(UIElement):
    def __init__(self, rect, layer, group):
        super().__init__(rect, layer, group)
        self.image = pygame.Surface(self.rect.size).convert()
        self.image.fill((20, 27, 27))
        pygame.draw.rect(self.image, (74, 82, 112), ((0, 0), self.rect.size), 1)


class Descriptionbox(UIElement):
    def __init__(self, rect, layer, group):
        super().__init__(rect, layer, group)
        self.text = ""
        self.last_text = None
        self.rebuild()

    def set_text(self, text):
        self.text = text
        self.rebuild()

    def pass_event(self, event):
        pass

    def rebuild(self):
        self.image.fill((0, 0, 0))
        pygame.draw.rect(self.image, (74, 82, 112), ((0, 0), self.rect.size), 1)
        text_surface = UI_FONT.render(
            self.text, False, (242, 234, 241), (20, 27, 27), self.rect.width - 2
        )
        self.image.blit(text_surface, (1, 1))
        self.last_text = self.text


class ItemButton(UIElement):
    def __init__(
        self, item_name, item_count, on_click, description_box, rect, layer, group
    ):
        super().__init__(rect, layer, group)
        self.name = item_name
        self.count = item_count
        self.on_click = on_click
        self.description_box = description_box
        # the bug net is not implemented (as of writing this comment), so it will be the debug item image
        self.item_image = pygame.transform.scale(
            ITEM_IMAGES.get(self.name, "bug net"), self.rect.size
        )
        self.count_image = NUMBER_FONT.render(str(self.count), False, (242, 234, 241))
        self.state = STATE_NORMAL
        self.bg_images = [pygame.transform.scale(i, self.rect.size) for i in BG_IMAGES]
        self.image = None
        self.rebuild()

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
                    self.description_box.set_text(self.name)
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
