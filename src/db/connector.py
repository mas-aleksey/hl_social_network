import logging
from typing import AsyncIterator

import asyncpg


logger = logging.getLogger("[PostgresDB]")


class PostgresDB:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self.pool = None

    async def connect(self) -> None:
        if self.pool is not None:
            return

        self.pool = await asyncpg.create_pool(dsn=self._dsn, statement_cache_size=0)
        await self.pool.fetch("SET TIME ZONE 'UTC';")
        logger.info("Connected to database")

    async def disconnect(self) -> None:
        if self.pool is None:
            return
        await self.pool.close()
        self.pool = None
        logger.info("Disconnected from database")


db: PostgresDB | None = None


async def get_db_connection() -> AsyncIterator[asyncpg.Connection]:
    if db is None:
        raise ValueError("Database is not initialized")

    async with db.pool.acquire() as conn:
        yield conn
