import os
import time

import psutil

import requests.exceptions
import yandex_music.exceptions
from yandex_music import Client, TrackId


class Yandex:
    def __init__(self):
        self.token = os.getenv("YMT")
        try:
            self.cli = Client(self.token).init()
        except yandex_music.exceptions.UnauthorizedError:
            raise yandex_music.exceptions.UnauthorizedError("Токен не указан или не действителен")
        self.queue = ""

    def get_user_info(self) -> dict:
        userinfo = self.cli.me

        return userinfo

    @staticmethod
    def __get_track_info(trackid: TrackId) -> dict:
        try:
            fetched_track = trackid.fetch_track()
            fetched_album = fetched_track.albums[0]
        except yandex_music.exceptions.TimedOutError:
            time.sleep(4)
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

    def get_current_playing_info(self) -> dict:
        doneresult = {}

        """
        try:
            queue_raw = self.cli.queues_list()[0]
        except (requests.exceptions.ReadTimeout, yandex_music.exceptions.TimedOutError):
            queue_raw = self.cli.queues_list()[0]
        """

        try:
            queue_raw = self.cli.queues_list()[0]
        except yandex_music.exceptions.TimedOutError:
            time.sleep(4)
            queue_raw = self.cli.queues_list()[0]

        if queue_raw.context.type == "radio":
            self.queue = self.cli.queues_list()[0]
        else:
            try:
                self.queue = self.cli.queue(queue_raw.id)
            except yandex_music.exceptions.NotFoundError:
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

        return doneresult
