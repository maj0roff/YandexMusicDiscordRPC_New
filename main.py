# Мамма мия 🤌
# Пепперонни 🤌
import json
import os
import threading


version = "Stable1.3"

from apps.update import Updater
Updater(version).update()


# Yandex env
os.environ["Yandex_Current"] = json.dumps({'type': 'waiting'})

from apps.yandex.main import Yandex
from apps.discord.main import Discord
from apps.userinterface.main import run_ui
yandex_thread = threading.Thread(target=Yandex().run_yandex)
discord_thread = threading.Thread(target=Discord().run_discord)
ui_thread = threading.Thread(target=run_ui)


def main():
    yandex_thread.start()
    discord_thread.start()
    ui_thread.start()


if __name__ == "__main__":
    main()
