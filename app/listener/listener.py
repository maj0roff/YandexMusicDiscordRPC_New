import os
import time

import yandex_music.exceptions

os.environ['DISCORD_CLIENTID'] = "1069497740238794853"

from app.modules.yandex import Yandex
from app.modules.discord import Discord

discord = Discord()
try:
    yandex = Yandex()
except yandex_music.exceptions.NetworkError:
    yandex = Yandex()
os.environ['USERNAME'] = str(yandex.get_user_info()["account"]["login"] + "@yandex.ru")


class Listener:
    def __init__(self):
        self.switchid = "0"
        self.desc = "0"
        self.radioimage = dict
        self.radiostate = str
        self.radiodetails = str

    def update_info(self, id):
        os.environ['CURRENT_TRACK'] = str(self.radiostate)
        os.environ['CURRENT_ARTIST'] = str(self.radiodetails)
        os.environ['CURRENT_IMAGE'] = str(self.radioimage['url'])
        os.environ['CURRENT_ID'] = str(id)

    def main_loop(self):
        discord.connect()
        while True:
            try:
                current = yandex.get_current_playing_info()
            except yandex_music.exceptions.NetworkError:
                time.sleep(3)
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
                        self.update_info(current['description'])
                        discord.update(self.radiostate, self.radiodetails, self.radioimage, small_image)

                case "playlist":
                    track = current['track_info']
                    if self.switchid != track['id']:
                        self.switchid = track['id']
                        self.radiodetails = f"{track['artists']}"
                        self.radiostate = f"{track['title']}"

                        if track['title'] == track['album_title']:
                            self.radioimage = {"url": current['track_info']['cover_link'],
                                               "text": f"{track['title']}"}
                        else:
                            self.radioimage = {"url": current['track_info']['cover_link'],
                                               "text": f"{track['title']} ({track['album_title']})"}

                        small_image_url = current['track_info']['artist_cover'] \
                            if current['track_info']['artist_cover'] is not None else "artists"
                        small_image = {"url": small_image_url, "text": track['artists']}
                        buttons = [{"label": "Oткрыть в Я.Mузыкa", "url": track['track_link']}]

                        print("Слушаем", self.radiodetails, "-", self.radiostate)
                        # buttons

                        self.update_info(track['id'])
                        discord.update(self.radiodetails, self.radiostate, self.radioimage, small_image, buttons)
                        
                case "radio_track":
                    radiotrack = current['track_info']
                    if self.switchid != current['type']:
                        self.switchid = current['type']
                        self.radiostate = radiotrack['title']
                        self.radiodetails = "Радио по треку"

                        large_image = {"url": f"https://{radiotrack['cover_link'].replace('%%', '800x800')}",
                                       "text": f"Радио по треку {radiotrack['artists']} - {radiotrack['title']}"}

                        small_image = {"url": "radio_editorial",
                                       "text": f"{radiotrack['artists']} - {radiotrack['title']}"}

                        print("Слушаем", self.radiostate.lower(), self.radiodetails.lower())
                        self.update_info(current['type'])

                        discord.update(self.radiostate, self.radiodetails, large_image, small_image)
            time.sleep(7)



