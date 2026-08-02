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

