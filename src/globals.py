"""
This module houses global variables and services accessed by the entirety of the game
Do NOT add variables to this unless it falls under these criteria or is approved upon talking with other developers:
  1) Will be used in almost all parts of the codebase
  2) Would have to be piped through at least 4 interfaces to reach its destination
  3) Inherantly there should only be one of them

The variables contained should ONLY be modified by the main.Game class, and even then only sparingly
"""

engine = None  # game engine, set by the Engine object upon running the game
map_registry = None  # representation of the world map, set by the Engine object upon loading a new map
player = None  # player sprite, set by the engine upon loading a new map
event_list = []  # list of pygame events, set every frame by the engine


def play_sound(sound_id):
    ...  # TODO


def switch_music(new_track):
    ...  # TODO


def spawn_particles(frames, positions, velocities):
    ...  # TODO


def camera_shake(value, time):
    ...  # TODO


def get_terrain(mask, offset):
    ...  # TODO


def find_sprites(group, id=None):
    ...  # TODO


def spawn_sprite(sprite):
    ...  # TODO


def show_dialog(self):
    ...  # TODO
