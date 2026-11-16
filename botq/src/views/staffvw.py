import asyncio
import datetime

import hikari
import miru

from ..bot.machine import client
from ..data.data import config, Data

STAFF_ROLES = {
    "Moderator": 1202912717648699402,
    "Control": 1202912639458480128,
    "Support": 1202912477864656947,
    "Media": 1202912410546081843,
    "Broadcaster": 1202912257533677619,
    "Helper": 1202911893619212318
}

class ViewSample(miru.View):
    def __init__(self):
        super().__init__(timeout = None)
    
    # async def view_check(self, ctx: miru.ViewContext) -> bool:
    #     ...
        
    # async def on_error(self, error: Exception, item: miru.abc.ViewItem | None = None, ctx: miru.ViewContext | None = None) -> None:
    #     ...
        
class SelectRole(ViewSample):
    
    @miru.text_select(
        options = [
            miru.SelectOption(
                label = role, 
                emoji = f"<:{role}:{emojiId}>"
            ) 
            for role, emojiId in STAFF_ROLES.items()
        ],
        placeholder = "Выберите staff роль!",
        max_values = 1
    )
    async def select_staff(self, ctx: miru.ViewContext, select: miru.MentionableSelect):
        staff_config = Data().staff
        
        embed = (
            hikari.Embed(
                title = select.values[0],
                colour = 0x313236
            )
            .add_field(
                name = staff_config[select.values[0]]["requirement"]["name"],
                value = staff_config[select.values[0]]["requirement"]["value"]
            )
            .add_field(
                name = staff_config[select.values[0]]["WN"]["name"],
                value = staff_config[select.values[0]]["WN"]["value"]
            )
            .set_image(
                "https://f8n-production-collection-assets.imgix.net/0xb932a70A57673d89f4acfFBE830E8ed7f75Fb9e0/7859/nft.gif?q=80&auto=compress&cs=srgb&h=640"
            )
        )
        
        view = ModalView(select.values[0])
        
        await ctx.respond(embed = embed, components = view, flags = hikari.MessageFlag.EPHEMERAL)
        client.start_view(view)
        
class ModalView(miru.View):
    def __init__(self, role):
        self._role = role
        
        super().__init__(timeout = None)
         
    @miru.button(label="Подать заявку", style=hikari.ButtonStyle.PRIMARY)
    async def modal_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        modal = RequestModal(title="Заявка", role = self._role)
        
        await ctx.respond_with_modal(modal)
        client.start_modal(modal)
                
class RequestModal(miru.Modal):
    def __init__(self, title, role):
        self._role = role
        
        super().__init__(title, timeout = None)
    
    name = miru.TextInput(
        label = "Ваше имя и возраст?",
        placeholder = "Пишите своё имя и возраст",
        required = True
    )

    time = miru.TextInput(
        label = "Ваш часовой пояс?",
        placeholder = "МСК +3",
        value = "МСК +3",
        required = True
    )
    
    time_required = miru.TextInput(
        label = "Сколько времени Вы готовы уделять проекту?",
        placeholder = "2 часа",
        required = True
    )
    
    rule = miru.TextInput(
        label = "Оцените ваше знание правил сервера и Discord",
        placeholder = "Там 13 лет в общем да",
        required = True,
        style = hikari.TextInputStyle.PARAGRAPH
    )
    
    exp =  miru.TextInput(
        label = "Был ли у Вас опыт в выбранной должности?",
        placeholder = "Я был на том-то том-то сервере",
        required = True,
        style = hikari.TextInputStyle.PARAGRAPH
    )

    async def callback(self, ctx: miru.ModalContext) -> None:
        embed = (
            hikari.Embed(
                colour = 0x313236
            )
            .add_field(
                name = "Имя",
                value = f"<@{ctx.author.id}>",
                inline = True
            )
            .add_field(
                name = "ID",
                value = ctx.author.id,
                inline = True
            )
            .add_field(
                name = "Заявка на:",
                value = f"<:{self._role}:{STAFF_ROLES[self._role]}> {self._role}",
                inline = True
            )
            .set_thumbnail(
                ctx.author.make_avatar_url()
            )
        )
        
        for key, item in vars(self)["_values"].items():
            embed.add_field(name = key.label, value = item)
        
        view = StaffSuccess(self._role)
                
        channel: hikari.TextableChannel = ctx.get_guild().get_channel(config["channelsFS"]["channelWSM"])
        
        await channel.send(embed = embed, components = view)
        client.start_view(view)
        
        await ctx.respond("Сообщение будет в скором времени рассмотрено!", flags = hikari.MessageFlag.EPHEMERAL)
        
class StaffSuccess(miru.View):
    def __init__(self, role):
        self._role = role
        
        super().__init__(timeout = None)
        
    @miru.button(label = "Принять", style = hikari.ButtonStyle.SUCCESS, custom_id = "accept")
    async def success(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        member = ctx.get_guild().get_member(self.message.embeds[0].fields[1].value)
        
        if config["rolesFS"]["staff"][self._role] in member.role_ids:
            await ctx.respond("Он уже принят!", flags = hikari.MessageFlag.EPHEMERAL)
            return
        
        embed = (
            hikari.Embed(
                colour = 0x313236
            )
            .set_author(
                name = "ㅤㅤㅤㅤㅤㅤㅤВас приняли в Staff!"
            )
            .set_image(
                "https://static.wikia.nocookie.net/b6ec2461-ebba-4d77-8698-c675555ffd88"
            )
        )
        
        asyncio.gather(
            member.add_role(config["rolesFS"]["staff"][self._role]),
            
            member.add_role(config["rolesFS"]["staff"]["Staff"]),
            
            member.send(embed = embed),
            
            ctx.respond("Операция завершена", flags = hikari.MessageFlag.EPHEMERAL)
        )
        
        button.disabled = True
        
        self.stop()
        
    @miru.button(label = "Отказ", style = hikari.ButtonStyle.DANGER, custom_id = "refusal")
    async def refuse(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        modal = RefusalModal(title="Причины отказа", role = self._role, member = ctx.get_guild().get_member(self.message.embeds[0].fields[1].value))
        
        await ctx.respond_with_modal(modal)
        client.start_modal(modal)
        
class RefusalModal(miru.Modal):
    def __init__(self, title, role, member):
        self._role = role
        self._member = member
        
        super().__init__(title, timeout = None)
    
    refusal =  miru.TextInput(
        label = "Причина вашего отказа?",
        placeholder = "Хуесос",
        required = True,
        style = hikari.TextInputStyle.PARAGRAPH
    )

    async def callback(self, ctx: miru.ModalContext) -> None:
        embed = (
            hikari.Embed(
                description = self.refusal.value,
                colour = 0x313236
            )
            .set_author(
                name = "ㅤㅤㅤㅤㅤㅤК сожалению, вам отказали!"
            )
            .set_image(
                "https://64.media.tumblr.com/e0598661a0524c3e5367677aca92532d/a59a0e3e3ab43cb7-cd/s500x750/1f8ca62625e0986f39e15c7366915efa86c2cd26.gif"
            )
        )
        
        await self._member.send(embed = embed)