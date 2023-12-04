@echo off
chcp 65001
cls
echo Установка необходимых пакетов
echo Убедитесь, что у вас Python 3.11.5
python -m pip install -r requirements.txt
echo Скрипт установки завершён
pause