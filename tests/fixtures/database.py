from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from db.connector import PostgresDB
from settings import Settings


ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent


@pytest.fixture
def prepare_test_database(settings: Settings) -> None:
    real_dsn = settings.DB_URI
    test_db_name = "pytest_db"
    test_db_url = real_dsn[0: real_dsn.rfind("/") + 1] + test_db_name
    with create_engine(real_dsn, isolation_level="AUTOCOMMIT").connect() as connection:
        # connection.execute(text(f'DROP DATABASE "{test_db_name}";'))
        connection.execute(text(f'CREATE DATABASE "{test_db_name}"'))

    try:
        alembic_file = ROOT_DIR / "alembic.ini"
        alembic_cfg = Config(alembic_file.as_posix())
        alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)
        command.upgrade(alembic_cfg, "head")
        yield test_db_url

    finally:
        with create_engine(real_dsn, isolation_level="AUTOCOMMIT").connect() as connection:
            connection.execute(text(f'DROP DATABASE "{test_db_name}";'))


@pytest.fixture
def db(prepare_test_database: str) -> PostgresDB:
    _db = PostgresDB(prepare_test_database)
    yield _db
