from bush import text_util
from scripts import base


class TestScript(base.EntityScript):
    def begin(self):
        super().begin()
        self.ask(
            "I have come to the conclusion that "
            + lorum_ipsum.lorum_ipsum
            + "  You're a silly goober.",
            ("Am Not!", "Sure am."),
            self.reply,
        )

    def reply(self, answer):
        print("reply")
        replies = {
            "Am Not!": "Yeah right.  And your Grandfather didn't make a backpack that lights up when you close it.  That's rich.",
            "Sure am.": "Since you're so honest, I'll be honest too.  Your dad has a peanut allergy.",
        }
        self.say(replies[answer], self.end)

    def end(self, _=0):
        print("Goodbye, you silly goober")
        super().end()
