from datetime import date

import bcrypt
import pytest

from db.connector import PostgresDB


@pytest.fixture
async def prepare_user(db: PostgresDB) -> None:
    async with db.pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
            "a.ivanov",
            "anton",
            "ivanov",
             date(1991, 1, 15),
            "male",
            "high load projects",
            "Moscow",
            bcrypt.hashpw("top_secret_password".encode(), bcrypt.gensalt()),
        )
