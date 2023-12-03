import os
from pypresence import Presence


class Discord:
    def __init__(self):
        self.clientid = os.getenv("DISCORD_CLIENTID")
        self.cli = Presence(self.clientid)

    def connect(self):
        self.cli.connect()

    def disconnect(self):
        self.cli.close()

    def update(self, state: str, details: str, large_image: dict, small_image: dict, buttons: list | None = None):
        # large_image -> url: str
        # large_image -> text: str
        # small_image -> url: str
        # small_image -> text: str
        # buttons -> 0: dict -> label: str
        #               dict -> url: str
        #            1: dict -> label: str
        #               dict -> url: str
        self.cli.update(state=state, details=details,
                        large_image=large_image["url"], large_text=large_image["text"],
                        small_image=small_image["url"], small_text=small_image["text"],
                        buttons=buttons)
