import aiosqlite

from db.repositories.base_repository import BaseRepository
from datetime import datetime

from models.leaderboard_entry import LeaderboardEntry
from models.schema.player import Player

class PlayerRepository(BaseRepository):

    def _map(self, row: aiosqlite.Row) -> Player:
        return Player(
            discord_id=row["discord_id"],
            username=row["username"],
            display_name=row["display_name"],

            gold=row["gold"],

            rolls_remaining=row["rolls_remaining"],
            claims_remaining=row["claims_remaining"],

            next_roll_at=self.from_database_datetime(row["next_roll_at"]),
            next_claim_at=self.from_database_datetime(row["next_claim_at"]),

            created_at=self.from_database_datetime(row["created_at"])
        )

    async def create(self, player: Player, tx=None) -> Player:
            await self.execute(
                """
                INSERT INTO players
                (discord_id,
                 username,
                 display_name,
                 gold,
                 next_roll_at,
                 next_claim_at,
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
                    self.to_database_datetime(player.next_roll_at),
                    self.to_database_datetime(player.next_claim_at),
                    player.rolls_remaining,
                    player.claims_remaining,
                    self.to_database_datetime(player.created_at)
                ),
                tx
            )

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
            SET username          = ?,
                display_name      = ?,
                gold              = ?,
                next_roll_at      = ?,
                next_claim_at     = ?,
                rolls_remaining   = ?,
                claims_remaining  = ?
            WHERE discord_id = ?
            """,
            (
                player.username,
                player.display_name,
                player.gold,
                self.to_database_datetime(player.next_roll_at),
                self.to_database_datetime(player.next_claim_at),
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

    async def create_if_missing(
            self,
            player: Player,
            tx=None
    ):
        await self.execute(
            """
            INSERT
            OR IGNORE INTO players
            (
                discord_id,
                username,
                display_name,
                gold,
                next_roll_at,
                next_claim_at,
                rolls_remaining,
                claims_remaining,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                player.discord_id,
                player.username,
                player.display_name,
                player.gold,
                self.to_database_datetime(player.next_roll_at),
                self.to_database_datetime(player.next_claim_at),
                player.rolls_remaining,
                player.claims_remaining,
                self.to_database_datetime(player.created_at)
            ),
            tx
        )

    async def total_gold(self, tx=None) -> int:
        row = await self.fetch_one(
            """
            SELECT COALESCE(SUM(gold), 0) AS total
            FROM players
            """,
            (),
            tx
        )

        return row["total"]

    async def get_top_pages(
            self,
            limit: int = 5,
            connection=None
    ) -> list[LeaderboardEntry]:
        rows = await self.fetch_all(
            """
            SELECT p.discord_id,
                   p.display_name,
                   COALESCE(SUM(i.amount), 0) AS total
            FROM players p
                     LEFT JOIN inventory i
                               ON i.player_id = p.discord_id
            GROUP BY p.discord_id
            ORDER BY total DESC, p.display_name LIMIT ?
            """,
            (limit,),
            connection
        )

        return [
            LeaderboardEntry(
                discord_id=row["discord_id"],
                username=row["display_name"],
                value=row["total"]
            )
            for row in rows
        ]

    async def get_top_first_claims(
            self,
            limit: int = 5,
            connection=None
    ) -> list[LeaderboardEntry]:
        rows = await self.fetch_all(
            """
            SELECT p.discord_id,
                   p.display_name,
                   COUNT(pg.id) AS total
            FROM players p
                     LEFT JOIN pages pg
                               ON pg.owner_id = p.discord_id
            GROUP BY p.discord_id
            ORDER BY total DESC, p.display_name LIMIT ?
            """,
            (limit,),
            connection
        )

        return [
            LeaderboardEntry(
                discord_id=row["discord_id"],
                username=row["display_name"],
                value=row["total"]
            )
            for row in rows
        ]

    async def get_top_gold(
            self,
            limit: int = 5,
            connection=None
    ) -> list[LeaderboardEntry]:
        rows = await self.fetch_all(
            """
            SELECT discord_id,
                   display_name,
                   gold
            FROM players
            ORDER BY gold DESC, display_name LIMIT ?
            """,
            (limit,),
            connection
        )

        return [
            LeaderboardEntry(
                discord_id=row["discord_id"],
                username=row["display_name"],
                value=row["gold"]
            )
            for row in rows
        ]

    async def count(self, tx=None) -> int:
        row = await self.fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM players
            """,
            (),
            tx
        )

        return row["count"]

    async def get_gold(
            self,
            discord_id: int,
            tx=None
    ) -> int:
        row = await self.fetch_one(
            """
            SELECT gold
            FROM players
            WHERE discord_id = ?
            """,
            (discord_id,),
            tx
        )

        return 0 if row is None else row[0]

    async def get_completion_leaderboard(
            self,
            limit: int = 5,
            tx=None
    ):
        rows = await self.fetch_all(
            """
            SELECT p.discord_id,
                   p.username,

                   COALESCE(
                           COUNT(DISTINCT i.page_id) * 100.0
                               / NULLIF(
                                   (SELECT COUNT(*) FROM pages),
                                   0
                                 ),
                           0
                   ) AS completion_percentage

            FROM players p

                     LEFT JOIN inventory i
                               ON i.player_id = p.discord_id
                                   AND i.amount > 0

            GROUP BY p.discord_id,
                     p.username

            ORDER BY completion_percentage DESC,
                     p.discord_id ASC LIMIT ?
            """,
            (
                limit,
            ),
            tx
        )

        return [
            LeaderboardEntry(
                discord_id=row["discord_id"],
                username=row["username"],
                value=row["completion_percentage"]
            )
            for row in rows
        ]