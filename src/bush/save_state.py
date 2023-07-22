from bush import asset_handler


class GameState:
    def __init__(
        self,
        save_directory,
        save_hook=lambda to_save_state: to_save_state,
        load_hook=lambda loaded_state: None,
    ):
        self.loader = asset_handler.AssetHandler(save_directory)
        self.save_hook = save_hook
        self.load_hook = load_hook
        self.data = {}

    def load(self, file_path):
        self.data = self.loader.load(file_path)
        self.load_hook(self)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value

    def save(self, file_path):
        self.save_hook(self)
        self.loader.save(file_path, self.data)


class LeveledGameState:
    def __init__(
        self,
        save_directory,
        default_level,
        save_hook=lambda to_save_state: to_save_state,
        load_hook=lambda loaded_state: loaded_state,
        save_path=None,
    ):
        self.loader = asset_handler.AssetHandler(save_directory)
        self.data = {}
        self.default_level = default_level
        self.save_path = save_path
        self.save_hook = save_hook
        self.load_hook = load_hook

    def get(self, key, level=None, default=None):
        if level is None:
            return self.data.get(key, default)
        if level in self.data:
            return self.data[level].get(key, default)
        if self.default_level in self.data:
            return self.data[self.default_level].get(key, default)
        return default

    def set(self, key, value, level=None):
        if level is None:
            self.data[key] = value
        elif level in self.data:
            self.data[level][key] = value
        else:
            self.data[level] = {key: value}

    def load(self, file_path=None):
        file_path = file_path or self.save_path
        self.save_path = file_path
        self.data = self.loader.load(file_path)
        self.load_hook(self)

    def save(self, file_path=None):
        print(file_path)
        self.save_hook(self)
        file_path = file_path or self.save_path
        self.loader.save(self.data, file_path)
