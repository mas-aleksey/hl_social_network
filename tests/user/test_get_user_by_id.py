import pytest
from httpx import AsyncClient

from db.connector import PostgresDB
from user.auth import make_token


@pytest.mark.usefixtures("prepare_user")
async def test_get_user_by_id(xclient: AsyncClient, db: PostgresDB) -> None:
    token = make_token("a.ivanov")
    response = await xclient.get("/user/get/a.ivanov", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    assert response.json() == {
        "id": "a.ivanov",
        "first_name": "anton",
        "last_name": "ivanov",
        "birthdate": "1991-01-15",
        "gender": "male",
        "interests": "high load projects",
        "city": "Moscow",
    }


@pytest.mark.usefixtures("prepare_user")
async def test_get_user_by_id_401(xclient: AsyncClient, db: PostgresDB) -> None:
    response = await xclient.get("/user/get/a.ivanov")
    assert response.status_code == 401, response.text
    assert response.json() == {"detail": "No token provided"}


@pytest.mark.usefixtures("prepare_user")
async def test_get_user_by_id_403(xclient: AsyncClient, db: PostgresDB) -> None:
    response = await xclient.get("/user/get/a.ivanov", headers={"Authorization": "Bearer foo"})
    assert response.status_code == 403, response.text
    assert response.json() == {"detail": "Invalid token"}
