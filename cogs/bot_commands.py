import discord
from discord import app_commands
from discord.ext import commands
import sheet as sh
from requests import get
from logger import setup_logger
from config import ASSIGNMENT_CHANNEL, ONESHOT_CHANNEL, role_dict

#Create a logger for the cog
logger = setup_logger(__name__)

# note: Remember that when you are inside a cog, you should use self.bot instead of just bot to refer to the bot instance. Moreover, slash commands (@app_commands.command) have been placed in cogs since discord.py v2.x, which means you should also convert your @bot.tree.command to @app_commands.command and use them inside the cog class.

class BotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # Normal text-based Commands

    @commands.command()
    async def foo(self, ctx, arg):
        await ctx.send(arg)


    # slash commands go here using @app_commands decorator

    @app_commands.command(name="findid")
    @app_commands.describe(user="User")
    async def findid(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.send_message("Done")
        await sh.findid(user.name, str(user.id))


    @app_commands.command(name="say")
    @app_commands.describe(arg="what to say")
    async def say(self, interaction: discord.Interaction, arg: str):
        user = interaction.user.name
        roles = await self.bot.guildstuff.fetch_member(int(arg))
        await interaction.response.send_message(f"Hey{interaction.user.mention}, test 2, {user}")


    @app_commands.command(name="oneshot")
    @app_commands.describe(series="# of the series")
    async def oneshot(self, interaction: discord.Interaction, series: str):
        target_channel = self.bot.get_channel(ONESHOT_CHANNEL)
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


    @app_commands.command(name="assign")
    @app_commands.describe(series="# of the series", chapter="What chapter", role="What needs to be done", who="Who")
    async def assign(self, interaction: discord.Interaction, series: str, chapter: str, role: str, who: str):
        await interaction.response.defer(ephemeral=True)
        target_channel = self.bot.get_channel(ASSIGNMENT_CHANNEL)
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


    @app_commands.command(name="bulkassign")
    @app_commands.describe(series="# of the series", start_chapter="start chapter", end_chapter="end chapter",
                        role="What needs to be done", who="Who")
    async def bulkassign(self, interaction: discord.Interaction, series: str, start_chapter: int, end_chapter: int, role: str,
                        who: str):
        target_channel = self.bot.get_channel(ASSIGNMENT_CHANNEL)
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

    @app_commands.command(name="channel")
    @app_commands.describe(channel="# of the channel", sheet="Name of the sheet")
    async def channel(self, interaction: discord.Interaction, channel: str, sheet: str):
        await interaction.response.send_message(f"{channel} was assigned to {sheet}")
        # datatest.add_to_json_file('channel.json', sheet, channel)
        await sh.writechannel(channel, sheet)


    @app_commands.command(name="create")
    @app_commands.describe(channelname="Name of the channel", sheet="Name of the sheet")
    async def create(self, interaction: discord.Interaction, channelname: str, sheet: str):
        guild = interaction.guild
        category = self.bot.get_channel(1218035431078236323)
        await sh.copy(sheet)

        channel = await guild.create_text_channel(channelname, category=category)
        new_position = 2  # Define new_position here
        await channel.edit(position=new_position)
        channels = sorted(guild.channels, key=lambda c: c.position)
        channels_positions = {channels[i].id: i for i in range(len(channels))}
        channels_positions[channel.id] = new_position
        id = channel.id
        await sh.writechannel(f"<@{channel.id}>", sheet)
    
    @app_commands.command(name="updatechannelname")
    @app_commands.describe(channel="# of the Channel", new_name="The new name for the sheet")
    async def updatechannelname(self, interaction: discord.Interaction, channel: str, new_name: str):
        await interaction.response.send_message(f"{channel} was reassigned to {new_name}")
        await sh.updatesheet(channel, new_name)


    @app_commands.command(name="updatechannelid")
    @app_commands.describe(new_channel="new # of the Channel", name="Name of the sheet")
    async def updatechannelid(self, interaction: discord.Interaction, new_channel: str, name: str):
        await interaction.response.send_message(f"{name} was reassigned to {new_channel}")
        await sh.updatechannel_id(new_channel, name)


    @app_commands.command(name="done")
    @app_commands.describe(series="# of the Series", chapter="What chapter", role="What role")
    async def done(self, interaction: discord.Interaction, series: str, chapter: str, role: str):
        first = None
        second = None
        target_channel_id = int("1218705159614631946")  # change to actual channel 
        target_channel = self.bot.get_channel(target_channel_id)
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


    @app_commands.command(name="logs")
    @app_commands.describe()
    async def logs(self, interaction: discord.Interaction):
        with open("example.log", "r") as file:
            await interaction.response.send_message(file.read(), ephemeral=True)


    @app_commands.command(name="ip")
    @app_commands.describe()
    async def ip(self, interaction: discord.Interaction):
        if interaction.user.id == 611962086049710120:
            ip = get('https://api.ipify.org').content.decode('utf8')
            await interaction.response.send_message(ip, ephemeral=True)
        else:
            await interaction.response.send_message("You are not allowed to use this command")


async def setup(bot):
    await bot.add_cog(BotCommands(bot)) 
    
