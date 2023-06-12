from game_objects.enemies import enemy


class Slime(enemy.BaseEnemy):
    def __init__(
        self,
        pos,
        registry,
        *_,
        id=None,
        layer=None,
        topleft=False,
        initial_state=None,
        physics_data=None,
        **__,
    ):
        super().__init__(
            pos,
            registry,
            anim_dict=enemy.get_anim_dict("slime2", (16, 16)),
            id=id,
            layer=layer,
            topleft=topleft,
            initial_state=initial_state,
            physics_data=physics_data,
            start_health=12,
            max_health=12,
            script="random-walk",
        )
