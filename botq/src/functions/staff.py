import datetime
import asyncio

import lightbulb
import hikari

from src.bot.machine import bot, client
from views.staffvw import SelectRole
from src.data.data import config
from functions.support import SupportCommands

STAFF_DESCRIPTION = {
    "1193123956824211467": "Cледит за порядком в голосовых каналах.",
    "1193540510795706470": "Cледит за порядком в текстовых каналах.",
    "1192887536503238818": "Верифицирует новых участников.",
    "1192017081093337170": "Занимается пиаром проекта и поиском новых участников на сервер.",
    "1193505537371930685": "Проводит различные мероприятия и трибуны.",
    "1193247640524181625": "Продвигает сервер благодаря прописыванию команд."
}

class StaffCommands(SupportCommands):
    
    @bot.command
    @lightbulb.add_checks(lightbulb.has_roles(config["rolesFS"]["developer"]))
    @lightbulb.command("staff", "Используйте эту команду если что-то идёт не по плану)!", ephemeral = True, auto_defer = True)
    @lightbulb.implements(lightbulb.SlashCommand)
    async def update_staff_request(ctx: lightbulb.Context):
        view = SelectRole()
        
        embed = (
            hikari.Embed(
                colour = 0x313236
            )
            .set_image(
                "https://64.media.tumblr.com/fe9b4f8b9aa6a0c37f5928c3123a7153/b981e7ca6d41deb4-f4/s500x750/223edc48ca9cc72cdff0e51894786fd24dff678e.gif"
            )
        )
        
        for role, item in STAFF_DESCRIPTION.items():
            embed.add_field(
                name = "ㅤ",
                value = f"<a:plasma:1203268812171124787> <@&{role}>\n ```{item}```",
                inline = (not role in ["1192887536503238818", "1192017081093337170"])
            )
        
        channel: hikari.TextableChannel = ctx.get_guild().get_channel(config["channelsFS"]["channelWS"])
        
        await asyncio.gather(
            channel.delete_messages(channel.fetch_history()),
            
            channel.send(embed = embed, components = view), 
            
            ctx.respond(
                "Сообщение отправлено куда нужно, также удалены другие сообщение!",
                
                flags = hikari.MessageFlag.EPHEMERAL
            )
        )

        client.start_view(view)
        
    @bot.command
    @lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MODERATE_MEMBERS))
    @lightbulb.option("user", "имя или индефикатор юзера", hikari.OptionType.USER, required = True)
    @lightbulb.option("time", "Укажите время в таком формате дд/мм/гг чч:мм:сс", hikari.OptionType.STRING, required = True)
    @lightbulb.command("timeout", "Тайм-аут нахуй", ephemeral = True, auto_defer = True)
    @lightbulb.implements(lightbulb.SlashCommand)
    async def timeout(ctx: lightbulb.Context):
        duration = datetime.datetime.strptime(ctx.options.time, '%d/%m/%y %H:%M:%S')
        
        user: hikari.Member = ctx.options.user
        
        await user.edit(communication_disabled_until = duration)
        
        await ctx.respond(f'{user.mention} был выдан тайм-аут на время {duration}')

        
        