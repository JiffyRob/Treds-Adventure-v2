import pygame

from bush import util_load


def set_channel_count(num):
    pygame.mixer.set_num_channels(num)


class AudioPlayer:
    def __init__(
        self,
        audio=None,
        load_callback=util_load.load_audio,
        default_fadein=0,
        default_fadeout=500,
        default_looping=0,
        default_unload=True,
    ):
        audio = audio or {}
        self.audio = {}
        self.default_fadein = default_fadein
        self.default_fadeout = default_fadeout
        self.default_looping = default_looping
        self.default_unload = default_unload
        self.current_track = None
        self.paused = False
        for key, sound in audio.items():
            if isinstance(sound, str):
                sound = load_callback(sound)
            self.audio[key] = sound

    def get_sound(self, key):
        return self.audio[key]

    @staticmethod
    def set_channel_count(num):
        set_channel_count(num)

    def play(self, sound):
        self.audio[sound].play()

    def switch_music(self, track, loops=None, fadeout=None, fadein=None):
        self.stop_music(fadeout)
        self.play_music(track, loops, fadein)

    def play_music(self, track, loops=None, fadein=None):
        if fadein is None:
            fadein = self.default_fadein
        if loops is None:
            loops = self.default_looping
        pygame.mixer.music.load(self.audio[track])
        pygame.mixer.music.play(loops, fade_ms=fadein)
        self.current_track = track

    def pause_music(self):
        self.paused = True
        pygame.mixer.music.pause()

    def unpause_music(self):
        self.paused = False
        pygame.mixer.music.unpause()

    def queue_music(self, track):
        pygame.mixer.music.queue(self.audio[track])

    def restart_music(self, preserve_paused=False):
        self.play_music(self.current_track)
        if self.paused and preserve_paused:
            self.pause_music()
        else:
            self.paused = False

    def stop_music(self, fadeout=None, unload=None):
        if unload is None:
            unload = self.default_unload
        if fadeout is None:
            fadeout = self.default_fadeout
        if fadeout:
            pygame.mixer.music.fadeout(fadeout)
        else:
            pygame.mixer.music.stop()
        if unload:
            self.unload_music()
        self.current_track = None

    def unload_music(self):
        pygame.mixer.music.unload()

    def stop_sound(self, sound=None):
        if sound is None:
            for sound in self.audio.values():
                sound.stop()
            return
        self.audio[sound].stop()

    def stop_all(self):
        self.stop_music()
        self.stop_sound()
