# Upscale Service

API для апскейлинга изображений на Flask + Celery + Redis + OpenCV DNN Super Resolution.

## Роуты

- `POST /upscale` — принимает файл изображения в поле `file`, возвращает `task_id`.
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

## Особенности реализации

- Модель загружается один раз на процесс Celery worker'а.
- Изображения не сохраняются на диск: исходный файл и результат временно хранятся в Redis.
- Результаты автоматически удаляются из Redis по TTL.
