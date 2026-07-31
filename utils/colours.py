import discord
from discord import Colour

class Colours:

    SUCCESS = discord.Colour.green()

    WARNING = discord.Colour.orange()

    ERROR = discord.Colour.red()

    INFO = discord.Colour.blurple()


def ping_colour(ping: int) -> Colour:

    if ping <= 80:
        return Colour.green()

    if ping <= 150:
        return Colour.gold()

    if ping <= 250:
        return Colour.orange()

    return Colour.red()
