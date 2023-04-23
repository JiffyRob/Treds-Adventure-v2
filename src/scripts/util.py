import pygame

from bush import sound_manager

music_player = sound_manager.music_player
sound_player = sound_manager.glob_player


def play_sound(sound_name):
    sound_player.play(sound_name)


def play_music(track_name, loops=-1):
    music_player.play(track_name, loops)
