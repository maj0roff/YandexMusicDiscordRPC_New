import os
import time

os.environ['DISCORD_CLIENTID'] = "1069497740238794853"

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
        os.system("cls")
        print("--------------------------")
        print("t.me/maj0rblog")
        print("--------------------------\n")
        discord.connect()
        while True:
            current = yandex.get_current_playing_info()
            match current['type']:
                case "radio":
                    if self.desc != current['description']:
                        self.desc = current['description']

                        radiotype = current['id'].split(":")[0]
                        subtype = current['id'].split(":")[1]

                        match radiotype:
                            case "personal":
                                self.radiostate = current['description']
                                self.radiodetails = f"Слушает персональное радио"
                                match subtype:
                                    case "hits":
                                        self.radioimage = {"url": "radio_hits",
                                                           "text": current['description']}
                                    case "missed-likes":
                                        self.radioimage = {"url": "radio_missed_likes",
                                                           "text": current['description']}
                                    case "collection":
                                        self.radioimage = {"url": "radio_collection",
                                                           "text": f"Моя {current['description'].lower()}"}
                            case "genre":
                                self.radiostate = current['description']
                                self.radiodetails = f"Слушает радио по жанрам"
                                self.radioimage = {"url": f"radio_genres",
                                                   "text": f"Жанр {current['description'].lower()}"}
                            case "mood":
                                self.radiostate = current['description']
                                self.radiodetails = f"Слушает радио по настроению"
                                self.radioimage = {"url": f"radio_mood",
                                                   "text": current['description']}
                            case "activity":
                                self.radiostate = current['description']
                                self.radiodetails = f"Слушает радио"
                                self.radioimage = {"url": f"radio_activity",
                                                   "text": current['description']}
                            case "epoch":
                                self.radiostate = current['description']
                                self.radiodetails = f"Слушает радио"
                                self.radioimage = {"url": f"radio_epoch",
                                                   "text": f"Эпоха {current['description'].lower()}"}
                            case _:
                                self.radiostate = current['description']
                                self.radiodetails = f"Слушает радио"
                                self.radioimage = {"url": "radio_editorial",
                                                   "text": current['description']}

                        small_image = {"url": "logo", "text": "Яндекс.Музыка"}
                        print(self.radiodetails, self.radiostate.lower())
                        discord.update(self.radiostate, self.radiodetails, self.radioimage, small_image)

                case "playlist":
                    track = current['track_info']
                    if self.switchid != track['id']:
                        self.switchid = track['id']
                        state = f"{track['artists']}"
                        details = f"{track['title']}"

                        if track['title'] == track['album_title']:
                            large_image = {"url": current['track_info']['cover_link'],
                                           "text": f"{track['title']}"}
                        else:
                            large_image = {"url": current['track_info']['cover_link'],
                                           "text": f"{track['title']} ({track['album_title']})"}

                        small_image_url = current['track_info']['artist_cover'] \
                            if current['track_info']['artist_cover'] is not None else "artists"
                        small_image = {"url": small_image_url, "text": track['artists']}
                        buttons = [{"label": "Открыть в Яндекс музыке", "url": track['track_link']}]

                        print("Слушаем", state, "-", details)
                        discord.update(state, details, large_image, small_image, buttons)
                        
                case "radio_track":
                    radiotrack = current['track_info']
                    if self.switchid != current['type']:
                        self.switchid = current['type']
                        state = radiotrack['title']
                        details = "Радио по треку"

                        large_image = {"url": f"https://{radiotrack['cover_link'].replace('%%', '800x800')}",
                                       "text": f"Радио по треку {radiotrack['artists']} - {radiotrack['title']}"}

                        small_image = {"url": "radio_editorial",
                                       "text": f"{radiotrack['artists']} - {radiotrack['title']}"}

                        print("Слушаем", details.lower(), state.lower())
                        discord.update(state, details, large_image, small_image)
            time.sleep(2)


App().main()
