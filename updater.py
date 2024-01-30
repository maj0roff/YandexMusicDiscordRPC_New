import requests
import time
import os
import zipfile
import shutil


print("Установка обновления для YandexMusicDiscordRPC")

try:
    os.mkdir(f"{os.getcwd()}\\update_cache\\")
except FileExistsError:
    pass

print("Сохранение конфига...")
shutil.copyfile(f"{os.getcwd()}\\config.ini", f"{os.getcwd()}\\update_cache\\config.ini")

print("Скачивание архива с обновлением...")

file_link = requests.get("https://api.github.com/repos/maj0roff/YandexMusicDiscordRPC_New/releases/latest").json()["assets"][0]["browser_download_url"]
req = requests.get(file_link)
filename = file_link.split('/')[-1]

with open(f"{os.getcwd()}\\update_cache\\{filename}", 'wb') as output_file:
    output_file.write(req.content)

print("Распаковка архива...")

z = zipfile.ZipFile(f"{os.getcwd()}\\update_cache\\{filename}")
z.extractall(f"{os.getcwd()}\\update_cache\\")

shutil.rmtree(f"{os.getcwd()}\\resources")
shutil.copytree(f"{os.getcwd()}\\update_cache\\build\\resources", f"{os.getcwd()}\\resources")
shutil.copyfile(f"{os.getcwd()}\\update_cache\\build\\YandexMusicRPC.exe", f"{os.getcwd()}\\YandexMusicRPC.exe")

print("Чистим временные файлы...")
shutil.rmtree(f"{os.getcwd()}\\update_cache")

print("Установка успешно закончена! Программа запустится через 5 секунд")
time.sleep(5)
os.system(f"{os.getcwd()}\\YandexMusicRPC.exe")
exit(1)
