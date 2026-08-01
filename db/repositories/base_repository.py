from datetime import datetime

import aiosqlite

from db.database import Database


class BaseRepository:

    def __init__(self, database: Database):
        self._database = database

    @property
    def database(self) -> Database:
        return self._database

    @staticmethod
    def to_database_datetime(value: datetime | None) -> float | None:
        return value.timestamp() if value else None

    @staticmethod
    def from_database_datetime(value: float | None) -> datetime |None:
        return datetime.fromtimestamp(value) if value else None

    async def execute(
            self,
            query: str,
            parameters: tuple = ()
    ) -> int:
        """
        Executes INSERT, UPDATE or DELETE.

        Returns the number of affected rows.
        """

        async with self.database.connection() as db:
            cursor = await db.execute(query, parameters)
            return cursor.rowcount

    async def fetch_one(
            self,
            query: str,
            parameters: tuple = ()
    ) -> aiosqlite.Row | None:
        """
        Executes a SELECT returning a single row.
        """

        async with self.database.connection() as db:
            cursor = await db.execute(query, parameters)
            return await cursor.fetchone()

    async def fetch_all(
            self,
            query: str,
            parameters: tuple = ()
    ) -> list[aiosqlite.Row]:
        """
        Executes a SELECT returning multiple rows.
        """

        async with self.database.connection() as db:
            cursor = await db.execute(query, parameters)
            return await cursor.fetchall()

    async def query_exists(
            self,
            query: str,
            parameters: tuple = ()
    ) -> bool:
        """
        Executes a SELECT EXISTS(...) query.
        """

        row = await self.fetch_one(query, parameters)

        return bool(row[0]) if row else False