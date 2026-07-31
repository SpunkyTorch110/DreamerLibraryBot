from contextlib import asynccontextmanager
from pathlib import Path
from db.schemas import initialize as init_schema

import aiosqlite

class Database:

    def __init__(self, path: str):
        self.path = Path(path)

    async def initialize(self):
        """
        Creates the db file and parent directories if needed.
        """

        self.path.parent.mkdir(parents=True, exist_ok=True)

        async with aiosqlite.connect(self.path) as connection:
            await init_schema(connection)

    @asynccontextmanager
    async def connection(self):
        connection = await aiosqlite.connect(self.path)
        connection.row_factory = aiosqlite.Row

        try:
            yield connection
            await connection.commit()
        except Exception:
            await connection.rollback()
            raise
        finally:
            await connection.close()