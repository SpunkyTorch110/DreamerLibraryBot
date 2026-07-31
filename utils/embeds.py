from __future__ import annotations
from typing import Iterable

import discord

class EmbedFactory:

    @staticmethod
    def create(
        *,
        title: str | None = None,
        description: str | None = None,
        colour: discord.Colour = discord.Colour.blurple(),
        url: str | None = None,
        timestamp=None,

        author_name: str | None = None,
        author_url: str | None = None,
        author_icon: str | None = None,

        thumbnail: str | None = None,
        image: str | None = None,

        footer_text: str | None = None,
        footer_icon: str | None = None,

        fields: Iterable[tuple[str, str, bool]] | None = None
    ) -> discord.Embed:
        """
        Creates a Discord embed.

        fields format:
            [
                ("Name", "Value", False),
                ("Another", "Another Value", True)
            ]
        """

        embed = discord.Embed(
            title=title,
            description=description,
            colour=colour,
            url=url,
            timestamp=timestamp
        )

        if author_name:
            embed.set_author(
                name=author_name,
                url=author_url,
                icon_url=author_icon
            )

        if thumbnail:
            embed.set_thumbnail(url=thumbnail)

        if image:
            embed.set_image(url=image)

        if footer_text:
            embed.set_footer(
                text=footer_text,
                icon_url=footer_icon
            )

        if fields:
            for name, value, inline in fields:
                embed.add_field(
                    name=name,
                    value=value,
                    inline=inline
                )

        return embed