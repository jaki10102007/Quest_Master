import discord
from discord import app_commands
from discord.ext import commands
import sheet as sh
import logging
from dotenv import load_dotenv
import os
import sys
from requests import get
from discord.ext import tasks
from datetime import datetime, timedelta

# Logging #
logger = logging.getLogger(__name__)
handler = logging.FileHandler('example.log', 'w', 'utf-8')
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception

# Constants #
load_dotenv()
TOKEN = os.getenv("TOKEN")  # Discord Token
BOT_ID = 1218682240947458129  # User id of the bot
ASSIGNMENT_CHANNEL = 1218705159614631946  # Channel ID of the assignment channel
CHECKUP_CHANNEL = 1224453260543266907  # Channel ID of Hdydrometer
ONESHOT_CHANNEL = 1225634854390206494  # Channel ID of the oneshot channel
role_dict = {
    "RP": ("B", "C"),
    "TL": ("D", "E"),
    "PR": ("F", "G"),
    "CLRD": ("H", "I"),
    "TS": ("J", "K"),
    "QC": ("L", "M"),
    "UPD": ("N", "O")
}
role_dict_reaction = {
    "B": "RP",
    "D": "TL",
    "F": "PR",
    "H": "CLRD",
    "J": "TS",
    "L": "QC",
    "N": "UPD"
}

bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())


# Bot events #
@bot.event  # Will start when the bot it ready
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    check_old_entries.start()
    global guildstuff
    guildstuff = bot.fetch_guild(1218035430373462016)
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(e)


@bot.event
async def on_raw_reaction_add(payload):
    assignmentlog = bot.get_channel(1219030657955794954)
    channel_id = payload.channel_id
    print(repr(payload.emoji))
    if payload.user_id != BOT_ID:  # Checks so it's not the bot reacting
        emoji_repr = repr(payload.emoji)
        if channel_id == ASSIGNMENT_CHANNEL: # everything in the assignment channel inside this if clause
            data, row_name = await sh.getmessageid(payload.message_id)
            if f"<@{payload.user_id}>" == data[4]:

                role = data[2]
                if emoji_repr == "<PartialEmoji animated=False name='✅' id=None>":
                    await remove_reaction(payload.channel_id, payload.message_id, "❌", True)
                    await remove_reaction(payload.channel_id, payload.message_id, "✅", True)
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
                    await remove_reaction(payload.channel_id, payload.message_id, "🥂", False)
                elif emoji_repr == "<PartialEmoji animated=False name='❌' id=None>":
                    await reactionhelper(data, assignmentlog, "Declined")
                    await delete_message(payload.channel_id, payload.message_id)
                    await sh.delete_row(row_name)  # clear
                elif emoji_repr == "<PartialEmoji animated=False name=':bomb:' id=None>":
                    guild = bot.get_guild(payload.guild_id)
                    member = guild.fetch_member(payload.user_id)
                    # Check if the member has the required role
                    required_role = discord.utils.get(guild.roles, name="Tavern Keeper")
                    if required_role in member.roles:
                        await delete_message(payload.channel_id, payload.message_id)
                        await sh.delete_row(row_name)
                        await assignmentlog.send(f"{await sh.getchannelid(data[0])} | CH {data[1]} | {role} | **Deleted** | {data[4]}")
        elif channel_id == CHECKUP_CHANNEL: # every reaction in the Hydromiter channel
            data, row_name = await sh.getmessageid_due_date(payload.message_id)
            if f"<@{payload.user_id}>" == data[4]:

                if emoji_repr == "<PartialEmoji animated=False name='✅' id=None>":
                    await remove_reaction(payload.channel_id, payload.message_id, "❌", False)
                    await remove_reaction(payload.channel_id, payload.message_id, "<:no:1225574648088105040>", False)
                if emoji_repr == "<PartialEmoji animated=False name='no' id=1225574648088105040>":
                    row = row_name
                    user = bot.get_user(payload.user_id)
                    role = data[2]
                    original_date = data[5]
                    if role in role_dict_reaction:
                        role = role_dict_reaction[role]
                    date, msg = await select_date(user, data[0], data[1], role, f"<@{payload.user_id}>")
                    due_date = date - timedelta(days=4)
                    print(due_date)
                    await sh.storetime(row, due_date)
                    await sh.remove_due_date(row)
                    await delete_message(payload.channel_id, payload.message_id)
                    await assignmentlog.send(
                        f"<@{payload.user_id}> has **extended** the due date for {data[0]} CH {data[1]} (Role: {role}) from {original_date} to **{date}**.\n"
                        f"Reason: {msg.content}")
                elif emoji_repr == "<PartialEmoji animated=False name='❌' id=None>":
                    await reactionhelper(data, assignmentlog, "Declined")
                    await delete_message(payload.channel_id, payload.message_id)
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


