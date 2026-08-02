import discord
from discord import app_commands
from discord.ext import commands

from checks.admin_check import is_admin
from embeds.page_layout import create_page_embed

from enums.gender import Gender
from enums.page_type import PageType
from enums.rank import Rank
from enums.rarity import Rarity
from models.create_page_request import CreatePageRequest
from utils.colours import Colours
from embeds.embed_factory import EmbedFactory


class Admin(commands.Cog):

    admin = app_commands.Group(
        name="admin",
        description="Admin commands."
    )

    def __init__(self, bot):
        self.bot = bot

    @admin.command(
        name="page_create",
        description="Creates a new encyclopedia page."
    )
    @is_admin()
    async def page_create(
            self,
            interaction: discord.Interaction,

            name: str,

            gender: Gender,

            rank: Rank,

            rarity: Rarity,

            page_type: PageType,

            description: str,

            strength: app_commands.Range[int, 0, 30],
            dexterity: app_commands.Range[int, 0, 30],
            constitution: app_commands.Range[int, 0, 30],
            intelligence: app_commands.Range[int, 0, 30],
            wisdom: app_commands.Range[int, 0, 30],
            charisma: app_commands.Range[int, 0, 30],

            collection: str,

            image_url: str
    ):
        await interaction.response.defer(ephemeral=True)

        request = CreatePageRequest(
            name=name,
            gender=gender,
            rank=rank,
            rarity=rarity,
            page_type=page_type,
            description=description,
            strength=strength,
            dexterity=dexterity,
            constitution=constitution,
            intelligence=intelligence,
            wisdom=wisdom,
            charisma=charisma,
            collection=collection,
            image_url=image_url
        )

        page, collection, page_image = await self.bot.admin_service.create_page(request)

        page_count = await self.bot.page_service.get_total_pages()

        embed = create_page_embed(page, collection, page_image, page_count)

        await interaction.followup.send(
            embed=embed,
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Admin(bot))