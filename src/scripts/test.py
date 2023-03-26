from bush import timer
from scripts import base


class TestScript(base.EntityScript):
    def begin(self):
        super().begin()
        self.say("Here is some TEST text", lambda x: self.end())

    def end(self):
        print("Goodbye, you silly goober")
        super().end()
