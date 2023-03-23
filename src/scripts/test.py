from bush import timer
from scripts import base


class TestScript(base.EntityScript):
    def script_update(self, dt):
        super().script_update(dt)
        print("I guess the time's not up.")

    def begin(self):
        super().begin()
        print("In the Beginning...")
        self.add_timer(timer.Timer(1000, self.end))
