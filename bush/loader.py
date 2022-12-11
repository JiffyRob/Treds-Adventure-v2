import csv
import json
import os
import pickle

import pygame
import pytmx


def load_image(path):
    return pygame.image.load(os.path.join(path))


def save_image(image, path, extension=".png"):
    return pygame.image.save(image, path, extension)


def load_audio(path):
    return pygame.mixer.Sound(os.path.join(path))


def load_text(path):
    with open(os.path.join(path)) as file:
        return file.read()


def save_text(text, path):
    with open(os.path.join(path), "w") as file:
        file.write(text)


def load_json(path):
    with open(os.path.join(path)) as file:
        return json.load(file)


def save_json(data, path):
    with open(os.path.join(path)) as file:
        json.dump(data, file)


def load_csv(path, delimiter=",", quotechar='"', escapechar=""):
    grid = []
    with open(os.path.join(path)) as file:
        reader = csv.reader(
            file, delimiter=delimiter, quotechar=quotechar, escapechar=escapechar
        )
        for row in reader:
            grid.append(row)
    return grid


def save_csv(grid, path, delimiter=",", quotechar='"', escapechar=""):
    with open(os.path.join(path)) as file:
        writer = csv.writer(
            file, delimiter=delimiter, quotechar=quotechar, escapechar=escapechar
        )
        columns = [i for i in grid[0].keys()]
        writer.writerow(columns)
        for row in grid.values():
            writer.writerow(row)


def load_csv_simple(path, delimiter=","):
    grid = []
    with open(os.path.join(path)) as file:
        for item in file.read().split(delimiter):
            grid.append(item.strip())
    return grid


def save_csv_simple(data, path, delimiter=", "):
    string = delimiter.join(data)
    with open(os.path.join(path), "w") as file:
        file.write(string)


def load_pickle(path):
    with open(os.path.join(path)) as file:
        return pickle.load(file)


def save_pickle(data, path):
    with open(os.path.join(path), "w") as file:
        pickle.dump(data, file)


def load_pickle_secure(path):
    with open(os.path.join(path)) as file:
        return json.loads(pickle.load(file))


def save_pickle_secure(data, path):
    with open(os.path.join(path), "w") as file:
        pickle.dump(json.dumps(data), file)


def load_map(path):
    return pytmx.load_pygame(path)


class ResourceLoader:
    """
    A Loader of resources.  Catches things by filepath so that you don't have to load them again.
    """

    def __init__(self):
        self.image_cache = {}
        self.generic_cache = {}
        self.sound_cache = {}
        self.map_cache = {}
        self.data_cache = {}
        # file extension -> load function
        self.load_dict = {
            "png": load_image,
            "jpeg": load_image,
            "bmp": load_image,
            "wav": load_audio,
            "ogg": load_audio,
            "txt": load_text,
            "json": load_json,
            "csv": load_csv,
            "pkl": load_pickle,
            "tmx": load_map,
            "generic": load_text,
        }
        # file extension -> save function
        self.save_dict = {
            "png": save_image,
            "jpeg": save_image,
            "bmp": save_image,
            "txt": save_text,
            "json": save_json,
            "csv": save_csv,
            "pkl": save_pickle,
            "generic": save_text,
        }
        # file extension -> cache dictionary
        self.type_dict = {
            "png": self.image_cache,
            "jpeg": self.image_cache,
            "bmp": self.image_cache,
            "wav": self.sound_cache,
            "ogg": self.sound_cache,
            "txt": self.data_cache,
            "json": self.data_cache,
            "csv": self.data_cache,
            "pkl": self.data_cache,
            "tmx": self.map_cache,
            "generic": self.generic_cache,
        }

    def load(self, filepath, cache=True):
        # get file extension
        filetype = self.type_dict.get(filepath.split(".")[-1], "generic")
        if filetype == "generic":
            print(
                "WARNING: File extension",
                filetype,
                "not supported.  Loading as plain text.",
            )
        # see if file was cached, return that
        if filepath in self.type_dict[filetype]:
            return self.type_dict[filetype][filepath]
        # load file
        result = self.load_dict[filetype](filepath)
        # add to cache if needed
        if cache:
            self.type_dict[filetype][filepath] = result
        return result

    def save(self, data, path):
        filetype = path.split(".")[-1]
        self.save_dict.get(filetype, "generic")(data, path)


glob_loader = ResourceLoader()
