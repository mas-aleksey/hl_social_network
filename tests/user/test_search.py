import pytest
from httpx import AsyncClient

from user.auth import make_token


@pytest.mark.usefixtures("prepare_user")
async def test_search_user(xclient: AsyncClient) -> None:
    params = {"first_name": "ant", "last_name": "iva"}
    headers = {"Authorization": f"Bearer {make_token("a.ivanov")}"}
    response = await xclient.get("/user/search", params=params, headers=headers)
    assert response.status_code == 200, response.text
    assert response.json() == [
        {
            "birthdate": "1991-01-15",
            "city": "Moscow",
            "first_name": "anton",
            "gender": "male",
            "id": "a.ivanov",
            "interests": "high load projects",
            "last_name": "ivanov",
        },
    ]
