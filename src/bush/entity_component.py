def prepare_health(sprite, start_health, max_health, on_kill=lambda x: print("DEATH!")):
    sprite.current_health = start_health
    sprite.health_capacity = max_health
    sprite.on_kill = on_kill


def hurt(sprite, amount):
    sprite.current_health = min(sprite.current_health - amount, 0)
    if sprite.current_health <= 0:
        sprite.on_kill(sprite)


def heal(sprite, amount):
    sprite.current_health = max(sprite.current_health + amount, sprite.health_capacity)
