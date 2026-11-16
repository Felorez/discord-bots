import hikari
import miru

from ..bot.machine import client
from ..data.data import config

REFUSAL_REASONS = ["Профиль пользователя", "Неадекватность", "Меньше 13", "Твинк", "Джампинг", "Отказ от верификации"]

class ViewSample(miru.View):
    async def view_check(self, ctx: miru.ViewContext) -> bool:
        if not config["roles"]["support"] in ctx.member.role_ids:
            await ctx.respond("Динах у тебя нет прав", flags = hikari.MessageFlag.EPHEMERAL)
            return False

        return True

    async def on_error(self, error: Exception, item: miru.abc.ViewItem | None = None, ctx: miru.ViewContext | None = None) -> None:
        if ctx:
            await ctx.respond("Произошла неожиданная ошибка!\n", error)
            return
        
        print(error)
    
class ChangeGender(ViewSample):
    __slots__ = ("__gender", "__memberWhoVF", "__embed",)
    
    def __init__(self, member):
        self.__memberWhoVF: hikari.InteractionMember = member
        self.__gender: str = ""
        
        embed_fields = {
            "Имя": f"```{self.__memberWhoVF}```",
            "ID": f"```{self.__memberWhoVF.id}```",
            "Ник": f"```{self.__memberWhoVF.nickname}```" if self.__memberWhoVF.nickname else f"```Нет никнейма```",
            "Аккаунт Создан": f"<t:{int(self.__memberWhoVF.user.created_at.timestamp())}:d>",
            "Присоединился": f"<t:{int(self.__memberWhoVF.joined_at.timestamp())}:d>"
        }
        
        self.__embed: hikari.Embed = (
            hikari.Embed(
                title = f"Верификация {self.__memberWhoVF}",
                description = "**Для взаимодействия с пользователем, используйте кнопки ниже:**",
                colour = 0x313236
            )
            .set_thumbnail(
                self.__memberWhoVF.make_avatar_url()
            )
            .set_footer(
                "idontnoy.",
                icon = config["developerAvatar"]
            )
        )
        
        for key, item in embed_fields.items():
            self.__embed.add_field(key, item, inline = True)
        
        super().__init__(timeout = None)
        
    @miru.button(label="Мужчина", emoji="", style=hikari.ButtonStyle.PRIMARY, custom_id = "mn-button")
    async def man(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        self.__gender = "man"
        view = Verification(self.__memberWhoVF, self.__gender)
        self.__embed.add_field("Гендер", f"`{self.__gender}`", inline = True)
        
        await ctx.edit_response(embed = self.__embed, components = view, flags = hikari.MessageFlag.EPHEMERAL)
        
        client.start_view(view)
        
        self.stop()
        
    @miru.button(label="Женщина", emoji="", style=hikari.ButtonStyle.DANGER, custom_id = "wm-button")
    async def woman(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        self.__gender = "woman"
        view = Verification(self.__memberWhoVF, self.__gender)
        self.__embed.add_field("Гендер", f"`{self.__gender}`", inline = True)
        
        await ctx.edit_response(embed = self.__embed, components = view, flags = hikari.MessageFlag.EPHEMERAL)
        
        client.start_view(view)
        
        self.stop()

class Verification(ViewSample):
    __slots__ = ("__memberWhoVF", "__gender",)
    
    def __init__(self, member, gender):
        self.__memberWhoVF: hikari.InteractionMember = member
        self.__gender = gender
        
        super().__init__(timeout = None)
        
    
    @miru.button(label="Верифицировать", emoji="", style=hikari.ButtonStyle.SECONDARY, custom_id = "vf-button")
    async def verification(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        await self.__memberWhoVF.add_role(config["gender_roles"][self.__gender])
        embed = (
            hikari.Embed(
                title = f"Вас верифицировали! Саппорт: {ctx.author} ^^",
                colour = 0x313236
            )
        )
        
        await self.__memberWhoVF.remove_role(config["roles"]["unvf"])
        
        await ctx.edit_response(f"{ctx.author.mention}, вы успешно верифицировали пользователя - {self.__memberWhoVF.mention}", components = None, flags = hikari.MessageFlag.EPHEMERAL)
        
        await self.__memberWhoVF.send(embed = embed, components = None, flags = hikari.MessageFlag.EPHEMERAL)
        
        self.stop()
        
    @miru.button(label="Недопуск", emoji="", style=hikari.ButtonStyle.SECONDARY, custom_id = "na-button")
    async def non_admission(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        view = NonAdmission(self.__memberWhoVF)
        embed = (
            hikari.Embed(
                title = f"Причины недопуска",
                colour = 0x313236
            )
        )
        
        await ctx.edit_response(embed = embed, components = view, flags = hikari.MessageFlag.EPHEMERAL)
        
        client.start_view(view)
        
        self.stop()
        
    @miru.button(label="Сменить гендерку", emoji="", style=hikari.ButtonStyle.SECONDARY, custom_id = "cg-button")
    async def change_gender(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        view = ChangeGender(self.__memberWhoVF)
        embed = (
            hikari.Embed(
                title = f"Смена гендера!",
                colour = 0x313236
            )
        )
        
        await ctx.edit_response(embed = embed, components = view, flags = hikari.MessageFlag.EPHEMERAL)
        
        client.start_view(view)
        
        self.stop()
            
class NonAdmission(ViewSample):
    __slots__ = ("__memberWhoVF")
    
    def __init__(self, member):
        self.__memberWhoVF: hikari.InteractionMember = member
        
        super().__init__(timeout = None)
        
    @miru.text_select(
        placeholder = "Выберите причину недопуска", 
        options= [miru.SelectOption(reason) for reason in REFUSAL_REASONS],
        max_values = len(REFUSAL_REASONS)
    )
    async def select_reason(self, ctx: miru.ViewContext, select: miru.TextSelect):
        embed = hikari.Embed(
            title = f"{self.__memberWhoVF}, вы были недопущены из-за следующих причин:", 
            colour = 0x313236
        )
        
        embed_result = hikari.Embed(
            title = f"{ctx.author}, вы успешно завершили операцию ^^", 
            colour = 0x313236
        )
        
        for reason in select.values:
            embed.add_field(
                f"Причина {select.values.index(reason)+1}:", 
                f"```{reason}```"
            )
            
        await self.__memberWhoVF.add_role(config["roles"]["refusal"])
        
        await self.__memberWhoVF.remove_role(config["roles"]["unvf"])
        
        await self.__memberWhoVF.send(embed = embed_result, components = None, flags = hikari.MessageFlag.EPHEMERAL)
        
        await ctx.respond(embed = embed)
        
        self.stop()