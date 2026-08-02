import discord
from discord import app_commands, Color
from discord.ext import commands

from checks.admin_check import is_admin
from embeds.page_layout import create_page_embed

from enums.gender import Gender
from enums.page_type import PageType
from enums.rank import Rank
from enums.rarity import Rarity
from models.create_page_request import CreatePageRequest

from models.edit_page_general import EditPageGeneralRequest
from models.edit_page_stats import EditPageStatsRequest
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

    @admin.command(
        name="page_alias_add",
        description="Adds an alias to a page."
    )
    @is_admin()
    async def page_alias_add(
            self,
            interaction: discord.Interaction,
            page: str,
            alias: str
    ):
        await interaction.response.defer(ephemeral=True)

        await self.bot.admin_service.add_page_alias(
            page,
            alias
        )

        await interaction.followup.send(
            embed=EmbedFactory.create(
                title="Alias Added",
                description=f"Added **{alias}** to **{page}**.",
                colour=Color.green()
            ),
            ephemeral=True
        )

    @admin.command(
        name="page_delete",
        description="Deletes a page and all related data."
    )
    @is_admin()
    async def page_delete(
            self,
            interaction: discord.Interaction,
            page_name: str
    ):
        await interaction.response.defer(ephemeral=True)

        await self.bot.admin_service.delete_page(page_name)

        embed = EmbedFactory.create(
            title="Page Deleted",
            description=f"Successfully deleted **{page_name}**.",
            colour=Colours.SUCCESS
        )

        await interaction.followup.send(
            embed=embed,
            ephemeral=True
        )

    @admin.command(
        name="page_edit_general",
        description="Edits the general information of a page."
    )
    @is_admin()
    async def page_edit_general(
            self,
            interaction: discord.Interaction,

            page_name: str,

            new_name: str | None = None,

            gender: Gender | None = None,

            rank: Rank | None = None,

            rarity: Rarity | None = None,

            page_type: PageType | None = None,

            collection: str | None = None
    ):
        await interaction.response.defer(ephemeral=True)

        request = EditPageGeneralRequest(
            page_name=page_name,
            new_name=new_name,
            gender=gender,
            rank=rank,
            rarity=rarity,
            page_type=page_type,
            collection=collection
        )

        page = await self.bot.admin_service.edit_page_general(request)

        embed = EmbedFactory.create(
            title="Page Updated",
            description=f"Successfully updated **{page.name}**.",
            colour=Colours.SUCCESS
        )

        await interaction.followup.send(
            embed=embed,
            ephemeral=True
        )

    @admin.command(
        name="page_edit_stats",
        description="Edits the stats of a page."
    )
    @is_admin()
    async def page_edit_stats(
            self,
            interaction: discord.Interaction,

            page_name: str,

            strength: app_commands.Range[int, 0, 999] | None = None,
            dexterity: app_commands.Range[int, 0, 999] | None = None,
            constitution: app_commands.Range[int, 0, 999] | None = None,
            intelligence: app_commands.Range[int, 0, 999] | None = None,
            wisdom: app_commands.Range[int, 0, 999] | None = None,
            charisma: app_commands.Range[int, 0, 999] | None = None,
    ):
        await interaction.response.defer(ephemeral=True)

        request = EditPageStatsRequest(
            page_name=page_name,
            strength=strength,
            dexterity=dexterity,
            constitution=constitution,
            intelligence=intelligence,
            wisdom=wisdom,
            charisma=charisma
        )

        page = await self.bot.admin_service.edit_page_stats(request)

        embed = EmbedFactory.create(
            title="Page Updated",
            description=f"Successfully updated the stats of **{page.name}**.",
            colour=Colours.SUCCESS
        )

        await interaction.followup.send(
            embed=embed,
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Admin(bot))