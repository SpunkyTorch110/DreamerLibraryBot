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
MAX_LEADERBOARD_PLAYERS = 5

# amount of pages that appear per page in the list
MAX_PAGES_PER_PAGE = 20

# amount of collections shown in a single page of collections listing
COLLECTION_PAGE_SIZE = 10

# amount of pages to skip in gallery viewing
GALLERY_JUMP_SIZE = 5

# time in hours for a single roll recharge to be added
ROLL_RECHARGE = 4

# max amount of rolls a player can have
MAX_ROLLS = 6

# time in hours for a single claim recharge to be added
CLAIM_RECHARGE = 12

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
SINGLE_STAR_DROP_CHANCE = 50
DOUBLE_STAR_DROP_CHANCE = 35
TRIPLE_STAR_DROP_CHANCE = 15