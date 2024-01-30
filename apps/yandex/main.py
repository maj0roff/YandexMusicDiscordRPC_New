import os
import json
import time
import configparser

from contextlib import suppress
from apps.token import update_token

import yandex_music.exceptions
from yandex_music import Client, TrackId

config = configparser.ConfigParser()
config.read('config.ini')


class Yandex:
    def __init__(self):
        print("Initializing Yandex")
        self.token = config.get("Settings", "token")
        if 'Ag' not in self.token:
            update_token()

        try:
            self.cli = Client(self.token).init()
        except yandex_music.exceptions.UnauthorizedError:
            update_token()
            self.cli = Client(self.token).init()
        self.queue = ""

    def get_user_info(self) -> dict:
        userinfo = self.cli.me
        return {"name": userinfo["account"]["first_name"],
                "surname": userinfo["account"]["second_name"],
                "login": userinfo["account"]["login"]}

    @staticmethod
    def __get_track_info(trackid: TrackId) -> dict:
        fetched_track = trackid.fetch_track()
        fetched_album = fetched_track.albums[0]

        tid = fetched_track.id
        title = fetched_track.title
        artists = ", ".join(fetched_track.artists_name())
        cover = f"https://{fetched_track.cover_uri.replace('%%', '800x800')}"
        if len(fetched_track.artists) != 1:
            artist_cover = None
        else:
            if fetched_track.artists[0].cover is None:
                artist_cover = "logo"
            else:
                artist_cover = f"https://{fetched_track.artists[0].cover.uri.replace('%%', '800x800')}"

        return {"id": tid,
                "title": title,
                "artists": artists,
                "album_title": fetched_album.title,
                "cover_link": cover,
                "artist_cover": artist_cover,
                "track_link": f"https://music.yandex.ru/album/{fetched_track.albums[0].id}/track/{tid}"}

    def run_yandex(self):
        os.environ["Yandex_Login"] = self.get_user_info()["login"]
        while True:
            doneresult = {}

            queue_raw = self.cli.queues_list()[0]

            if queue_raw.context.type == "radio":
                self.queue = self.cli.queues_list()[0]
            else:
                with suppress(yandex_music.exceptions.TimedOutError):
                    try:
                        self.queue = self.cli.queue(queue_raw.id)
                    except yandex_music.exceptions.NotFoundError:
                        with suppress(yandex_music.exceptions.TimedOutError):
                            self.queue = self.cli.queues_list()[0]

            queue_type = self.queue.context.type
            match queue_type:
                case "radio":
                    if self.queue.context.id.split(':')[0] == "track":
                        radio_trackinfo = self.cli.tracks(self.queue.context.id.split(':')[1])[0]
                        doneresult.update({"type": "radio_track",
                                           "track_info": {
                                               "id": radio_trackinfo['id'],
                                               "title": radio_trackinfo['title'],
                                               "artists": ", ".join(radio_trackinfo.artists_name()),
                                               "cover_link": radio_trackinfo['cover_uri']
                                           }})
                    else:
                        doneresult.update({"type": "radio",
                                           "id": self.queue.context.id,
                                           "description": self.queue.context.description})
                case "various":
                    try:
                        track_info = self.__get_track_info(self.queue.get_current_track())
                        doneresult.update({"type": "playlist",
                                           "track_info": track_info})
                    except TypeError:
                        doneresult.update({"type": "radio",
                                           "description": "Слушает радио"})
                case "my_music":
                    doneresult.update({"type": "playlist",
                                       "track_info": self.__get_track_info(self.queue.get_current_track())})
                case "playlist":
                    doneresult.update({"type": "playlist",
                                       "track_info": self.__get_track_info(self.queue.get_current_track())})
                case "artist":
                    doneresult.update({"type": "playlist",
                                       "track_info": self.__get_track_info(self.queue.get_current_track())})

            os.environ["Yandex_Current"] = json.dumps(doneresult)
            time.sleep(3)
