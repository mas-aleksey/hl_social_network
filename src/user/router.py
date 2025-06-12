import bcrypt
from asyncpg import Connection, UniqueViolationError
from fastapi import APIRouter, Depends, HTTPException

from db.connector import get_db_connection
from settings import get_settings
from user.auth import authorized_user, make_token
from user.schemas import LoginUser, RegisterResponse, RegisterUser, SearchUser, Token, UserInfo


router = APIRouter(tags=["User"])
settings = get_settings()


@router.post("/login")
async def login(
    login_user: LoginUser,
    conn: Connection = Depends(get_db_connection),
) -> Token:
    user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", login_user.user_id)
    if not user or not bcrypt.checkpw(login_user.password.encode(), user["password"]):
        raise HTTPException(status_code=401, detail="User or password incorrect")

    return Token(token=make_token(user["id"]))


@router.post("/user/register")
async def register(
    user: RegisterUser,
    conn: Connection = Depends(get_db_connection),
) -> RegisterResponse:
    try:
        await conn.execute(
            "INSERT INTO users VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
            user.login,
            user.first_name,
            user.last_name,
            user.birthdate,
            user.gender,
            user.interests,
            user.city,
            bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()),
        )
    except UniqueViolationError as exc:
        raise HTTPException(status_code=409, detail="User already exists") from exc
    return RegisterResponse(user_id=user.login)


@router.get("/user/get/{user_login}")
async def get_user(
    user_login: str,
    conn: Connection = Depends(get_db_connection),
    _=Depends(authorized_user),
) -> UserInfo:
    user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_login)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInfo(**user)


@router.get("/user/search")
async def search_user(
    params: SearchUser = Depends(SearchUser),
    conn: Connection = Depends(get_db_connection),
    _=Depends(authorized_user),
) -> list[UserInfo]:
    users = await conn.fetch(
        "SELECT * FROM users WHERE first_name LIKE $1 AND last_name LIKE $2 ORDER BY id",
        f"{params.first_name}%",
        f"{params.last_name}%",
    )
    return [UserInfo(**user) for user in users]
