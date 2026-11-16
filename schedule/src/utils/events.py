import lightbulb
import hikari

from ..bot.machine import bot, client
from ..data.data import config

@bot.listen()
async def on_member_join(event: hikari.MemberCreateEvent):
    await event.member.add_role(config["roles"]["unvf"])