from scripts import base, random_walk, test

scripts = {
    "base-map": base.Script,
    "base-entity": base.EntityScript,
    "random-walk": random_walk.RandomWalkScript,
    "test-script": test.TestScript,
}


def get_script(name, sprite, registry):
    return scripts.get(name, lambda **kwargs: None)(
        sprite=sprite,
        registry=registry,
    )
