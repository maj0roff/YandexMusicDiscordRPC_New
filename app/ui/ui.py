import webbrowser
import wx
import wx.adv

import os
import psutil
import requests
from PIL import Image, ImageDraw

TRAY_TOOLTIP = 'YandexMusicRPC'
TRAY_ICON = 'resources/logo.ico'
TELEGRAM_ICON = 'resources/telegram.png'


def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im


def png_to_bitmap(png, size=(18, 18)):
    return wx.Image(png, wx.BITMAP_TYPE_ANY).Rescale(size[0], size[1], wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()


def create_label(menu, icon, label, func):
    item = wx.MenuItem(menu, -1, label)
    if icon is not None:
        item.SetBitmap(icon)

    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):

        self.done_cover = None
        self.artist_label = None
        self.track_label = None

        self.switch = ""
        self.track_cover = ""

        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.Bind(wx.adv.EVT_TASKBAR_RIGHT_DOWN, self.on_right_down)
        self.ShowBalloon("Привет!", "Я нахожусь в трее.")
        self.trackinfo = self.get_track_info()

    def CreatePopupMenu(self):
        menu = wx.Menu()
        logo_label = create_label(menu, png_to_bitmap(TRAY_ICON), 'YandexMusicRPC', self.opengit)
        telegram_label = create_label(menu, png_to_bitmap(TELEGRAM_ICON), 'Мой телеграм канал', self.opentg)
        menu.AppendSeparator()
        username_label = create_label(menu, None, f'Вы вошли как: {os.environ.get("USERNAME")}', None)
        username_label.Enable(False)
        userexit_label = create_label(menu, None, f'Выйти из аккаунта', self.exitacc)
        menu.AppendSeparator()
        self.track_label = create_label(menu, self.done_cover, f'{self.trackinfo["track"]}', None)
        self.artist_label = create_label(menu, None, f'{self.trackinfo["artist"]}', None)
        menu.AppendSeparator()
        exit_label = create_label(menu, None, 'Выход', self.on_exit)
        return menu

    def get_track_info(self) -> dict:
        return {
            'track': os.environ.get("CURRENT_TRACK") if os.environ.get(
                "CURRENT_TRACK") is not None else "Ищем информацию о треке",
            'artist': os.environ.get("CURRENT_ARTIST"),
            'image': os.environ.get("CURRENT_IMAGE"),
            'id': os.environ.get("CURRENT_ID")
        }

    def set_icon(self, path):
        icon = wx.Icon(path)
        self.SetIcon(icon, TRAY_TOOLTIP)

    def exitacc(self, event):
        import configparser
        config = configparser.ConfigParser()
        config.read('config.ini')
        config.set('Settings', 'token', "TOKEN_HERE")
        with open('config.ini', 'w') as cfg:
            config.write(cfg)
        self.ShowBalloon("Уведомление", "Вы успешно вышли из аккаунта.")
        wx.CallAfter(self.Destroy)
        self.frame.Close()

    def opengit(self, event):
        webbrowser.open("https://github.com/maj0roff/YandexMusicDiscordRPC_New")

    def opentg(self, event):
        webbrowser.open("https://t.me/maj0rblog")

    def on_right_down(self, event):
        self.trackinfo = self.get_track_info()
        if self.switch != self.trackinfo["id"]:
            self.switch = self.trackinfo['id']

            if "https" in self.trackinfo["image"]:
                img_data = requests.get(self.trackinfo["image"]).content
                with open('resources/cache/cached_cover.png', 'wb') as handler:
                    handler.write(img_data)
                img = Image.open("resources/cache/cached_cover.png")
                img = add_corners(img, 192)
                img.save("resources/cache/cached_cover.png")
                self.track_cover = "resources/cache/cached_cover.png"
            else:
                self.track_cover = f"resources/covers/{self.trackinfo['image']}.png"

        self.done_cover = png_to_bitmap(self.track_cover, (32, 32))

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        self.frame.Close()


class App(wx.App):
    def OnInit(self):
        frame = wx.Frame(None)
        self.SetTopWindow(frame)
        TaskBarIcon(frame)
        return True


def main():
    app = App(False)
    app.MainLoop()
    current_system_pid = os.getpid()

    ThisSystem = psutil.Process(current_system_pid)
    ThisSystem.terminate()
