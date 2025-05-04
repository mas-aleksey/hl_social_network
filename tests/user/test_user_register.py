from datetime import date

import bcrypt
import pytest
from httpx import AsyncClient

from db.connector import PostgresDB


REGISTER_PAYLOAD = {
    "login": "a.ivanov",
    "first_name": "anton",
    "last_name": "ivanov",
    "password": "top_secret_password",
    "birthdate": "1991-01-15",
    "gender": "male",
    "interests": "high load projects",
    "city": "Moscow",
}


async def test_register_user(xclient: AsyncClient, db: PostgresDB) -> None:
    response = await xclient.post("/user/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 200, response.text
    assert response.json() == {"user_id": "a.ivanov"}

    async with db.pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE id = 'a.ivanov'")
    assert user["id"] == "a.ivanov"
    assert user["first_name"] == "anton"
    assert user["last_name"] == "ivanov"
    assert bcrypt.checkpw(REGISTER_PAYLOAD["password"].encode(), user["password"])
    assert user["birthdate"] == date(1991, 1, 15)
    assert user["gender"] == "male"
    assert user["interests"] == "high load projects"
    assert user["city"] == "Moscow"


@pytest.mark.usefixtures("prepare_user")
async def test_register_user_conflict(xclient: AsyncClient, db: PostgresDB) -> None:
    response = await xclient.post("/user/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 409, response.text
    assert response.json() == {"detail": "User already exists"}
