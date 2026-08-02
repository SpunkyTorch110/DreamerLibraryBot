import discord
from discord import Color, Embed

from embeds.embed_factory import EmbedFactory
from enums.gender import Gender
from enums.page_type import PageType
from enums.rank import Rank
from models.schema import collection
from models.schema.collection import Collection
from models.schema.page import Page
from models.schema.page_image import PageImage
from utils.colours import Colours


def create_page_embed(page: Page, collect: Collection, page_image: PageImage,
                      total_pages: int, original_owner: discord.abc.User | None = None,
                      hide_stats: bool = False) -> Embed:

    collection_name = collect.name if collect else "Unknown"

    gender_emoji = {
        Gender.MALE: "♂️",
        Gender.FEMALE: "♀️",
        Gender.NON_BINARY: "⚧️",
        Gender.UNKNOWN: "❓"
    }[page.gender]

    rank_emoji = "❓" if hide_stats else {
        Rank.F: "🇫",
        Rank.D: "🇩",
        Rank.C: "🇨",
        Rank.B: "🇧",
        Rank.A: "🇦",
        Rank.S: "🇸",
        Rank.SS: "🇸 🇸",
        Rank.SSS: "🇸 🇸 🇸"
    }[page.rank]

    rarity = "⭐" * int(page.rarity)

    stat_prefix = "+" if page.page_type != PageType.CHARACTER else ""

    embed = EmbedFactory.create(
        title=f"{page.name}",
        description=(
            "(Claim this page to learn more about it)"
            if hide_stats
            else page.description
        ),
        colour=Color.gold()
    )

    if original_owner is not None:
        embed.set_author(
            name=f"First Claimed by {original_owner.display_name}",
            icon_url=original_owner.display_avatar.url
        )
    else:
        embed.set_author(
            name="Unclaimed",
            icon_url="https://cdn.discordapp.com/embed/avatars/0.png"
        )

    # Top information
    embed.add_field(
        name="Gender",
        value=gender_emoji,
        inline=True
    )

    embed.add_field(
        name="Rank",
        value=rank_emoji,
        inline=True
    )

    embed.add_field(
        name="Rarity",
        value=rarity,
        inline=True
    )

    # First stat row
    if not hide_stats:
        embed.add_field(
            name="💪 STR",
            value=f"**{stat_prefix}{page.strength}**",
            inline=True
        )

        embed.add_field(
            name="🏹 DEX",
            value=f"**{stat_prefix}{page.dexterity}**",
            inline=True
        )

        embed.add_field(
            name="❤️ CON",
            value=f"**{stat_prefix}{page.constitution}**",
            inline=True
        )

        # Second stat row
        embed.add_field(
            name="🧠 INT",
            value=f"**{stat_prefix}{page.intelligence}**",
            inline=True
        )

        embed.add_field(
            name="🙏 WIS",
            value=f"**{stat_prefix}{page.wisdom}**",
            inline=True
        )

        embed.add_field(
            name="✨ CHA",
            value=f"**{stat_prefix}{page.charisma}**",
            inline=True
        )

    embed.set_image(url=page_image.image_url)

    embed.set_footer(
        text=f"{collection_name} • {page.page_type.name.title()} • Page {page.id}/{total_pages}"
    )

    return embed