# Helper functions #
#
async def remove_reaction(channel_id, message_id, emoji, add):
    channel = bot.get_channel(channel_id)
    message = await channel.fetch_message(message_id)
    await message.clear_reaction(emoji)
    if add:
        await message.add_reaction("🥂")


async def delete_message(channel_id, message_id):
    channel = bot.get_channel(int(channel_id))

    message = await channel.fetch_message(int(message_id))

    await message.delete()


async def select_date(user, series, chapter, role, usermention):
    await user.send(
        f'Hey, {usermention}! It looks like you need a bit more time to finish **"{series} CH {chapter} (Role: {role})".\n'
        f'**No worries! Please let us know your new expected completion date by entering it in the format YYYY-MM-DD.\n'
        f'This helps us update our schedule accordingly. Thanks for your hard work and for keeping the team updated!')

    def check(msg):
        return msg.author == user and isinstance(msg.channel, discord.DMChannel) and \
            datetime.strptime(msg.content, '%Y-%m-%d')

    msg = await bot.wait_for('message', check=check)
    date = datetime.strptime(msg.content, '%Y-%m-%d').date()
    await user.send(f'You have selected the date {date:%B %d, %Y}.')
    await user.send('What is the reason for the delay? Please provide a brief explanation.')
    msg = await bot.wait_for('message', check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel))
    await user.send(
        f'Thank you for letting us know! We will update the schedule accordingly. \nIf you have any questions or need '
        f'further assistance, please feel free to reach out to us. \nWe appreciate your hard work and dedication to '
        f'the team!')
    return date, msg


async def reactionhelper(data, assignmentlog, status):
    role = data[2]
    if role in role_dict_reaction:
        role = role_dict_reaction[role]
    await sh.write(data, status)
    await assignmentlog.send(
        f"{await sh.getchannelid(data[0])} | CH {data[1]} | {role} | sheet updated to status: **{status}** by: {data[4]}")


# /commands #
@bot.tree.command(name="findid")
@app_commands.describe(user="User")
async def findid(interaction: discord.Interaction, user: discord.User):
    await interaction.response.send_message("Done")
    await sh.findid(user.name, str(user.id))


@bot.tree.command(name="say")
@app_commands.describe(arg="what to say")
async def say(interaction: discord.Interaction, arg: str):
    user = interaction.user.name
    print(arg)
    roles = await bot.guildstuff.fetch_member(int(arg))
    print(roles)
    await interaction.response.send_message(f"Hey{interaction.user.mention}, test 2, {user}")


@bot.tree.command(name="oneshot")
@app_commands.describe(series="# of the series")
async def oneshot(interaction: discord.Interaction, series: str):
    target_channel = bot.get_channel(ONESHOT_CHANNEL)
    await interaction.response.defer(ephemeral=True)
    message = await target_channel.send(f" We are recruiting for a new oneshot **{series}**")
    await message.add_reaction("<BunKill:1218766575302348891>")
    await message.add_reaction("<cocosideeye:1219500662799208458>")
    await message.add_reaction("<communistecommunist:1219519556305948723>")
    await message.add_reaction("<Kokopium:1219519277783322647>")
    await message.add_reaction("<mingmingsmirk:1224929840633741312>")
    await message.add_reaction("<JerryShocked:1218766878479093872>")
    series = sh.getsheetname(series)
    await interaction.followup.send("Done")


@bot.tree.command(name="assign")
@app_commands.describe(series="# of the series", chapter="What chapter", role="What needs to be done", who="Who")
async def assign(interaction: discord.Interaction, series: str, chapter: str, role: str, who: str):
    await interaction.response.defer(ephemeral=True)
    target_channel = bot.get_channel(ASSIGNMENT_CHANNEL)
    member = interaction.guild.get_member(int(who[2:-1]))
    required_role = discord.utils.get(interaction.guild.roles, name="Hungover")
    role = role.upper()
    first = None
    second = None
    if role.upper() in role_dict:
        first, second = role_dict[role.upper()]
    if first is None:
        await interaction.followup.send(f" '{role.upper()}' is not a valid Role ", ephemeral=True)
        ## One SHot ##
    if required_role not in member.roles:

        message = await target_channel.send(f"{series}| CH {chapter} | {role} | {who}")
        data = [await sh.getsheetname(series), chapter, first, second, who]
        await sh.store(message.id, data[0], chapter, who, first, second)
        await sh.write(data, "Assigned")
        await interaction.followup.send(content="Assigned")
        await message.add_reaction("✅")
        await message.add_reaction("❌")
    else:
        await interaction.followup.send(f"{who} is on Hiatus", ephemeral=True)
@bot.tree.command(name="bulkassign")
@app_commands.describe(series="# of the series", start_chapter="start chapter", end_chapter="end chapter",
                       role="What needs to be done", who="Who")
