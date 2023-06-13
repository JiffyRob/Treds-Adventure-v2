import gc
import os.path

from bush.util_load import *


class AssetHandler:
    """
    A Loader of resources.  Catches things by filepath so that you don't have to load them again.
    """

    def __init__(self, default_directory=""):
        image_cache = {}
        generic_cache = {}
        sound_cache = {}
        map_cache = {}
        world_cache = {}
        data_cache = {}
        # file extension -> load function
        self.load_dict = {
            "png": load_image,
            "jpeg": load_image,
            "jpg": load_image,
            "bmp": load_image,
            "wav": load_audio,
            "ogg": load_audio,
            "txt": load_text,
            "json": load_json,
            "csv": load_csv,
            "pkl": load_pickle,
            "tmx": load_map,
            "world": load_world,
            "gz": load_gzip,
            "sav": load_gzip,
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
            "gz": load_gzip,
            "sav": save_gzip,
            "generic": save_text,
        }
        # file extension -> cache dictionary
        self.type_dict = {
            "png": image_cache,
            "jpeg": image_cache,
            "bmp": image_cache,
            "wav": sound_cache,
            "ogg": sound_cache,
            "txt": data_cache,
            "json": data_cache,
            "csv": data_cache,
            "pkl": data_cache,
            "gz": data_cache,
            "sav": data_cache,
            "tmx": map_cache,
            "world": world_cache,
            "generic": generic_cache,
        }
        self.base = os.path.join(default_directory)

    def cache_folder(self, path=None):
        if path is None:
            path = self.base
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if filename.split(".")[-1] in self.load_dict:
                    file_path = join(dirpath, filename)
                    file_path = os.path.relpath(file_path, self.base)
                    self.load(file_path)

    def cache_asset_handler(self, other):
        for key, value in other.type_dict.items():
            for path, resource in value.items():
                filedir, filename = os.path.split(path)
                filepath = join(filedir, filename)
                if (
                    os.path.commonpath({filedir, self.base}) == self.base
                    and filepath not in self.type_dict[key]
                ):
                    self.type_dict[key][filepath] = resource
                    print("caching", filepath)

    def set_home(self, path):
        self.base = os.path.join(path)

    def load(self, filepath, cache=True, loader=None, **kwargs):
        filepath = os.path.join(self.base, filepath)
        # get file extension
        filetype = filepath.split(".")[-1]
        if filetype == "generic":
            print(
                "WARNING: File extension",
                filetype,
                "not known to loader.  Loading as plain text.",
            )
        # see if file was cached, return that
        if filepath in self.type_dict[filetype]:
            return self.type_dict[filetype][filepath]
        # load file
        print("loading", filepath)
        loader = loader or self.load_dict[filetype]
        result = loader(filepath, **kwargs)
        # add to cache if needed
        if cache:
            self.type_dict[filetype][filepath] = result
        return result

    def load_spritesheet(self, path, size=(16, 16), margin=(0, 0), spacing=0):
        image = self.load(path)
        return make_spritesheet(image, size, margin, spacing)

    def save(self, data, path):
        filetype = path.split(".")[-1]
        self.save_dict.get(filetype, "generic")(data, os.path.join(self.base, path))

    def empty(self):
        for key in self.type_dict.keys():
            self.type_dict[key] = {}
        gc.collect()


glob_loader = AssetHandler()
