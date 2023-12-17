#
# Автор: maj0r (t.me/maj0rblog)
# Если вам интересно развитие этого проекта, советую подписаться на мой блог t.me/maj0rblog
#

import os
import psutil
import configparser
from threading import Thread


config = configparser.ConfigParser()
config.read('config.ini')

os.environ["YMT"] = config.get('Settings', 'token') # Здесь должен быть ваш токен Яндекс музыки

if __name__ == "__main__":
    if not os.path.exists("resources/cache") or not os.path.exists("resources"):
        raise Exception("Не найдены необходимые файлы. Пожалуйста, прочтите инструкцию.")
    if os.getenv("YMT") == "TOKEN_HERE" or "":
        raise Exception("Не указан токен, укажите пожалуйста токен.")

    from app.listener.listener import Listener
    from app.ui.ui import main as UI

    listener = Thread(target=Listener().main_loop)
    listener.start()

    ui = Thread(target=UI)
    ui.start()
