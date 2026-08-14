from datetime import timedelta

from dotenv import load_dotenv
import os

from enums.rarity import Rarity

load_dotenv()

# the discord bot token of your bot
TOKEN = os.getenv("DISCORD_TOKEN")

# the discord id of the admins of the bot
ADMIN_IDS = {
    int(admin_id.strip())
    for admin_id in os.getenv("DISCORD_ADMIN_IDS", "").split(",")
    if admin_id.strip()
}

# the location and name of the database file for the bots data
DATABASE = "data/dreamerlibrarybot.db"

# the id of the bot creator
BOT_CREATOR = os.getenv("BOT_CREATOR")

# status on the discord bot
DISCORD_STATUS = "v1.0 | Use /roll to start"

# amount of players shown in the leaderboard
MAX_LEADERBOARD_PLAYERS = 8

# amount of pages that appear per page in the list
MAX_PAGES_PER_PAGE = 20

# amount of collections shown in a single page of collections listing
COLLECTION_PAGE_SIZE = 6

# amount of pages to skip in gallery viewing
GALLERY_JUMP_SIZE = 5

# max amount of rolls a player can have
MAX_ROLLS = 6

# max amount of claims a player can have
MAX_CLAIMS = 2

# amount of rolls the player starts with initially
STARTING_ROLLS = 3

# amount of claims the players starts with initially
STARTING_CLAIMS = 1

# sell values of each star type
ROLL_SELL_VALUES = {
    Rarity.SINGLE_STAR: 2,
    Rarity.DOUBLE_STAR: 5,
    Rarity.TRIPLE_STAR: 10,
}

# drop chances to get the rarities while rolling
SINGLE_STAR_DROP_CHANCE = 55
DOUBLE_STAR_DROP_CHANCE = 30
TRIPLE_STAR_DROP_CHANCE = 15

# amount of time for a roll and claim to recharge with and without an upgrade

ROLL_RECHARGE = timedelta(hours=4)
ROLL_RECHARGE_UPGRADED = timedelta(hours=3)

CLAIM_RECHARGE = timedelta(hours=12)
CLAIM_RECHARGE_UPGRADED = timedelta(hours=10)


# shop cost for the roll and claim upgrade

ROLL_UPGRADE_COST = 100
CLAIM_UPGRADE_COST = 100