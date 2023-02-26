from bush import asset_handler


class GameState:
    def __init__(self, save_directory):
        self.loader = asset_handler.AssetHandler(save_directory)
        self.data = {}

    def load(self, file_path):
        self.data = self.loader.load(file_path)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value

    def save(self, file_path):
        self.loader.save(file_path, self.data)


class LeveledGameState:
    def __init__(self, save_directory, default_level, save_path=None):
        self.loader = asset_handler.AssetHandler(save_directory)
        self.data = {}
        self.default_level = default_level
        self.save_path = save_path

    def get(self, key, level=None, default=None):
        if level is None:
            return self.data.get(key, default)
        return self.data.get(level, self.data[self.default_level]).get(key, default)

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

    def save(self, file_path=None):
        file_path = file_path or self.save_path
        self.loader.save(file_path, self.data)
