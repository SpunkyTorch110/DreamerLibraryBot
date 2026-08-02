import aiosqlite

from db.repositories.base_repository import BaseRepository
from datetime import datetime

from models.schema.player import Player

class PlayerRepository(BaseRepository):

    def _map(self, row: aiosqlite.Row) -> Player:
        return Player(
            discord_id=row["discord_id"],
            username=row["username"],
            display_name=row["display_name"],
            gold=row["gold"],
            last_roll=self.from_database_datetime(row["last_roll"]),
            last_claim=self.from_database_datetime(row["last_claim"]),
            created_at=self.from_database_datetime(row["created_at"]),
            rolls_remaining=row["rolls_remaining"],
            claims_remaining=row["claims_remaining"],
        )

    async def create(self, player: Player, tx=None) -> Player:
            cursor = await self.execute(
                """
                INSERT INTO players
                (discord_id,
                 username,
                 display_name,
                 gold,
                 last_roll,
                 last_claim,
                 rolls_remaining,
                 claims_remaining,
                 created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    player.discord_id,
                    player.username,
                    player.display_name,
                    player.gold,
                    self.to_database_datetime(player.last_roll),
                    self.to_database_datetime(player.last_claim),
                    player.rolls_remaining,
                    player.claims_remaining,
                    self.to_database_datetime(player.created_at)
                ),
                tx
            )

            player.discord_id = cursor.lastrowid

            return player

    async def get(self, discord_id: int, tx=None) -> Player | None:
        row = await self.fetch_one(
            """
            SELECT *
            FROM players
            WHERE discord_id = ?
            """,
            (discord_id,),
            tx
        )

        return None if row is None else self._map(row)

    async def exists(self, discord_id: int, tx=None) -> bool:
        return await self.query_exists(
            """
            SELECT EXISTS(SELECT 1
                          FROM players
                          WHERE discord_id = ?)
            """,
            (discord_id,),
            tx
        )

    async def delete(self, discord_id: int, tx=None):
        await self.execute(
            """
            DELETE
            FROM players
            WHERE discord_id = ?
            """,
            (discord_id,),
            tx
        )

    async def get_all(self, tx=None) -> list[Player]:
        rows = await self.fetch_all(
            """
            SELECT *
            FROM players
            ORDER BY username
            """,
            (),
            tx
        )

        return [self._map(row) for row in rows]

    async def update(self, player: Player, tx=None):
        await self.execute(
            """
            UPDATE players
            SET username     = ?,
                display_name = ?,
                gold         = ?,
                last_roll    = ?,
                last_claim   = ?,
                rolls_remaining   = ?,
                claims_remaining  = ?
            WHERE discord_id = ?
            """,
            (
                player.username,
                player.display_name,
                player.gold,
                self.to_database_datetime(player.last_roll),
                self.to_database_datetime(player.last_claim),
                player.rolls_remaining,
                player.claims_remaining,
                player.discord_id
            ),
            tx
        )

    async def update_username(
            self,
            discord_id: int,
            username: str,
            tx=None
    ):
            await self.execute(
                """
                UPDATE players
                SET username = ?
                WHERE discord_id = ?
                """,
                (username, discord_id),
                tx
            )

    async def update_display_name(
            self,
            discord_id: int,
            display_name: str | None,
            tx=None
    ):
            await self.execute(
                """
                UPDATE players
                SET display_name = ?
                WHERE discord_id = ?
                """,
                (display_name, discord_id),
                tx
            )

    async def set_gold(
            self,
            discord_id: int,
            gold: int,
            tx=None
    ):
            await self.execute(
                """
                UPDATE players
                SET gold = ?
                WHERE discord_id = ?
                """,
                (gold, discord_id),
                tx
            )

    async def add_gold(
            self,
            discord_id: int,
            amount: int,
            tx=None,
    ):
            await self.execute(
                """
                UPDATE players
                SET gold = gold + ?
                WHERE discord_id = ?
                """,
                (amount, discord_id),
                tx
            )

    async def remove_gold(
            self,
            discord_id: int,
            amount: int,
            tx=None
    ):
            await self.execute(
                """
                UPDATE players
                SET gold = MAX(0, gold - ?)
                WHERE discord_id = ?
                """,
                (amount, discord_id),
                tx
            )

    async def set_last_roll(
            self,
            discord_id: int,
            timestamp: datetime,
            tx=None,
    ):
            await self.execute(
                """
                UPDATE players
                SET last_roll = ?
                WHERE discord_id = ?
                """,
                (
                    self.to_database_datetime(timestamp),
                    discord_id
                ),
                tx
            )

    async def set_last_claim(
            self,
            discord_id: int,
            timestamp: datetime,
            tx=None,
    ):
            await self.execute(
                """
                UPDATE players
                SET last_claim = ?
                WHERE discord_id = ?
                """,
                (
                    self.to_database_datetime(timestamp),
                    discord_id
                ),
                tx
            )

    async def set_rolls_remaining(
            self,
            discord_id: int,
            rolls_remaining: int,
            tx=None
    ):
        await self.execute(
            """
            UPDATE players
            SET rolls_remaining = ?
            WHERE discord_id = ?
            """,
            (rolls_remaining, discord_id),
            tx
        )

    async def consume_roll(
            self,
            discord_id: int,
            tx=None
    ):
        await self.execute(
            """
            UPDATE players
            SET rolls_remaining = MAX(0, rolls_remaining - 1)
            WHERE discord_id = ?
            """,
            (discord_id,),
            tx
        )

    async def reset_rolls_remaining(
            self,
            discord_id: int,
            rolls_remaining: int,
            tx=None
    ):
        await self.execute(
            """
            UPDATE players
            SET rolls_used = ?
            WHERE discord_id = ?
            """,
            (rolls_remaining, discord_id),
            tx
        )

    async def reset_roll_and_claim_usage(
            self,
            discord_id: int,
            rolls_remaining: int,
            claims_remaining: int,
            tx=None
    ):
        await self.execute(
            """
            UPDATE players
            SET rolls_remaining  = ?,
                claims_remaining = ?
            WHERE discord_id = ?
            """,
            (rolls_remaining, claims_remaining, discord_id),
            tx
        )