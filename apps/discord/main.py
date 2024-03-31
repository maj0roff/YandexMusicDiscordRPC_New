import os
import json
import time
from contextlib import suppress
from pypresence import Presence


class Discord:
    def __init__(self):
        print("[ Discord ] Initializing module")
        print("[ Discord ] Active!")
        self.appid = "1069497740238794853"
        self.cli = Presence(self.appid)
        self.switchid = "0"
        self.desc = "0"
        self.radioimage = dict
        self.radiostate = str
        self.radiodetails = str

    def __connect(self):
        self.cli.connect()

    def __disconnect(self):
        self.cli.close()

    def __update(self, state: str, details: str, large_image: dict, small_image: dict, buttons: list | None = None):
        # large_image -> url: str
        # large_image -> text: str
        # small_image -> url: str
        # small_image -> text: str
        # buttons -> 0: dict -> label: str
        #               dict -> url: str
        #            1: dict -> label: str
        #               dict -> url: str
        self.cli.update(state=state, details=details,
                        large_image=large_image["url"],
                        large_text=large_image["text"],
                        small_image=small_image["url"],
                        small_text=small_image["text"],
                        buttons=buttons)

    def update_info(self, tid):
        os.environ['UI_Track'] = str(self.radiostate)
        os.environ['UI_Artists'] = str(self.radiodetails)
        os.environ['UI_ImageLink'] = str(self.radioimage['url'])
        os.environ['UI_ID'] = str(tid)

    def run_discord(self):
        self.__connect()
        while True:
            current = os.getenv("Yandex_Current")
            current = json.loads(current)

            with suppress(AttributeError):
                try:
                    match current['type']:
                        case "waiting":
                            self.radiostate = "Ищем информацию..."
                            self.radiodetails = "Скоро всё найдём!"
                            small_image = {"url": "logo", "text": "Яндекс.Музыка"}
                            self.radioimage = {"url": f"radio_activity",
                                               "text": "Ищем информацию"}
                            self.__update(self.radiostate, self.radiodetails, small_image=small_image, large_image=self.radioimage)
                            self.update_info("Kek")

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
                                            case "never-heard":
                                                self.radioimage = {"url": "radio_never_heard",
                                                                   "text": current['description'].lower()}
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
                                self.__update(self.radiostate, self.radiodetails, self.radioimage, small_image)
                                self.update_info(current['description'])

                        case "playlist":
                            track = current['track_info']
                            with suppress(TypeError):
                                if self.switchid != track['id']:
                                    self.switchid = track['id']
                                    self.radiodetails = f"{track['artists']}" if track['artists'] != '' else track['album_title']
                                    self.radiostate = f"{track['title']}"

                                    if track['title'] == track['album_title']:
                                        self.radioimage = {"url": current['track_info']['cover_link'],
                                                           "text": f"{track['title']}"}
                                    else:
                                        self.radioimage = {"url": current['track_info']['cover_link'],
                                                           "text": f"{track['title']} ({track['album_title']})"}


                                    if track['artists'] != '':
                                        small_image_url = current['track_info']['artist_cover'] \
                                            if current['track_info']['artist_cover'] is not None else "artists"
                                        small_image = {"url": small_image_url, "text": track['artists']}
                                    else:
                                        small_image = {"url": None, "text": None}

                                    buttons = [{"label": "Oткрыть в Я.Mузыкa", "url": track['track_link']}]

                                    print("Слушаем", self.radiodetails, "-", self.radiostate)
                                    # buttons

                                    self.__update(self.radiodetails, self.radiostate, self.radioimage, small_image, buttons)
                                    self.update_info(track['id'])

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

                                self.__update(self.radiostate, self.radiodetails, large_image, small_image)
                                self.update_info(current['type'])
                except KeyError:
                    self.radiostate = "Ищем информацию..."
                    self.radiodetails = "Скоро всё найдём!"
                    small_image = {"url": "logo", "text": "Яндекс.Музыка"}
                    self.radioimage = {"url": f"radio_activity",
                                       "text": "Ищем информацию"}
                    self.__update(self.radiostate, self.radiodetails, small_image=small_image,
                                  large_image=self.radioimage)
                    self.update_info("Kek")
            time.sleep(3)
