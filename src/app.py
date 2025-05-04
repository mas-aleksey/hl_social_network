from contextlib import asynccontextmanager
from types import AsyncGeneratorType

from fastapi import FastAPI

from db import connector
from settings import get_settings
from user.router import router as user_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGeneratorType:
    settings = get_settings()
    connector.db = connector.PostgresDB(dsn=settings.DB_URI)
    await connector.db.connect()
    yield
    await connector.db.disconnect()


app = FastAPI(
    description="Service issues SSL certificate and upload it to Barbican",
    lifespan=lifespan,
)


app.include_router(user_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8000)
