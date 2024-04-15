import discord
from discord import app_commands
from discord.ext import commands
import sheet as sh
from dotenv import load_dotenv
from requests import get
from discord.ext import tasks
from datetime import datetime, timedelta
from logger import setup_logger

logger = setup_logger(__name__)

setup_event_handlers = {}


async def on_ready(bot):
    logger.info(f'{bot.user} has connected to Discord!')
    sh.check_old_entries.start()
    try:
        global guildstuff
        guildstuff = await bot.fetch_guild(1218035430373462016)
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")


async def on_disconnect(bot):
    logger.warning("Bot has disconnected from Discord.")
    # ... rest of your on_ready code ...


async def on_resumed(bot):
    logger.info("Bot has reconnected and resumed operations.")
    # ... rest of your on_disconnect code ...


# Handles errors triggered during command invocation
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Command does not exist.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Missing a required argument.')
    else:
        await ctx.send('An error occurred while processing the command.')
    logger.error(f"Error during command execution: {error}")
