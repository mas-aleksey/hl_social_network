import asyncio
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from random import randint
from time import monotonic

import bcrypt
import pytest
from httpx import AsyncClient

from db.connector import PostgresDB
from user.auth import make_token


REQUEST_COUNT = 5000


@pytest.fixture
def user_data_file() -> Path:
    current_dir = Path(__file__).parent.resolve(strict=True)
    return current_dir / "people.csv"


@pytest.fixture
async def user_db(db: PostgresDB, user_data_file: Path) -> list[tuple]:
    user_data = []
    time_start = datetime.now()
    psw = bcrypt.hashpw("top_secret_password".encode(), bcrypt.gensalt())
    async with db.pool.acquire() as conn:
        with user_data_file.open("r") as file:
            for i, line in enumerate(file):
                row = line.split(",")
                first_name, last_name = row[0].split(" ")
                birthdate = date.fromisoformat(row[1])
                user_data.append(
                    (str(i), first_name, last_name, birthdate, "-", "high load projects", row[2], psw),
                )
        await conn.executemany("INSERT INTO users VALUES ($1, $2, $3, $4, $5, $6, $7, $8)", user_data)
    print(f"Generated users in {datetime.now() - time_start}")
    return user_data


@dataclass
class Statistics:
    count: int
    start_time: datetime
    end_time: datetime = field(init=False)
    latencies: list[float] = field(default_factory=list)

    def show(self) -> None:
        total_time = round((self.end_time - self.start_time).total_seconds(), 2)
        rps = round(self.count / total_time, 2)
        min_latency = min(self.latencies)
        max_latency = max(self.latencies)
        avg_latency = round(sum(self.latencies) / len(self.latencies), 2)

        print(f"Request count: {self.count}")
        print(f"Total time: {total_time}s")
        print(f"Requests per second: {rps}")
        print(f"Min latency: {min_latency}ms")
        print(f"Max latency: {max_latency}ms")
        print(f"Average latency: {avg_latency}ms")


@pytest.fixture
async def timeit_request(xclient: AsyncClient, db: PostgresDB, user_db: list[tuple]) -> callable:
    async with db.pool.acquire() as conn:
        count = await conn.fetchval("SELECT COUNT(*) FROM users")
    headers = {"Authorization": f"Bearer {make_token("0")}"}

    async def inner(request_per_thread: int, stat: Statistics) -> None:
        for _ in range(request_per_thread):
            start_time = monotonic()
            i = randint(0, count - 1)
            params = {"first_name": user_db[i][1][:3], "last_name": user_db[i][2][:3]}
            await xclient.get("/user/search", params=params, headers=headers)
            latency = round(1000.0 * (monotonic() - start_time), 3)
            stat.latencies.append(latency)

    return inner


@pytest.mark.parametrize("thread_count", [1, 10, 100, 1000])
async def test_high_load_without_index(timeit_request: callable, thread_count: int) -> None:
    request_per_thread = REQUEST_COUNT // thread_count
    stat = Statistics(REQUEST_COUNT, datetime.now())

    await asyncio.gather(
        *[asyncio.create_task(timeit_request(request_per_thread, stat)) for _ in range(thread_count)],
    )
    stat.end_time = datetime.now()
    stat.show()


@pytest.mark.parametrize("thread_count", [1, 10, 100, 1000])
async def test_high_load_with_index(db: PostgresDB, timeit_request: callable, thread_count: int) -> None:
    async with db.pool.acquire() as conn:
        await conn.execute("CREATE INDEX users_name_id_idx ON users(first_name, last_name, id);")
    request_per_thread = REQUEST_COUNT // thread_count
    stat = Statistics(REQUEST_COUNT, datetime.now())

    await asyncio.gather(
        *[asyncio.create_task(timeit_request(request_per_thread, stat)) for _ in range(thread_count)],
    )
    stat.end_time = datetime.now()
    stat.show()


async def test_high_load_with_index_explain(db: PostgresDB, timeit_request: callable, user_db: list[tuple]) -> None:
    async with db.pool.acquire() as conn:
        await conn.execute("CREATE INDEX users_name_id_idx ON users(first_name, last_name, id);")
        count = await conn.fetchval("SELECT COUNT(*) FROM users")
        i = randint(0, count - 1)
        first_name, last_name = user_db[i][1][:3], user_db[i][2][:3]
        result = await conn.fetch(
            "EXPLAIN ANALYZE SELECT * FROM users WHERE first_name LIKE $1 AND last_name LIKE $2 ORDER BY id",
            f"{first_name}%",
            f"{last_name}%",
        )
        print("\n")
        for row in result:
            print(next(row.values()))
