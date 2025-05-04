import pytest
from httpx import AsyncClient

from db.connector import PostgresDB


@pytest.mark.usefixtures("prepare_user")
async def test_user_login(xclient: AsyncClient, db: PostgresDB) -> None:
    response = await xclient.post("/login", json={"user_id": "a.ivanov", "password": "top_secret_password"})
    assert response.status_code == 200, response.text
    assert response.json()["token"]


@pytest.mark.usefixtures("prepare_user")
async def test_user_login_401_wrong_user(xclient: AsyncClient, db: PostgresDB) -> None:
    response = await xclient.post("/login", json={"user_id": "foo", "password": "top_secret_password"})
    assert response.status_code == 401, response.text
    assert response.json() == {"detail": "User or password incorrect"}


@pytest.mark.usefixtures("prepare_user")
async def test_user_login_401_wrong_password(xclient: AsyncClient, db: PostgresDB) -> None:
    response = await xclient.post("/login", json={"user_id": "a.ivanov", "password": "foo"})
    assert response.status_code == 401, response.text
    assert response.json() == {"detail": "User or password incorrect"}
