import csv
import json
import os
import pickle

import pygame


def load_image(path):
    print("loading", path)
    return pygame.image.load(os.path.join(path))


def save_image(image, path, extension=".png"):
    return pygame.image.save(image, path, extension)


def load_audio(path):
    if not pygame.mixer.get_init():
        pygame.mixer.init()
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
