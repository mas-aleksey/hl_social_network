import sys
from logging import config as logger_config

import pytest

from db import connector
from settings import Settings, get_settings


pytest_plugins = [
    "fixtures.api",
    "fixtures.database",
    "fixtures.db_data",
]


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(autouse=True)
async def app_lifespan(db: connector.PostgresDB) -> None:
    connector.db = db
    await connector.db.connect()
    yield
    await connector.db.disconnect()


@pytest.fixture(autouse=True)
def init_logger() -> None:
    logger_config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "verbose": {
                    "class": "logging.Formatter",
                    "format": "%(asctime)s [%(levelname)s] %(name)-5s: %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "verbose",
                    "stream": sys.stdout,
                },
            },
            "loggers": {
                "databases": {"level": "INFO"},
            },
            "root": {
                "level": "DEBUG",
                "formatter": "verbose",
                "handlers": [
                    "console",
                ],
            },
        },
    )
