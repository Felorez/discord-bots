import lightbulb
import hikari

from src.bot.machine import bot, client
from views.verfication import ChangeGender
from src.data.data import config

class SupportCommands:
    
    @bot.command
    @lightbulb.add_checks(lightbulb.has_roles(config["roles"]["support"]))
    @lightbulb.option("user", "имя или индефикатор юзера", hikari.OptionType.USER, required = True)
    @lightbulb.command("verification", "Используйте эту команду чтобы завершить верефикацию!)", ephemeral = True, auto_defer = True)
    @lightbulb.implements(lightbulb.SlashCommand)
    async def response_support(ctx: lightbulb.Context):
        if (ctx.options.user.is_bot) or (config["gender_roles"]["man"] in ctx.options.user.role_ids) or (config["gender_roles"]["woman"] in ctx.options.user.role_ids):
            await ctx.respond("Уже верифицирован!")
            return
        
        view = ChangeGender(ctx.options.user)
        
        image_embed = (
            hikari.Embed(
                colour = 0x313236
            )
            .set_image(
                "https://upload.wikimedia.org/wikipedia/commons/9/9c/Black_hole_representation.gif"
            )
        )
        
        embed = (
            hikari.Embed(
                colour = 0x313236
            )
            .set_author(
                name = f"Выберите гендер, который хотите присвоить {ctx.options.user}⠀⠀⠀",
                icon = ctx.options.user.make_avatar_url()
            )
        )
        
        await ctx.respond(embeds = [image_embed, embed], components = view, flags = hikari.MessageFlag.EPHEMERAL)
        client.start_view(view)
        
    # @bot.listen(lightbulb.CommandErrorEvent)
    # async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    #     if isinstance(event.exception, lightbulb.MissingRequiredRole):
    #         await event.context.respond("У тебя нет прав использовать эту команду)", flags = hikari.MessageFlag.EPHEMERAL)
    #         return
        
        