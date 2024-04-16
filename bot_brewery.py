import discord
from config import TOKEN, BOT_ID, ASSIGNMENT_CHANNEL, CHECKUP_CHANNEL, ONESHOT_CHANNEL, COMMAND_PREFIX, role_dict, role_dict_reaction
import sys
from discord.ext import tasks
from datetime import datetime, timedelta
import asyncio
from utils.utils import remove_reaction, delete_message, select_date, reactionhelper
from utils.event_handlers import *

# Setup logger
logger = setup_logger(__name__)


# Instantiate the bot
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=discord.Intents.all()) # Initialize bot with a command prefix


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
    logger.info(payload.emoji)
    logger.info(repr(payload.emoji))
    assignmentlog = bot.get_channel(1219030657955794954)
    channel_id = payload.channel_id
    if payload.user_id != BOT_ID:  # Checks so it's not the bot reacting
        emoji_repr = repr(payload.emoji)
        if channel_id == ASSIGNMENT_CHANNEL: # everything in the assignment channel inside this if clause
            data, row_name = await sh.getmessageid(payload.message_id)
            if f"<@{payload.user_id}>" == data[4]:
                role = data[2]
                if emoji_repr == "<PartialEmoji animated=False name='✅' id=None>":
                    await remove_reaction(bot, payload.channel_id, payload.message_id, "❌", True)
                    await remove_reaction(bot, payload.channel_id, payload.message_id, "✅", True)
                    await reactionhelper(data, assignmentlog, "Working")
                    current_time = datetime.now().date().strftime("%Y-%m-%d")
                    await sh.storetime(row_name, current_time)
                elif emoji_repr == "<PartialEmoji animated=False name='🥂' id=None>":
                    if role in role_dict_reaction:
                        role = role_dict_reaction[role]
                    await assignmentlog.send(
                        f"{await sh.getchannelid(data[0])} | CH {data[1]} | {role} | **Done** | {data[4]}")
                    # if role == "UPD":
                    #    await sh.write(data, "")
                    # else:
                    #    await sh.write(data, "Done")
                    await sh.write(data, "Done")
                    await sh.delete_row(row_name)  # clear message data
                    await remove_reaction(bot, payload.channel_id, payload.message_id, "🥂", False)
                elif emoji_repr == "<PartialEmoji animated=False name='❌' id=None>":
                    await reactionhelper(data, assignmentlog, "Declined")
                    await delete_message(bot ,payload.channel_id, payload.message_id)
                    await sh.delete_row(row_name)  # clear
                elif emoji_repr == "<PartialEmoji animated=False name='💣' id=None>":
                    guild = bot.get_guild(payload.guild_id)
                    required_role = discord.utils.get(guild.roles, name="Tavern Keeper")
                    member = guild.get_member(payload.user_id)
                    logger.info(member.roles)
                    if required_role in member.roles:
                        await delete_message(bot, payload.channel_id, payload.message_id)
                        await sh.write(data, "")
                        await sh.delete_row(row_name)
                        await assignmentlog.send(f"{await sh.getchannelid(data[0])} | CH {data[1]} | {role} | **Deleted** | {data[4]}")
        elif channel_id == CHECKUP_CHANNEL: # every reaction in the Hydrometer channel
            data, row_name = await sh.getmessageid_due_date(payload.message_id)
            if f"<@{payload.user_id}>" == data[4]:

                if emoji_repr == "<PartialEmoji animated=False name='✅' id=None>":
                    await delete_message(bot, payload.channel_id, payload.message_id, delete_after=60)
                    await remove_reaction(bot, payload.channel_id, payload.message_id, "❌", False)
                    await remove_reaction(bot, payload.channel_id, payload.message_id, "<:no:1225574648088105040>", False)
                if emoji_repr == "<PartialEmoji animated=False name='no' id=1225574648088105040>":
                    row = row_name
                    user = bot.get_user(payload.user_id)
                    role = data[2]
                    original_date = data[5]
                    if role in role_dict_reaction:
                        role = role_dict_reaction[role]
                    date, msg = await select_date(bot,user, data[0], data[1], role, f"<@{payload.user_id}>")
                    due_date = date - timedelta(days=4)
                    await sh.storetime(row, due_date)
                    await sh.remove_due_date(row)
                    await delete_message(bot, payload.channel_id, payload.message_id)
                    await assignmentlog.send(
                        f"<@{payload.user_id}> has **extended** the due date for {data[0]} CH {data[1]} (Role: {role}) from {original_date} to **{date}**.\n"
                        f"Reason: {msg.content}")
                elif emoji_repr == "<PartialEmoji animated=False name='❌' id=None>":
                    await reactionhelper(data, assignmentlog, "Declined")
                    await delete_message(bot, payload.channel_id, payload.message_id)
                    await sh.delete_row(row_name)  # clear
        elif channel_id == ONESHOT_CHANNEL:
            if emoji_repr == "<PartialEmoji animated=False name='BunKill' id=1218766575302348891>":
                role = "RP"
            elif emoji_repr == "<PartialEmoji animated=False name='cocosideeye' id=1219500662799208458>":
                role = "TL"
            elif emoji_repr == "<PartialEmoji animated=False name='communistecommunist' id=1219519556305948723>":
                role = "PR"
            elif emoji_repr == "<PartialEmoji animated=False name='Kokopium' id=1219519277783322647>":
                role = "CLRD"
            elif emoji_repr == "<PartialEmoji animated=False name='mingmingsmirk' id=1224929840633741312>":
                role = "TS"
            elif emoji_repr == "<PartialEmoji animated=False name='JerryShocked' id=1218766878479093872>":
                role = "QC"
            else:
                return
            await sh.oneshot(payload.message_id, role)

@bot.event
async def on_member_join(member):
    await sh.findid(member.name, str(member.id))


# Define tasks - looping #
@tasks.loop(minutes=1)
async def check_old_entries():
    await sh.check_old_entries(bot)


# Main function to run the bot
async def main():
    try:
        await bot.load_extension('cogs.bot_commands') # Load your commands extension
        await bot.load_extension('cogs.help_command') # Load your help command extension

        check_old_entries.start() # Start the looping task
        await bot.start(TOKEN) # Start the bot

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
