
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
