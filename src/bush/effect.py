import pygame

from bush import timer


# until https://github.com/pygame-community/pygame-ce/issues/1847 is implemented
# use python-zzy's workaround
def solid_overlay(surf, overlay_color=(0, 0, 0)):
    return pygame.mask.from_surface(surf).to_surface(
        setcolor=overlay_color, unsetcolor=(0, 0, 0, 0)
    )


class Effect:
    def __init__(self, duration):
        self.life_timer = timer.DTimer(duration)

    def apply(self, surface):
        if self.done():
            return surface.copy()
        else:
            return self._apply(surface)

    def _apply(self, surface):
        return surface.copy()

    def update(self, dt):
        self.life_timer.update(dt)

    def done(self):
        return self.life_timer.done()

    def reset(self):
        self.life_timer.reset()


class Flicker(Effect):
    def __init__(self, duration, delay=16):
        super().__init__(duration)
        self.switch_timer = timer.DTimer(delay)
        self.show = True

    def update(self, dt):
        super().update(dt)
        self.switch_timer.update(dt)

    def _apply(self, surface):
        if self.switch_timer.done():
            self.switch_timer.reset()
            self.show = not self.show

        surface = surface.copy()
        surface.set_alpha(surface.get_alpha() * self.show * 0.7)
        return surface


class Overlay(Effect):
    def __init__(self, duration, color="red"):
        super().__init__(duration)
        self.color = color

    def _apply(self, surface):
        return solid_overlay(surface, self.color)


class Blink(Effect):
    def __init__(self, duration, delay=16, color="red"):
        super().__init__(duration)
        self.switch_timer = timer.DTimer(delay)
        self.show = True
        self.color = color

    def update(self, dt):
        super().update(dt)
        self.switch_timer.update(dt)

    def _apply(self, surface):
        if self.switch_timer.done():
            self.switch_timer.reset()
            self.show = not self.show

        if self.show:
            return surface.copy()
        return solid_overlay(surface, self.color)
