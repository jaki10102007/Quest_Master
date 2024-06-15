from discord.ext import commands
from logger import setup_logger
import sheet as sh
from bot_brewery import remove_reaction

logger = setup_logger(__name__)

setup_event_handlers = {}


async def bot_ready(bot):
    """
        Logs  bot's connection to Discord and syncs commands. Logs any sync errors.

        Args:
            bot (Bot): The bot instance that has connected to Discord.
    """
    logger.info(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")


async def bot_disconnect(bot):
    logger.warning("Bot has disconnected from Discord.")
    # ... rest of your on_disconnect code ...


async def bot_resumed(bot):
    logger.info("Bot has reconnected and resumed operations.")
    # ... rest of your on_resumed code ...


# Handles errors triggered during command invocation
async def bot_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Command does not exist.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Missing a required argument.')
    else:
        await ctx.send('An error occurred while processing the command.')
    logger.error(f"Error during command execution: {error}")
