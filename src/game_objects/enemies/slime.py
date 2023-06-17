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
            start_health=12,
            max_health=12,
            script="random-walk",
        )
