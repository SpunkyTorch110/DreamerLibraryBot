from contextlib import asynccontextmanager
from pathlib import Path

import aiosqlite

from db.schemas import initialize as init_schema


class Database:

    def __init__(self, path: str):
        self.path = Path(path)

    async def initialize(self):
        """
        Creates the database file and initializes the schema.
        """

        self.path.parent.mkdir(parents=True, exist_ok=True)

        async with aiosqlite.connect(self.path) as connection:
            connection.row_factory = aiosqlite.Row
            await init_schema(connection)

    @asynccontextmanager
    async def connection(self):
        """
        Opens a database connection.

        Every repository method can use this directly when no
        transaction is active.
        """

        connection = await aiosqlite.connect(self.path)
        await connection.execute("PRAGMA foreign_keys = ON")
        connection.row_factory = aiosqlite.Row

        try:
            yield connection
            await connection.commit()
        except Exception:
            await connection.rollback()
            raise
        finally:
            await connection.close()

    @asynccontextmanager
    async def transaction(self):
        """
        Opens a database transaction that can be shared across
        multiple repository calls.
        """

        async with self.connection() as connection:
            yield connection