import discord
from discord import app_commands
from discord.ext import commands
import sheet as sh
from requests import get
from logger import setup_logger
from config import ASSIGNMENT_CHANNEL, ONESHOT_CHANNEL, role_dict
from datetime import datetime, timedelta
from config import role_dict_reaction

class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='Assigned', value='assigned'),
            discord.SelectOption(label='Accepted', value='accepted'),
        ]
        super().__init__(placeholder='Select an Option', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == 'accepted':
            data = await sh.retriev_assignments(interaction.user.id)
            filtered_data = [item for item in data if len(item[0]) != 6]
            print(filtered_data)
            filtered_data2 = "\n".join([item[0][1] for item in filtered_data])
            # print(filtered_data2)
            embed = discord.Embed(title="Accepted",
                                  description="List of Your Accepted  Assignments",
                                  colour=0x00b0f4)
            embed.add_field(name="Series",
                            value="\n".join([item[0][1] for item in filtered_data]),
                            inline=True)
            updated_dates = [(datetime.strptime(item[0][6], date_format) + timedelta(days=4)).strftime(date_format) for item
                             in filtered_data]
            embed.add_field(name="Due Date",
                            value="\n".join(updated_dates),
                            inline=True)
            combined_values = [
                f"https://discord.com/channels/1218035430373462016/1218705159614631946/{item[0][0]}" for item
                in filtered_data]
            combined_string = "\n".join(combined_values)
            embed.add_field(name="Link",
                            value=combined_string,
                            inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        if self.values[0] == 'assigned':
            data = await sh.retriev_assignments(interaction.user.id)
            filtered_data = [item for item in data if len(item[0]) == 6]
            print(filtered_data)
            embed = discord.Embed(title="Assigned",
                                  description="List of Your Assignments which are not accepted",
                                  colour=0x00b0f4)
            embed.add_field(name="Series",
                            value="\n".join([item[0][1] for item in filtered_data]),
                            inline=True)
            corresponding_values = [role_dict_reaction[item[0][3]] for item in filtered_data]
            embed.add_field(name="Role",
                            value="\n".join(corresponding_values),
                            inline=True)
            combined_values = [
                f"https://discord.com/channels/1218035430373462016/1218705159614631946/{item[0][0]}" for item
                in filtered_data]
            print(combined_values)
            print(filtered_data[0][0])
            combined_string = "\n".join(combined_values)
            embed.add_field(name="Link",
                            value=combined_string,
                            inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Dropdown())

class assignment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

            message = await target_channel.send(f"{await sh.getsheetname(series)} | CH {chapter} | {role} | {who}")
            data = [await sh.getsheetname(series), chapter, first, second, who]
            if data[0] is None:
                await interaction.followup.send(
                    f"Oops something went wrong! \nAre you sure that the channel is Inside the Databank?",
                    ephemeral=True)
            # If the sheet is not found, the message will be deleted and the user will be notified
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
    async def bulkassign(self, interaction: discord.Interaction, series: str, start_chapter: int, end_chapter: int,
                         role: str,
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
                message = await target_channel.send(f"{await sh.getsheetname(series)}| CH {chapter} | {role} | {who}")
                data = [await sh.getsheetname(series), chapter, first, second, who]
                await sh.store(message.id, data[0], chapter, who, first, second)
                await sh.write(data, "Assigned")

                await message.add_reaction("✅")
                await message.add_reaction("❌")
        await interaction.followup.send(content="Assigned")

    @app_commands.command(name="assignments")
    async def dropdown(self, interaction: discord.Interaction):
        view = DropdownView()
        await interaction.response.send_message(view=view, ephemeral=True)
    # slash commands go here using @app_commands decorator

async def setup(bot):
    await bot.add_cog(assignment(bot))