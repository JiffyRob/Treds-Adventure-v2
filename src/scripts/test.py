from bush import timer
from scripts import base


class TestScript(base.EntityScript):
    def begin(self):
        super().begin()
        self.ask(
            "How silly of a goober are you?",
            (
                "A little silly.",
                "Pretty silly...",
                "No comment.",
                "So very ridiculously silly that this answer had to over flow a line or two!!!",
            ),
            self.end,
        )

    def end(self):
        print("Goodbye, you silly goober")
        super().end()