async def bulkassign(interaction: discord.Interaction, series: str, start_chapter: int, end_chapter: int, role: str,
                     who: str):
    target_channel = bot.get_channel(ASSIGNMENT_CHANNEL)
    role = role.upper()
    first = None
    second = None
    await interaction.response.defer(ephemeral=True)
    if role.upper() in role_dict:
        first, second = role_dict[role.upper()]
    if first is None:
        await interaction.response.send_message(f" '{role.upper()}' is not a valid Role ", ephemeral=True)
    else:
        for x in range(start_chapter, end_chapter + 1):
            chapter = str(x)
            message = await target_channel.send(f"{series}| CH {chapter} | {role} | {who}")
            data = [await sh.getsheetname(series), chapter, first, second, who]
            await sh.store(message.id, data[0], chapter, who, first, second)
            await sh.write(data, "Assigned")

            await message.add_reaction("✅")
            await message.add_reaction("❌")
    await interaction.followup.send(content="Assigned")


@bot.tree.command(name="channel")
@app_commands.describe(channel="# of the channel", sheet="Name of the sheet")
async def channel(interaction: discord.Interaction, channel: str, sheet: str):
    await interaction.response.send_message(f"{channel} was assigned to {sheet}")
    # datatest.add_to_json_file('channel.json', sheet, channel)
    await sh.writechannel(channel, sheet)


@bot.tree.command(name="create")
@app_commands.describe(channelname="Name of the channel", sheet="Name of the sheet")
async def create(interaction: discord.Interaction, channelname: str, sheet: str):
    guild = interaction.guild
    category = bot.get_channel(1218035431078236323)
    await sh.copy(sheet)

    channel = await guild.create_text_channel(channelname, category=category)
    new_position = 2  # Define new_position here
    await channel.edit(position=new_position)
    channels = sorted(guild.channels, key=lambda c: c.position)
    channels_positions = {channels[i].id: i for i in range(len(channels))}
    channels_positions[channel.id] = new_position
    id = channel.id
    await sh.writechannel(f"<@{channel.id}>", sheet)


@bot.tree.command(name="updatechannelname")
@app_commands.describe(channel="# of the Channel", new_name="The new name for the sheet")
async def updatechannelname(interaction: discord.Interaction, channel: str, new_name: str):
    await interaction.response.send_message(f"{channel} was reassigned to {new_name}")
    await sh.updatesheet(channel, new_name)


@bot.tree.command(name="updatechannelid")
@app_commands.describe(new_channel="new # of the Channel", name="Name of the sheet")
async def updatechannelid(interaction: discord.Interaction, new_channel: str, name: str):
    await interaction.response.send_message(f"{name} was reassigned to {new_channel}")
    await sh.updatechannel_id(new_channel, name)


@bot.tree.command(name="done")
@app_commands.describe(series="# of the Series", chapter="What chapter", role="What role")
async def assign(interaction: discord.Interaction, series: str, chapter: str, role: str):
    first = None
    second = None
    target_channel_id = int("1218705159614631946")  # change to actual channel 
    target_channel = bot.get_channel(target_channel_id)
    user = interaction.user.id

    role = role.upper()
    if role.upper() in role_dict:
        first, second = role_dict[role]
    if first == None:
        if target_channel is None:
            logger.error("Done command used with invalid role")
        else:
            await interaction.response.send_message(f" '{role.upper()}' is not a valid Role ", ephemeral=True)
    else:
        # await target_channel.send(f"{interaction.user.mention} | {series}| CH {chapter} | {role.upper()} | Done")
        await target_channel.send(f"{series} | CH {chapter} | {role.upper()} | Done | {interaction.user.mention}")
        list = [await sh.getsheetname(series), chapter, first, second, f"<@{user}>"]
        await sh.write(list, "Done")
        # await interaction.response.send_message("Send", ephemeral=True)


@bot.tree.command(name="logs")
@app_commands.describe()
async def logs(interaction: discord.Interaction):
    with open("example.log", "r") as file:
        await interaction.response.send_message(file.read(), ephemeral=True)


@bot.tree.command(name="ip")
@app_commands.describe()
async def ip(interaction: discord.Interaction):
    if interaction.user.id == 611962086049710120:
        ip = get('https://api.ipify.org').content.decode('utf8')
        await interaction.response.send_message(ip, ephemeral=True)
    else:
        await interaction.response.send_message("You are not allowed to use this command")


# Normal Commands #


@bot.command()
async def foo(ctx, arg):
    await ctx.send(arg)


# Looping tasks #
@tasks.loop(minutes=1)
async def check_old_entries():
    print("checking old entries")
    await sh.check_old_entries(bot)


bot.run(TOKEN)
