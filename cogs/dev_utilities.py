from discord.ext import commands
import discord
from discord import app_commands
from discord.ext import commands
import sheet as sh
from requests import get
from logger import setup_logger
from config import ASSIGNMENT_CHANNEL, ONESHOT_CHANNEL, role_dict
from datetime import datetime, timedelta
from config import role_dict_reaction
logger = setup_logger(__name__)
class dev_utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="logs")
    async def upload_log(self, interaction: discord.Interaction):
        """
        Uploads the app.log file to the Discord channel where the command was invoked.
        """
        with open('app.log', 'rb') as fp:
            await interaction.response.send_message(file=discord.File(fp, 'app.log'))

    @app_commands.command(name="botlogs")
    async def upload_botlog(self, interaction: discord.Interaction):
        """
        Uploads the bot.log file to the Discord channel where the command was invoked.
        """
        with open('bot.log', 'rb') as fp:
            await interaction.response.send_message(file=discord.File(fp, 'bot.log'))

    @app_commands.command(name="ip")
    @app_commands.describe()
    async def ip(self, interaction: discord.Interaction):
        if interaction.user.id == 611962086049710120:
            ip = get('https://api.ipify.org').content.decode('utf8')
            await interaction.response.send_message(ip, ephemeral=True)
        else:
            await interaction.response.send_message("You are not allowed to use this command")


async def setup(bot):
    await bot.add_cog(dev_utils(bot))