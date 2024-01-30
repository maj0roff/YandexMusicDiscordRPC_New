import requests
import wx
import re
import os
import psutil

app = wx.App()
app.MainLoop()


class Updater:
    def __init__(self, version):
        self.version = version

    def update(self):
        r = requests.get("https://api.github.com/repos/maj0roff/YandexMusicDiscordRPC_New/releases/latest")
        latest_version = r.json()["tag_name"]
        update_log = re.sub(r'!\[image\]\(.*?\)', "", r.json()["body"])
        if latest_version != self.version:
            resp = wx.MessageBox(f'Обнаружена новая версия программы.'
                                 f'\n\nСписок изменений:{update_log}'
                                 f'\n\nХотите обновиться?',
                                 'Обновление',
                                 wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
            if resp == wx.OK:
                print(os.getcwd())
                os.system(f"{os.getcwd()}\\updater.exe")
                current_system_pid = os.getpid()

                ThisSystem = psutil.Process(current_system_pid)
                ThisSystem.terminate()

            else:
                return
