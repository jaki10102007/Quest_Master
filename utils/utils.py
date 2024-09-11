import logging
import discord
import sheet as sh
from datetime import datetime
from config import role_dict_reaction , ASSIGNMENT_CHANNEL , CHECKUP_CHANNEL , ONESHOT_CHANNEL
import asyncio



# Helper functions #
async def remove_reaction(bot, channel_id, message_id, emoji, add):
    channel = bot.get_channel(channel_id)
    message = await channel.fetch_message(message_id)
    await message.clear_reaction(emoji)
    if add:
        await message.add_reaction("🥂")


async def delete_message(bot, channel_id, message_id, delete_after=None):
    channel = bot.get_channel(int(channel_id))
    message = await channel.fetch_message(int(message_id))
    if delete_after is not None:
        await message.delete(delay=delete_after)
    else:
        await message.delete()


async def select_date(bot, user, series, chapter, role, usermention):
    def check(msgs):
        return msgs.author == user and isinstance(msgs.channel, discord.DMChannel) and \
            datetime.strptime(msgs.content, '%Y-%m-%d')

    await user.send(
        f'Hey, {usermention}! It looks like you need a bit more time to finish **"{series} CH {chapter} (Role: {role})".\n'
        f'**No worries! Please let us know your new expected completion date by entering it in the format YYYY-MM-DD.\n'
        f'This helps us update our schedule accordingly. Thanks for your hard work and for keeping the team updated!')
    msg = await bot.wait_for('message', check=check)
    date = datetime.strptime(msg.content, '%Y-%m-%d').date()
    await user.send(f'New due date set to {date:%B %d, %Y}.')
    await user.send('What is the reason for the delay? Please provide a brief explanation.')
    msg = await bot.wait_for('message', check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel))
    await user.send(
        f'Thank you for letting us know! We will update the schedule accordingly. \nIf you have any questions or need'
        f'further assistance, please feel free to reach out to us. \nWe appreciate your hard work and dedication to '
        f'the team!')
    return date, msg


async def reactionhelper(data, assignmentlog, status):
    role = data[2]
    if role in role_dict_reaction:
        role = role_dict_reaction[role]
    await sh.write(data, status)
    await assignmentlog.send(
        f"{data[0]} | CH {data[1]} | {role} | sheet updated to status: **{status}** by: {await sh.getuser(data[4])}")


async def oneshot_reaction(bot, payload, assignmentlog):
    emoji_repr = repr(payload.emoji)
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
    # await sh.oneshot(payload.message_id, role)


async def assignment_reaction(bot, payload, assignmentlog):
    """
        Handles reactions added to assignment messages in Discord.

        This function is triggered when a reaction is added to an assignment message. It checks the type of reaction and performs different actions accordingly:
        - '✅': Marks the assignment as "Working" and stores the current time.
        - '🥂': Marks the assignment as "Done", sends a completion message to the assignment log, and deletes the assignment message after a delay.
        - '❌': Marks the assignment as "Declined" and deletes the assignment message.
        - '💣': If the user has the "Tavern Keeper" role, deletes the assignment message.

        Args:
            bot (Bot): The bot instance.
            payload (Payload): The payload of the reaction add event.
            assignmentlog (TextChannel): The Discord channel where assignment logs are sent.
        """
    emoji_repr = repr(payload.emoji)
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
                f"{data[0]} | CH {data[1]} | {role} | **Done** | {await sh.getuser(data[4])}")
            # if role == "UPD":
            #    await sh.write(data, "")
            # else:
            #    await sh.write(data, "Done")
            await sh.write(data, "Done")
            await sh.delete_row(row_name)  # clear message data
            await remove_reaction(bot, payload.channel_id, payload.message_id, "🥂", False)
            await asyncio.sleep(120)
            await delete_message(bot, payload.channel_id, payload.message_id)
        elif emoji_repr == "<PartialEmoji animated=False name='❌' id=None>":
            await reactionhelper(data, assignmentlog, "Declined")
            await delete_message(bot, payload.channel_id, payload.message_id)
            await sh.delete_row(row_name)  # clear
        elif emoji_repr == "<PartialEmoji animated=False name='💣' id=None>":
            guild = bot.get_guild(payload.guild_id)
            required_role = discord.utils.get(guild.roles, name="Tavern Keeper")
            member = guild.get_member(payload.user_id)
            if required_role in member.roles:
                await delete_message(bot, payload.channel_id, payload.message_id)
                await sh.write(data, "")
                await sh.delete_row(row_name)


async def checkup_reaction(bot, payload, assignmentlog):
    """
        Handles reactions added to checkup messages in Discord.

        This function is triggered when a reaction is added to a checkup message. It checks the type of reaction and performs different actions accordingly:
        - '✅': Deletes the checkup message and removes certain reactions.
        - 'no': Extends the due date for the assignment related to the checkup message, sends a message to the assignment log about the extension, and deletes the checkup message.

        Args:
            bot (Bot): The bot instance.
            payload (Payload): The payload of the reaction add event.
            assignmentlog (TextChannel): The Discord channel where assignment logs are sent.
        """
    emoji_repr = repr(payload.emoji)
    data, row_name = await sh.getmessageid_due_date(payload.message_id)
    if f"<@{payload.user_id}>" == data[5]:
        if emoji_repr == "<PartialEmoji animated=False name='✅' id=None>":
            await delete_message(bot, payload.channel_id, payload.message_id, delete_after=60)
        if emoji_repr == "<PartialEmoji animated=False name='no' id=1225574648088105040>":
            row = row_name
            user = bot.get_user(payload.user_id)
            role = data[3]
            original_date = data[6]
            if role in role_dict_reaction:
                role = role_dict_reaction[role]
            date, msg = await select_date(bot, user, data[1], data[2], role, f"<@{payload.user_id}>")
            due_date = date - timedelta(days=4)
            await sh.storetime(row, due_date)
            await sh.remove_due_date(row)
            await delete_message(bot, payload.channel_id, payload.message_id)
            await assignmentlog.send(
                f"<@{payload.user_id}> has **extended** the due date for {data[1]} CH {data[2]} (Role: {role}) from {original_date} to **{date}**.\n"
                f"Reason: {msg.content}")
        elif emoji_repr == "<PartialEmoji animated=False name='❌' id=None>":
            await delete_message(bot, payload.channel_id, payload.message_id)
            await delete_message(bot, ASSIGNMENT_CHANNEL, f"{data[0]}")
            await sh.delete_row(row_name)
            data.pop(0)
            await reactionhelper(data, assignmentlog, "Declined")