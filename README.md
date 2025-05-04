# Highload Architect - проект социальной сети

## Пререквизиты:
- docker
- docker-compose
- python3.12
- `.env` файл с содержимым

```
#   Postgres
POSTGRES_DB=social_network
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

#   App
DB_URI=postgresql://postgres:postgres@localhost:5678/social_network
SECRET_KEY=DjZ3VVECEiVR9tiwWFF8MEbutZVHgMqG
```

## Команды для запуска проекта
```bash
docker compose up -d db
pip install poetry && poetry self add poetry-dotenv-plugin
poetry install
poetry run alembic upgrade head
PYTHONPATH=$PWD/src poetry run uvicorn src.app:app
```

## Запуск тестов
```bash
PYTHONPATH=$PWD/src poetry run pytest tests -vv
```