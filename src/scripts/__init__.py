from scripts import base, random_walk

scripts = {
    "base-map": base.Script,
    "base-entity": base.EntityScript,
    "random-walk": random_walk.RandomWalkScript,
}


def get_script(name):
    return scripts.get(name, None)
