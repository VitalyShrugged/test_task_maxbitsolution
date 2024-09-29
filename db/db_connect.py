import asyncio
import logging

import asyncpg
from config.config import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_USER,
    POSTGRES_PORT,
)


class AsyncDBConnect:
    def __init__(self):
        self.connection = None
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)

    async def connect(self):
        try:
            self.connection = await asyncpg.connect(
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                database=POSTGRES_DB,
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
            )
            self.logger.info("Подключено к базе данных")
            return self.connection
        except asyncpg.PostgresError as e:
            self.logger.error(f"Ошибка при подключении к БД: {e}")

    async def disconnect(self):
        if self.connection:
            await self.connection.close()
            self.logger.info("Отключено от базы данных")

    async def create_tables(self) -> None:
        try:
            if not self.connection:
                await self.connect()
            await self.connection.execute(
                """CREATE TABLE IF NOT EXISTS users (
                                            id SERIAL PRIMARY KEY,
                                            user_id BIGINT UNIQUE,
                                            password TEXT,
                                            username TEXT UNIQUE
                                        )
                                        """
            )
            await self.connection.execute(
                """CREATE TABLE IF NOT EXISTS tasks (
                            id SERIAL PRIMARY KEY,
                            user_id BIGINT,
                            title TEXT,
                            description TEXT,
                            is_done BOOLEAN DEFAULT FALSE,
                            FOREIGN KEY(user_id) REFERENCES users(user_id)
                        )"""
            )
            self.logger.info("Таблица и индекс успешно созданы")
        except asyncpg.PostgresError as e:
            self.logger.error(f"Ошибка создания таблицы: {e}")

    async def execute_query(self, query, *params):
        async with self.lock:
            if not self.connection:
                await self.connect()
            try:
                await self.connection.execute(query, *params)
            except asyncpg.PostgresError as e:
                self.logger.error(f"Ошибка выполнения запроса: {e}")

    async def fetch_query(self, query, *params):
        async with self.lock:
            if not self.connection:
                await self.connect()
            try:
                result = await self.connection.fetch(query, *params)
                return result
            except asyncpg.PostgresError as e:
                self.logger.error(f"Ошибка выполнения запроса: {e}")
                return []
