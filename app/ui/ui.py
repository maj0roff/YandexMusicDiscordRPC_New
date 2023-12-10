import webbrowser
import wx.adv
import wx

import os
import psutil

TRAY_TOOLTIP = 'YandexMusicRPC'
TRAY_ICON = 'resources/logo.ico'
TELEGRAM_ICON = 'resources/telegram.png'


def png_to_bitmap(png):
    return wx.Image(png, wx.BITMAP_TYPE_ANY).Rescale(18, 18, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()


def create_label(menu, icon, label, func):
    item = wx.MenuItem(menu, -1, label)
    if icon is not None:
        item.SetBitmap(icon)

    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.ShowBalloon("Привет!", "Я нахожусь в трее.")
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        logo_label = create_label(menu, png_to_bitmap(TRAY_ICON), 'YandexMusicRPC', self.opengit)
        telegram_label = create_label(menu, png_to_bitmap(TELEGRAM_ICON), 'Мой телеграм канал', self.opentg)
        menu.AppendSeparator()
        exit_label = create_label(menu, None, 'Выход', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.Icon(path)
        self.SetIcon(icon, TRAY_TOOLTIP)

    def opengit(self, event):
        webbrowser.open("https://github.com/maj0roff/YandexMusicDiscordRPC_New")

    def opentg(self, event):
        webbrowser.open("https://t.me/maj0rblog")

    def on_left_down(self, event):
        print('left click.')

    def on_exit(self, event):
        self.ShowBalloon("Выход", "Всё? Завершаю работу!")
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
