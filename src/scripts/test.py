from scripts import base


class TestScript(base.EntityScript):
    def update(self, dt):
        print("I exist!")

    def begin(self):
        print("In the Beginning...")
