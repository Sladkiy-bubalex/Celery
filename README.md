# Api cервис на Flask для апскейлинга изображений.

## Описание

- Сервис принимает изображение HTTP методом POST для [апскейлинга](https://ru.wiktionary.org/wiki/%D0%B0%D0%BF%D1%81%D0%BA%D0%B5%D0%B9%D0%BB%D0%B8%D0%BD%D0%B3)
- При загрузке изображения отдает:
  - task_id - для запроса по ходу выполнения задачи
  - doc_id - для возврата обработанного файла

## Начало работы

- Установите Docker Desktop
- Выполните команду ```docker build -t api_upscale:1.0 .```
- Выполните команду ```docker-compose up -d```
- Выполняйте запросы по end-point`ам

## Стэк

- Flask
- Flask-Pymongo
- Celery
- Redis
- OpenCV
- Cachetools