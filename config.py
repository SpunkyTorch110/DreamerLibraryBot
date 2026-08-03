from dotenv import load_dotenv
import os

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

# amount of players shown in the leaderboard
MAX_LEADERBOARD_PLAYERS = 5

# amount of pages that appear per page in the list
MAX_PAGES_PER_PAGE = 20

# amount of pages to skip in gallery viewing
GALLERY_JUMP_SIZE = 5