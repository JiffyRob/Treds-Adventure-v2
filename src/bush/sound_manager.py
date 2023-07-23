import pygame

from bush import asset_handler, util_load


class SoundHandler:
    def __init__(self, sounds=None, load_callback=util_load.load_audio):
        self.sounds = {}
        if sounds is not None:
            for key, sound in sounds:
                if isinstance(sound, str):
                    self.load(key)
                else:
                    self.sounds[key] = sound
        self.load_callback = load_callback

    def load(self, path):
        sound = self.load_callback(path)
        self.sounds[path] = sound
        return sound

    def delete(self, path):
        self.sounds.pop(path, None)

    def get(self, path):
        return self.sounds.get(path, self.load(path))

    def play(self, name):
        self.get(name).play()

    def stop(self, name=None):
        if name is None:
            for sound in self.sounds.values():
                sound.stop()
        elif name in self.sounds:
            self.sounds[name].stop()


class _MusicPlayer:
    def __init__(self, tracks=None):
        if tracks is None:
            tracks = {}
        self.tracks = tracks
        self.paused = False
        self.current_track = None

    def add_track(self, name, path):
        self.tracks[name] = path

    def add_tracks(self, track_dict):
        for key, value in track_dict.items():
            self.add_track(key, value)

    def remove_track(self, name):
        self.tracks.pop(name, None)

    def play(self, track, loops=-1):
        pygame.mixer.music.load(self.tracks[track])
        pygame.mixer.music.play(loops)
        self.current_track = self.tracks[track]

    def stop(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        self.current_track = None
        self.paused = False

    def pause(self):
        pygame.mixer.music.pause()
        self.paused = True

    def unpause(self):
        pygame.mixer.music.unpause()
        self.paused = False

    def rewind(self, preserve_pause=True):
        pygame.mixer.music.play(self.tracks[self.current_track])
        if self.paused and preserve_pause:
            pygame.mixer.music.pause()
        else:
            self.paused = False

    def queue(self, track):
        pygame.mixer.music.queue(self.tracks[track])

    @property
    def volume(self):
        return pygame.mixer.music.get_volume()

    @volume.setter
    def volume(self, volume):
        return pygame.mixer.music.set_volume(volume)

    def get_metadata(self, track=None):
        if track is None:
            track = self.current_track
        if track is None:
            track = "all"
        if track == "all":
            output = {}
            for name, path in self.tracks.items():
                output[name] = pygame.mixer.music.get_metadata(path)
            return output
        return pygame.mixer.music.get_metadata(self.tracks[track])


glob_player = SoundHandler(load_callback=asset_handler.glob_loader.load)
music_player = _MusicPlayer()
