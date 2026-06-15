# Upscale Service

API для апскейлинга изображений на Flask + Celery + Redis + OpenCV DNN Super Resolution.

## Роуты

- `POST /upscale` — принимает файл изображения в поле `file`, проверяет формат по сигнатуре файла и возвращает `task_id`. Разрешены JPG, PNG, BMP, TIFF.
- `GET /tasks/<task_id>` — возвращает статус задачи и ссылку на обработанный файл, если задача выполнена.
- `GET /processed/<file>` — возвращает обработанный PNG-файл.

## Запуск через Docker

```bash
docker compose up --build
```

## Проверка

```bash
curl -X POST -F "file=@lama_300px.png" http://localhost:5000/upscale
curl http://localhost:5000/tasks/<task_id>
curl -o result.png http://localhost:5000/processed/<file>
```

## Тесты

```bash
pip install -r requirements.txt
pytest
```

## Конфигурация

Основные параметры вынесены в `config.py`: адреса Redis/Celery, TTL для исходных и обработанных файлов, лимит размера загрузки, путь к модели и список разрешённых типов изображений. Значения можно переопределять через переменные окружения.

## Особенности реализации

- Модель загружается один раз на процесс Celery worker'а.
- `/upscale` принимает только JPG, PNG, BMP и TIFF; тип определяется по магическим байтам, а не по имени файла.
- Изображения не сохраняются на диск: исходный файл и результат временно хранятся в Redis.
- Результаты автоматически удаляются из Redis по TTL.
