import os
import time

os.environ["DISCORD_CLIENTID"] = "1069497740238794853"

from app.modules.yandex import Yandex
from app.modules.discord import Discord

discord = Discord()
yandex = Yandex()


class App:
    def __init__(self):
        self.switchid = "0"
        self.desc = "0"
        self.radioimage = ""
        self.radiostate = ""
        self.radiodetails = ""

    def main(self):
        discord.connect()
        while True:
            current = yandex.get_current_playing_info()
            time.sleep(2)
            match current["type"]:
                case "radio":
                    if self.desc != current["description"]:
                        print(current)
                        self.desc = current["description"]

                        radiotype = current["id"].split(":")[0]
                        subtype = current["id"].split(":")[1]

                        match radiotype:
                            case "personal":
                                self.radiostate = current["description"]
                                self.radiodetails = f"Слушает персональное радио"
                                match subtype:
                                    case "hits":
                                        self.radioimage = {"url": "radio_hits",
                                                           "text": current["description"]}
                                    case "missed-likes":
                                        self.radioimage = {"url": "radio_missed_likes",
                                                           "text": current["description"]}
                                    case "collection":
                                        self.radioimage = {"url": "radio_collection",
                                                           "text": f"Моя {current["description"].lower()}"}
                            case "genre":
                                self.radiostate = current["description"]
                                self.radiodetails = f"Слушает радио по жанрам"
                                self.radioimage = {"url": f"radio_genres",
                                                   "text": f"Жанр {current["description"].lower()}"}
                            case "mood":
                                self.radiostate = current["description"]
                                self.radiodetails = f"Слушает радио по настроению"
                                self.radioimage = {"url": f"radio_mood",
                                                   "text": current["description"]}
                            case "activity":
                                self.radiostate = current["description"]
                                self.radiodetails = f"Слушает радио"
                                self.radioimage = {"url": f"radio_activity",
                                                   "text": current["description"]}
                            case "epoch":
                                self.radiostate = current["description"]
                                self.radiodetails = f"Слушает радио"
                                self.radioimage = {"url": f"radio_epoch",
                                                   "text": f"Эпоха {current["description"].lower()}"}
                            case _:
                                self.radiostate = current["description"]
                                self.radiodetails = f"Слушает радио"
                                self.radioimage = {"url": "radio_editorial",
                                                   "text": current["description"]}

                        small_image = {"url": "logo", "text": "Яндекс.Музыка"}
                        discord.update(self.radiostate, self.radiodetails, self.radioimage, small_image)

                case "playlist":
                    track = current["track_info"]
                    if self.switchid != track["id"]:
                        self.switchid = track["id"]
                        print(track)
                        state = f"{track["artists"]}"
                        details = f"{track["title"]}"

                        if track["title"] == track["album_title"]:
                            large_image = {"url": current["track_info"]["cover_link"],
                                           "text": f"{track["title"]}"}
                        else:
                            large_image = {"url": current["track_info"]["cover_link"],
                                           "text": f"{track["title"]} ({track["album_title"]})"}

                        small_image_url = current["track_info"]["artist_cover"] \
                            if current["track_info"]["artist_cover"] is not None else "artists"
                        small_image = {"url": small_image_url, "text": track["artists"]}
                        buttons = [{"label": "Открыть в Яндекс музыке", "url": track["track_link"]}]

                        discord.update(state, details, large_image, small_image, buttons)


App().main()
