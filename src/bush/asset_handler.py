import gc

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
        loader = loader or self.load_dict[filetype]
        result = loader(filepath, **kwargs)
        # add to cache if needed
        if cache:
            self.type_dict[filetype][filepath] = result
        return result

    def save(self, data, path):
        filetype = path.split(".")[-1]
        self.save_dict.get(filetype, "generic")(data, os.path.join(self.base, path))

    def empty(self):
        for key in self.type_dict.keys():
            self.type_dict[key] = {}
        gc.collect()


glob_loader = AssetHandler()
