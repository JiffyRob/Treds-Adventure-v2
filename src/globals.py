"""
This module houses global variables and services accessed by the entirety of the game
Do NOT add variables to this unless it falls under these criteria or is approved upon talking with other developers:
  1) Will be used in almost all parts of the codebase
  2) Would have to be piped through at least 4 interfaces to reach its destination
  3) Inherantly there should only be one of them

All variables here to be modified in the "global state setting" section of the main.Game.__init__() function
"""

player = None  # player object, to be phased out
engine = None


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
