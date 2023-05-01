from bush import timer


class Tool:
    def __init__(self, player, usage_delay, push_state=None, mana_cost=0):
        self.player = player
        self.use_timer = timer.Timer(usage_delay)
        self.use_timer.finish()
        self.push_state = push_state
        self.mana_cost = 0

    def equip(self):
        self.use_timer.finish()

    def dequip(self):
        pass

    def can_be_used(self):
        return self.use_timer.done() and self.player.current_mana >= self.mana_cost

    def use(self):
        if self.can_be_used():
            self.use_callback()
            if self.push_state is not None:
                self.player.push_state(self.push_state)

    def use_callback(self):
        print(self, "used")


class Sword(Tool):
    def __init__(self, player):
        super().__init__(player, 250)


def get_tool(player, tool_id):
    return TOOL_DICT[tool_id](player)


TOOL_DICT = {"base": Tool, "sword": Sword}