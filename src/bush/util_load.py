import csv
import json
import os
import pickle
import zlib

import pygame

import pytmx

ENCODING = "UTF-8"

join = os.path.join


def load_image(path):
    return pygame.image.load(join(path))


def load_image_folder(path):
    img_extensions = "png", "jpg", "jpeg", "bmp"
    img_dict = {}
    for entry in os.scandir(join(path)):
        if entry.is_file():
            *fname, extension = entry.name.split(".")
            if extension in img_extensions:
                img_dict[".".join(fname)] = load_image(entry.path)
    return img_dict


def load_spritesheet(path, frame_size, margin=(0, 0), spacing=0):
    # load image
    spritesheet = load_image(path)
    return make_spritesheet(spritesheet, frame_size, margin, spacing)


def make_spritesheet(spritesheet, frame_size, margin=(0, 0), spacing=0):
    # try to optimize the surface for drawing on the screen
    try:
        spritesheet = spritesheet.convert_alpha()
    # will raise an error if there is no screen to optimize for
    # ignore it
    except pygame.error:
        print("alpha conversion not possible")
    # creation of variables
    surf_list = []
    width, height = spritesheet.get_size()
    x = margin[0]
    y = margin[1]
    # surface grabbing loop
    while True:
        if x + frame_size[0] > width:
            x = margin[0]
            y += frame_size[1] + spacing
        img_rect = pygame.Rect((x, y), frame_size)
        try:
            subsurf = spritesheet.subsurface(img_rect)
        except ValueError:
            break
        surf_list.append(subsurf)
        x += frame_size[0] + spacing
    return surf_list


def load_gzip(path):
    with open(path, "rb") as file:
        return json.loads(zlib.decompress(file.read()).decode("UTF-8"))


def save_gzip(data, path):
    with open(path, "wb") as file:
        file.write(zlib.compress(bytes(json.dumps(data), "UTF-8")))


def save_image(image, path, extension=".png"):
    return pygame.image.save(image, path, extension)


def load_audio(path):
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    return pygame.mixer.Sound(join(path))


def load_text(path):
    with open(join(path)) as file:
        return file.read()


def save_text(text, path):
    with open(join(path), "w") as file:
        file.write(text)


def load_json(path):
    with open(join(path)) as file:
        return json.load(file)


def save_json(data, path):
    with open(join(path), "w") as file:
        json.dump(data, file)


def load_csv(path, delimiter=",", quotechar='"', escapechar=""):
    grid = []
    with open(join(path)) as file:
        reader = csv.reader(
            file, delimiter=delimiter, quotechar=quotechar, escapechar=escapechar
        )
        for row in reader:
            grid.append(row)
    return grid


def save_csv(grid, path, delimiter=",", quotechar='"', escapechar=""):
    with open(join(path)) as file:
        writer = csv.writer(
            file, delimiter=delimiter, quotechar=quotechar, escapechar=escapechar
        )
        columns = [i for i in grid[0].keys()]
        writer.writerow(columns)
        for row in grid.values():
            writer.writerow(row)


def load_csv_simple(path, delimiter=","):
    grid = []
    with open(join(path)) as file:
        for item in file.read().split(delimiter):
            grid.append(item.strip())
    return grid


def save_csv_simple(data, path, delimiter=", "):
    string = delimiter.join(data)
    with open(join(path), "w") as file:
        file.write(string)


def load_pickle(path):
    with open(join(path), "rb") as file:
        return pickle.load(file)


def save_pickle(data, path):
    with open(join(path), "wb") as file:
        pickle.dump(data, file)


def load_pickle_secure(path):
    with open(join(path)) as file:
        return json.loads(pickle.load(file))


def save_pickle_secure(data, path):
    with open(join(path), "w") as file:
        pickle.dump(json.dumps(data), file)


def load_map(path):
    return pytmx.load_pygame(path)


def load_world(path):
    with open(join(path)) as file:
        world_data = json.loads(file.read())
    maps = world_data["maps"]
    export_data = {}
    for map_data in maps:
        map_path = join(os.path.dirname(path), map_data["fileName"])
        tmx_map = load_map(map_path)
        rect = (
            map_data["x"],
            map_data["y"],
            tmx_map.width * tmx_map.tilewidth,
            tmx_map.height * tmx_map.tileheight,
        )
        export_data[tmx_map.filename.split(".")[-2]] = rect, tmx_map
    return export_data
