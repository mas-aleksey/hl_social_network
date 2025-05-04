from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, Request

from settings import get_settings


settings = get_settings()
ALG = "HS256"
TIME_DELTA = timedelta(hours=1)


def make_token(user_id: str) -> str:
    data = {
        "sub": user_id,
        "exp": datetime.now(tz=timezone.utc) + TIME_DELTA,
    }
    return jwt.encode(data, settings.SECRET_KEY, algorithm=ALG)


def authorized_user(request: Request) -> str:
    token = request.headers.get("Authorization") or request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")
    token = token.split(" ")[-1]
    try:
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALG])
    except jwt.exceptions.InvalidTokenError as exc:
        raise HTTPException(status_code=403, detail="Invalid token") from exc

    return data["sub"]
