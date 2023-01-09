"""
Bush util

Basic utility module
"""
import pygame

# Constants
QUEUE_EMPTY = "QUEUE_EMPTY"


def debug_view(img):
    screen = pygame.display.set_mode(img.get_size())
    clock = pygame.time.Clock()
    running = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if not running:
            break
        screen.blit(img, (0, 0))
        pygame.display.update()
        clock.tick(60)
    pygame.quit()
    return img


def rvec(vec: pygame.Vector2):
    """return a list value of a vector, with both coordinates rounded"""
    return [round(vec.x), round(vec.y)]


def direction(vec: pygame.Vector2):
    """return a tuple of 1s signed to vector values - eg < -8, 7 > -> (-1, 1)"""
    return vec.x / abs(vec.x), vec.y / abs(vec.y)


def vec_abs(vec: pygame.Vector2):
    """return the 'absolute value' of the vector"""
    return pygame.Vector2(abs(vec.x).abs(vec.y))


def circle_surf(radius, color, width=0):
    """Return a pygame surface of a circle"""
    surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(surface, color, (radius, radius), radius, width=width)
    return surface


def rect_surf(rect, color, width=0):
    """Return a pygame surface of a rect"""
    rect = pygame.Rect(rect)
    rect.topleft = (0, 0)
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(surface, color, rect, width=width)
    return surface


class IDHandler:
    """
    Simple class for generating and returning numerical ids
    """

    def __init__(self, start: int = 0):
        self._current_id = start - 1

    def get_next(self):
        """Get next ID"""
        self._current_id += 1
        return self._current_id

    def reset(self, start: int):
        """Reset counter back to start"""
        self._current_id = start - 1


class FifoQueue:
    """
    Simple FIFO Queue to cut down on dependencies
    """

    def __init__(self):
        self._list = []

    def add(self, thing):
        self._list.append(thing)

    def pop(self, thing):
        if self._list:
            return self._list.pop(0)
        return QUEUE_EMPTY
