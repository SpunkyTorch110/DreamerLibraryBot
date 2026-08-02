import discord


class PlayerService:

    def __init__(self, bot):
        self.bot = bot

    async def get_discord_user(
            self,
            user_id: int | None
    ) -> discord.User | None:

        if user_id is None:
            return None

        # Try the cache first
        user = self.bot.get_user(user_id)

        if user is not None:
            return user

        # Fetch from Discord if not cached
        try:
            return await self.bot.fetch_user(user_id)
        except discord.NotFound:
            return None
        except discord.HTTPException:
            return None