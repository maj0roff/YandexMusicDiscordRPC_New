# Мамма мия 🤌
# Пепперонни 🤌
import sys
import win32console
import json
import os
import threading
import time

import configparser
config = configparser.ConfigParser()
config.read('config.ini')


def allocate_console():
    win32console.FreeConsole()
    win32console.AllocConsole()
    sys.stdout = open("CONOUT$", "w")
    sys.stderr = open("CONOUT$", "w")


os.environ["Version"] = "S_02_02"
try:
    os.environ["DEBUG"] = config.get("Settings", "debug")
    os.environ["DEBUG_Update"] = config.get("Settings", "debug_update")
except configparser.NoOptionError:
    print("[ Main ] Old config detected. Adding new strings.")
    config["Settings"]["token"] = config.get("Settings", "token")
    config["Settings"]["debug"] = "False"
    config["Settings"]["debug_update"] = "False"
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    os.environ["DEBUG"] = "False"
    os.environ["DEBUG_Update"] = "False"

if os.environ.get("DEBUG") == "True":
    allocate_console()

# Yandex env
os.environ["Yandex_Current"] = json.dumps({'type': 'waiting'})


from apps.yandex.main import Yandex
from apps.discord.main import Discord
from apps.userinterface.main import run_ui


def threads_listener():
    yandex_thread = threading.Thread(target=Yandex().run_yandex)
    discord_thread = threading.Thread(target=Discord().run_discord)
    ui_thread = threading.Thread(target=run_ui)

    yandex_thread.start()
    discord_thread.start()
    ui_thread.start()
    while True:
        if not yandex_thread.is_alive():
            print("[ Threads listener ] Yandex thread got dead. Trying to restart.")
            yandex_thread = None
            yandex_thread = threading.Thread(target=Yandex().run_yandex)
            yandex_thread.start()
        if not discord_thread.is_alive():
            print("[ Threads listener ] Discord thread got dead. Trying to restart.")
            discord_thread = None
            discord_thread = threading.Thread(target=Discord().run_discord)
            discord_thread.start()
        if not ui_thread.is_alive():
            print("[ Threads listener ] UI thread got dead. Trying to restart.")
            ui_thread = None
            ui_thread = threading.Thread(target=run_ui)
            ui_thread.start()
        time.sleep(30)


listener = threading.Thread(target=threads_listener)


def main():
    listener.start()


if __name__ == "__main__":
    main()
