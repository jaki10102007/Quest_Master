import discord
import sheet as sh
from datetime import datetime
from config import role_dict_reaction

# Helper functions #

async def remove_reaction(bot, channel_id, message_id, emoji, add):
    channel = bot.get_channel(channel_id)
    message = await channel.fetch_message(message_id)
    await message.clear_reaction(emoji)
    if add:
        await message.add_reaction("🥂")


async def delete_message(bot, channel_id, message_id):
    channel = bot.get_channel(int(channel_id))
    message = await channel.fetch_message(int(message_id))
    await message.delete()


async def select_date(bot, user, series, chapter, role, usermention):
    def check(msg):
        return msg.author == user and isinstance(msg.channel, discord.DMChannel) and \
            datetime.strptime(msg.content, '%Y-%m-%d')
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
        f"{await sh.getchannelid(data[0])} | CH {data[1]} | {role} | sheet updated to status: **{status}** by: {data[4]}")
