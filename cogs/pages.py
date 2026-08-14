from discord.ext import commands
from discord import app_commands
import discord

from embeds.embed_factory import EmbedFactory
from embeds.page_layout import create_page_embed
from modals.gallery_view import GalleryView
from modals.library_list_view import LibraryListView
from utils.colours import Colours


class Pages(commands.Cog):

    pages = app_commands.Group(
        name="pages",
        description="Browse the DREAMER Library."
    )

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @pages.command(
        name="search",
        description="Searches for a page by name or alias."
    )
    async def search(
            self,
            interaction: discord.Interaction,
            page: str
    ):
        await interaction.response.defer()

        view = await self.bot.page_service.find_discovered_page(page)

        if view is None or not view.page.discovered:
            embed = EmbedFactory.create(
                title="Unknown Page",
                description="No page matching your search has been discovered yet or doesn't exist.",
                colour=Colours.INFO
            )

            embed.set_thumbnail(
                url=self.bot.user.display_avatar.url
            )

            await interaction.followup.send(
                embed=embed
            )
            return

        owner = await self.bot.player_service.get_discord_user(
            view.page.owner_id
        )

        total_pages = await self.bot.page_service.get_total_pages()

        embed = create_page_embed(
            page=view.page,
            collect=view.collection,
            page_image=view.image,
            total_pages=total_pages,
            original_owner=owner,
            hide_stats=view.page.owner_id is None
        )

        await interaction.followup.send(
            embed=embed
        )

    @pages.command(
        name="list",
        description="Lists every page in the library."
    )
    async def list_pages(
            self,
            interaction: discord.Interaction
    ):
        await interaction.response.defer()

        entries = await self.bot.page_service.get_library_entries()

        view = LibraryListView(
            bot=self.bot,
            entries=entries,
            owner_id=interaction.user.id
        )

        message = await interaction.followup.send(
            embed=view.build_embed(),
            view=view,
            wait=True
        )

        view.message = message

    @pages.command(
        name="gallery",
        description="Browse the Library gallery."
    )
    async def gallery(
            self,
            interaction: discord.Interaction
    ):

        await interaction.response.defer()

        gallery = await self.bot.page_service.get_gallery_pages()

        if not gallery:
            embed = EmbedFactory.create(
                title="Gallery",
                description="There are no pages in the library.",
                colour=Colours.INFO
            )

            await interaction.followup.send(
                embed=embed
            )

            return

        view = GalleryView(
            bot=self.bot,
            gallery=gallery,
            owner_id=interaction.user.id
        )

        message = await interaction.followup.send(
            embed=await view.build_embed(),
            view=view,
            wait=True
        )

        view.message = message

    @pages.command(
        name="collection",
        description="Shows all pages belonging to a collection."
    )
    @app_commands.describe(
        name="The name of the collection."
    )
    async def collection(
            self,
            interaction: discord.Interaction,
            name: str
    ):
        await interaction.response.defer()

        result = await self.bot.page_service.get_library_entries_by_collection(
            name
        )

        #
        # Collection does not exist
        #

        if result is None:

            embed = EmbedFactory.create(
                title="📚 Collection Not Found",
                description=(
                    f"No collection named **{name}** was found."
                ),
                colour=Colours.WARNING
            )

            if self.bot.user:
                embed.set_thumbnail(
                    url=self.bot.user.display_avatar.url
                )

            await interaction.followup.send(
                embed=embed
            )

            return

        collection_name, entries = result

        #
        # Collection exists but has no pages
        #

        if not entries:

            embed = EmbedFactory.create(
                title=f"📚 {collection_name}",
                description=(
                    "This collection currently doesn't contain "
                    "any pages."
                ),
                colour=Colours.INFO
            )

            if self.bot.user:
                embed.set_thumbnail(
                    url=self.bot.user.display_avatar.url
                )

            await interaction.followup.send(
                embed=embed
            )

            return

        #
        # Create the paginated list.
        #

        view = LibraryListView(
            bot=self.bot,
            entries=entries,
            owner_id=interaction.user.id,
            title=f"📚 {collection_name} — Page List"
        )

        message = await interaction.followup.send(
            embed=view.build_embed(),
            view=view,
            wait=True
        )

        #
        # Store the message so the View can disable its buttons
        # when it times out.
        #

        view.message = message


async def setup(bot: commands.Bot):
    await bot.add_cog(Pages(bot))