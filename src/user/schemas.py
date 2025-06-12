from datetime import date

from pydantic import BaseModel, Field


class LoginUser(BaseModel):
    user_id: str
    password: str


class Token(BaseModel):
    token: str


class UserInfo(BaseModel):
    login: str = Field(alias="id")
    first_name: str
    last_name: str
    birthdate: date | None = None
    gender: str | None = None
    interests: str | None = None
    city: str | None = None


class RegisterUser(BaseModel):
    login: str
    first_name: str
    last_name: str
    birthdate: date | None = None
    gender: str | None = None
    interests: str | None = None
    city: str | None = None
    password: str


class RegisterResponse(BaseModel):
    user_id: str


class SearchUser(BaseModel):
    first_name: str
    last_name: str
