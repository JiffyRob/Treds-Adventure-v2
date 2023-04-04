from bush import lorum_ipsum
from scripts import base


class TestScript(base.EntityScript):
    def begin(self):
        super().begin()
        self.ask(
            lorum_ipsum.lorum_ipsum + "  You're a silly goober.",
            ("A", "B"),
            self.reply,
        )

    def reply(self, answer):
        self.say(f"You said {answer}", self.end)

    def end(self, _=0):
        print("Goodbye, you silly goober")
        super().end()
