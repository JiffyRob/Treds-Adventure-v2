from game_objects.enemies import enemy


class Slime(enemy.BaseEnemy):
    def __init__(
        self,
        data,
    ):
        super().__init__(
            data=data,
            anim_dict=enemy.get_anim_dict("slime2", (16, 16)),
            initial_state="idle",
            start_health=3,
            max_health=3,
            script="random_walk.snk",
        )
