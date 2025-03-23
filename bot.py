import discord
import calendar

from os import environ as env
from discord.ext import commands
from datetime import date
from django import setup

env.setdefault("DJANGO_SETTINGS_MODULE", "bot_discord.settings")
setup()

from bot_discord.discord_settings import DISCORD_TOKEN, logging
from bot_discord.utils.land import show_lands_contributions
from bot_discord.models import DiscordUser

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True


logger = logging.getLogger("bot")


bot = commands.Bot(command_prefix="/", intents=intents)

@bot.command()
async def points(ctx):
    hoy = date.today()
    fecha_inicio = date(hoy.year, hoy.month, 1)
    fecha_final = date(hoy.year, hoy.month, calendar.monthrange(hoy.year, hoy.month)[1])

    try:
        await show_lands_contributions(ctx, fecha_inicio, fecha_final)
    except Exception as e:
        await ctx.send(f"Error: {e}")


@bot.command()
async def daypoints(ctx):
    hoy = date.today()

    try:
        await show_lands_contributions(ctx, hoy, hoy)
    except Exception as e:
        await ctx.send(f"Error: {e}")


@bot.command()
async def clean(ctx, cantidad: int = 1000):
    await ctx.channel.purge(limit=cantidad)
    await ctx.send(f"🧹 Se han eliminado {cantidad} mensajes. 🧹", delete_after=5)


bot.run(DISCORD_TOKEN, root_logger=True)
