import dotenv

dotenv.load_dotenv(".env")

from src.functions import support, staff
from src.utils import events

from src.bot.machine import bot

bot.run()