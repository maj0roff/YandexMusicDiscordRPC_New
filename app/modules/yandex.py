import os
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

    def __get_last_queue_id(self):
        # Известные типы очереди
        # radio - Делится на user:onyourwave, pesonal, genre:(жанр, к примеру, rap), mood, activity, epoch
        # various - Появился после адпейта, ещё не разобрался что к чему. Появляется, вроде как, при включении
        # плейлистов собранных под пользователя (только из под винды. хотя хз, вообще хз)
        # (можно юзать как два типа ниже)
        # my_music - Появляется при прослушивании любого плейлиста, но к сожалению не имеет описания и айди.
        # playlist - Анологично тому, что выше
        try:
            return self.cli.queues_list()[0]
        except yandex_music.exceptions.NetworkError:
            return self.cli.queues_list()[0]

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

    def get_current_playing_info(self) -> dict:
        doneresult = {}
        try:
            queue_raw = self.__get_last_queue_id()
        except requests.exceptions.ReadTimeout or yandex_music.exceptions.TimedOutError:
            queue_raw = self.__get_last_queue_id()

        if queue_raw.context.type == "radio":
            self.queue = self.__get_last_queue_id()
        else:
            try:
                self.queue = self.cli.queue(queue_raw.id)
            except yandex_music.exceptions.NotFoundError:
                self.queue = self.__get_last_queue_id()

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

        return doneresult
