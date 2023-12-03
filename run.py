#
# Автор: maj0r (t.me/maj0rblog)
# Если вам интересно развитие этого проекта, советую подписаться на мой блог t.me/maj0rblog
#

import os


os.environ["YANDEXMUSIC_TOKEN"] = ""  # Здесь должен быть ваш токен Яндекс музыки

if __name__ == "__main__":
    if os.getenv("YANDEXMUSIC_TOKEN") == "":
        print("Сначала введите токен")
        exit()

    from app.app import App
    app = App()
    app.main()
