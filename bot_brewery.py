import discord
from config import TOKEN, BOT_ID, ASSIGNMENT_CHANNEL, CHECKUP_CHANNEL, ONESHOT_CHANNEL, COMMAND_PREFIX, \
    role_dict_reaction
import sys
from discord.ext import tasks
import asyncio
from utils.utils import assignment_reaction, checkup_reaction, oneshot_reaction
from utils.event_handlers import *

# Setup logger
logger = setup_logger(__name__)

# Instantiate the bot
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=discord.Intents.all())  # Initialize bot with a command prefix


# Attach event handlers
@bot.event
async def on_ready():
    await bot_ready(bot)


@bot.event
async def on_disconnect():
    await bot_disconnect(bot)


@bot.event
async def on_resumed():
    await bot_resumed(bot)


@bot.event
async def on_command_error(ctx, error):
    await bot_command_error(ctx, error)


@bot.event
async def on_raw_reaction_add(payload):
    assignmentlog = bot.get_channel(1219030657955794954)
    channel_id = payload.channel_id
    if payload.user_id != BOT_ID:  # Checks so it's not the bot reacting
        if channel_id == ASSIGNMENT_CHANNEL:
            await assignment_reaction(bot, payload, assignmentlog)
        elif channel_id == CHECKUP_CHANNEL:  # every reaction in the Hydrometer channel
            await checkup_reaction(bot, payload, assignmentlog)
        elif channel_id == ONESHOT_CHANNEL:
            await oneshot_reaction(bot, payload, assignmentlog)


@bot.event
async def on_member_join(member):
    await sh.findid(member.name, str(member.id))


# Define tasks - looping #
@tasks.loop(minutes=1)
async def check_old_entries():
    await bot.wait_until_ready()  # Wait until the bot is ready
    await sh.check_old_entries(bot)


# Main function to run the bot
async def main():
    try:
        await bot.load_extension('cogs.bot_commands')  # Load your commands extension
        await bot.load_extension('cogs.help_command')  # Load your help command extension        await bot.load_extension('cogs.dev_utilities')  # Load your dev utilities extension
        await bot.load_extension('cogs.assignment')  # Load your assignment extension
        check_old_entries.start()  # Start the looping task
        await bot.start(TOKEN)  # Start the bot

    except KeyboardInterrupt:
        await bot.close()
        logger.info("Bot shut down via KeyboardInterrupt")


# Handle exceptions globally
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception

if __name__ == '__main__':
    asyncio.run(main())
