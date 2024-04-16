from discord.ext import commands

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')  # Remove the default help command

    @commands.command(name='help')
    async def custom_help(self, ctx):
        help_text = """
        **Custom Help**
        - `$foo <arg>`: Echoes the argument.
        - `/assign <series> <chapter> <role> <who>`: Assigns a task.
        - `/oneshot <series>`: Creates a oneshot assignment.
        - `/channel <channel> <sheet>`: Assigns a channel to a sheet.
        - `/create <channelname> <sheet>`: Creates a new channel.
        (Add more as needed)
        """
        await ctx.send(help_text)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))