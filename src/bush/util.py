"""
Bush util

Basic utility module
"""
import math
import queue
import random
import sys

import pygame

# Constants
QUEUE_EMPTY = "QUEUE_EMPTY"
METHOD_COUNTERCLOCKWISE = 0
METHOD_CLOCKWISE = 1
METHOD_X = 2
METHOD_Y = 3


def debug_view(img, scale=False):
    if isinstance(img, pygame.Mask):
        img = img.to_surface()
    screen = pygame.display.set_mode(img.get_size())
    if scale:
        screen = pygame.display.set_mode(img.get_size(), pygame.SCALED)
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


def sign(vec: pygame.Vector2):
    """return a tuple of 1s or 0s signed to vector values - eg < -8, 7> -> (-1, 1) or <0, 3> -> (0, 1)"""
    x = 0
    if vec.x:
        x = int(vec.x / abs(vec.x))
    y = 0
    if vec.y:
        y = int(vec.y / abs(vec.y))
    return x, y


def direction(vec: pygame.Vector2):
    """return a tuple of 1s or 0s rounded to match the direction of a vector"""
    x, y = 0, 0
    if vec:
        x, y = round(vec.normalize())
    return x, y


def direction_orthag(vec: pygame.Vector2):
    vec = vec.copy()
    index = 0
    if abs(vec.y) > abs(vec.x):
        index = 1
    vec[index - 1] = 0
    return sign(vec)


def string_direction(vec: pygame.Vector2):
    """return a string representing direction eg <1, 3> -> 'right_down' or <0, 0> -> 'still' or <0, 1> -> 'right'"""
    return {
        (0, -1): "up",
        (0, 1): "down",
        (-1, 0): "left",
        (1, 0): "right",
        (-1, -1): "left_up",
        (-1, 1): "left_down",
        (1, -1): "right_up",
        (1, 1): "right_down",
        (0, 0): "still",
    }[direction(vec)]


def round_string_direction(string, method=METHOD_X):
    def counter_clockwise(direc):
        return {
            "right_up": "up",
            "right_down": "right",
            "left_down": "down",
            "left_up": "left",
        }[direc]

    def clockwise(direc):
        return {
            "right_up": "right",
            "right_down": "down",
            "left_down": "left",
            "left_up": "up",
        }[direc]

    def x(direc):
        return direc.split("_")[0]

    def y(direc):
        return direc.split("_")[1]

    if "_" not in string:
        return string
    return (counter_clockwise, clockwise, x, y)[method](string)


def string_direction_to_vec(string):
    return {
        "up": pygame.Vector2(0, -1),
        "right_up": pygame.Vector2(1, -1),
        "right": pygame.Vector2(1, 0),
        "right_down": pygame.Vector2(1, 1),
        "down": pygame.Vector2(0, 1),
        "left_down": pygame.Vector2(-1, 1),
        "left": pygame.Vector2(-1, 0),
        "left_up": pygame.Vector2(-1, -1),
        "still": pygame.Vector2(),
    }[string]


def vec_abs(vec: pygame.Vector2):
    """return the 'absolute value' of the vector"""
    return pygame.Vector2(abs(vec.x), abs(vec.y))


def search(start: tuple | pygame.Vector2, dist: int | float = 1):
    """yields positions in a grid of spacing 'dist', in order of rough proximity to 'start'"""

    def neighbors(position: tuple[int]):
        return (
            (position[0], position[1] - 1),
            (position[0] + 1, position[1]),
            (position[0], position[1] + 1),
            (position[0] - 1, position[1]),
        )

    # breadth first search (https://www.redblobgames.com/pathfinding/a-star/introduction.html)
    frontier = queue.Queue()
    frontier.put(tuple(start))
    reached = set()
    reached.add(tuple(start))
    while True:
        current = frontier.get()
        for next in neighbors(current):
            if next not in reached:
                frontier.put(next)
                reached.add(next)
        yield current


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


def is_pygbag():
    return sys.platform == "emscripten"


def randincircle(length, outside=False):
    angle = random.random() * 2 * math.pi
    mult = 1 - (random.random() * outside)
    return pygame.Vector2(
        math.cos(angle) * length * mult, math.sin(angle) * length * mult
    )


def randinrect(rect):
    return pygame.Vector2(
        random.uniform(rect.left, rect.right), random.uniform(rect.top, rect.bottom)
    )


def repeat(image, size, alpha=False):
    if alpha:
        new_surface = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
    else:
        new_surface = pygame.Surface(size).convert()
        colorkey = image.get_colorkey()
        if colorkey is not None:
            new_surface.set_colorkey(colorkey)
    image_size = image.get_size()
    for x in range(0, size[0], image_size[0]):
        for y in range(0, size[1], image_size[1]):
            new_surface.blit(image, (x, y))
    return new_surface
