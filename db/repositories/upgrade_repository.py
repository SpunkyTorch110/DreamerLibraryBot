from db.repositories.base_repository import BaseRepository
from models.schema.player_upgrades import PlayerUpgrades


class UpgradeRepository(BaseRepository):

    @staticmethod
    def _map(row) -> PlayerUpgrades:
        return PlayerUpgrades(
            player_id=row["player_id"],
            roll_upgraded=bool(row["roll_upgraded"]),
            claim_upgraded=bool(row["claim_upgraded"])
        )

    async def get(
            self,
            player_id: int,
            tx=None
    ) -> PlayerUpgrades | None:

        row = await self.fetch_one(
            """
            SELECT
                player_id,
                roll_upgraded,
                claim_upgraded
            FROM upgrades
            WHERE player_id = ?
            """,
            (
                player_id,
            ),
            tx
        )

        if row is None:
            return None

        return self._map(row)

    async def create(
            self,
            upgrades: PlayerUpgrades,
            tx=None
    ):
        await self.execute(
            """
            INSERT INTO upgrades (
                player_id,
                roll_upgraded,
                claim_upgraded
            )
            VALUES (?, ?, ?)
            """,
            (
                upgrades.player_id,
                int(upgrades.roll_upgraded),
                int(upgrades.claim_upgraded)
            ),
            tx
        )

    async def upgrade_roll(
            self,
            player_id: int,
            tx=None
    ) -> bool:

        result = await self.execute(
            """
            UPDATE upgrades
            SET roll_upgraded = 1
            WHERE player_id = ?
              AND roll_upgraded = 0
            """,
            (
                player_id,
            ),
            tx
        )

        return result.rowcount > 0

    async def upgrade_claim(
            self,
            player_id: int,
            tx=None
    ) -> bool:

        result = await self.execute(
            """
            UPDATE upgrades
            SET claim_upgraded = 1
            WHERE player_id = ?
              AND claim_upgraded = 0
            """,
            (
                player_id,
            ),
            tx
        )

        return result.rowcount > 0

    async def has_roll_upgrade(
            self,
            player_id: int,
            tx=None
    ) -> bool:

        row = await self.fetch_one(
            """
            SELECT roll_upgraded
            FROM upgrades
            WHERE player_id = ?
            """,
            (
                player_id,
            ),
            tx
        )

        return row is not None and bool(row["roll_upgraded"])

    async def has_claim_upgrade(
            self,
            player_id: int,
            tx=None
    ) -> bool:

        row = await self.fetch_one(
            """
            SELECT claim_upgraded
            FROM upgrades
            WHERE player_id = ?
            """,
            (
                player_id,
            ),
            tx
        )

        return row is not None and bool(row["claim_upgraded"])