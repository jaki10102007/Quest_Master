import discord
from discord import app_commands
from discord.ext import commands
import sheet as sh
import logging
import inspect
import sys
from dotenv import load_dotenv
import os
from requests import get

load_dotenv()
TOKEN= os.getenv("TOKEN") # Discord Token
print(TOKEN)
role_dict = {
    "RP": ("B", "C"),
    "TL": ("D", "E"),
    "PR": ("F", "G"),
    "CLRD": ("H", "I"),
    "TS": ("J", "K"),
    "QC": ("L", "M")
}
role_dict_reaction = {
    "B": "RP",
    "D": "TL",
    "F": "PR",
    "H": "CLRD",
    "J": "TS",
    "L": "QC"
}
logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename='bot_errors.log', level=logging.ERROR)
line_number = inspect.currentframe().f_lineno

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception



bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    logging.info(f'{bot.user} has connected to Discord!')
    try: 
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


async def remove_reaction(channel_id, message_id, emoji):
    channel = bot.get_channel(channel_id)
    message = await channel.fetch_message(message_id)
    await message.clear_reaction(emoji)

async def delete_message(channel_id, message_id):
    channel = bot.get_channel(int(channel_id))

    message = await channel.fetch_message(int(message_id))

    await message.delete()

@bot.event
async def on_raw_reaction_add(payload):
    print(payload.emoji)
    channel_id = payload.channel_id
    target_channel_id = 1218705159614631946
    if ((channel_id == target_channel_id) and payload.user_id != 1218682240947458129):
        print("Passed channel and not bot ")
        data, row_name = sh.getmessageid(payload.message_id)
        print(data[4])
        print(payload.user_id)
        if f"<@{payload.user_id}>" == data[4]:
            print("passed right user")
            print(repr(payload.emoji))
            if repr(payload.emoji) == "<PartialEmoji animated=False name='✅' id=None>":
                print("passed right emoji")
                print("Reaction added in the target channel")
                print(payload)
                #data, row_name = sheet.getmessageid(payload.message_id)
                #data = sheet.getmessageid(payload.message_id)
                print(data)
                series = sh.getchannelid(data[0])
                #series = datatest.get_key("channel.json", data[0])
                chapter = data[1]
                role = data[2]
                if role in role_dict_reaction:
                    role = role_dict_reaction[role]
                else:
                    logging.info(f"Invalid role at line {line_number}")

                user= data[4]
                sh.write(data, "Working")
                await remove_reaction(payload.channel_id, payload.message_id, "❌")
                await remove_reaction(payload.channel_id, payload.message_id, "✅")
                target_channel_id = int("1219030657955794954")  # change to actual channel
                
                target_channel = bot.get_channel(target_channel_id)
                channel = bot.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id) 
                await message.add_reaction("🥂")
                await target_channel.send(f"{series} | CH {chapter} | {role} | sheet updated to status: Accepted by: {user}")
            
            elif repr(payload.emoji) == "<PartialEmoji animated=False name='🥂' id=None>":
                print("test")
                role = None
                await remove_reaction(payload.channel_id, payload.message_id, "🥂")
                target_channel_id = int("1219030657955794954")  # change to actual channel 
                target_channel = bot.get_channel(target_channel_id)
                data, row_name = sh.getmessageid(payload.message_id)
                #data = sheet.getmessageid(payload.message_id)
                series = sh.getchannelid(data[0])
                #series = datatest.get_key("channel.json", data[0])
                chapter = data[1]
                role = data[2]
                if role in role_dict_reaction:
                    role = role_dict_reaction[role]
                else:
                    logging.info(f"Invalid role at line {line_number}")

                user= data[4]
                print("this is series")
                print(series)
                print(role)
                await target_channel.send(f"{series} | CH {chapter} | {role} | Done | {user}")
                #await delete_message(payload.channel_id, payload.message_id)
                sh.write(data, "Done")
                sh.delete_row(row_name) #clear
            

            else: 
                target_channel_id = int("1219030657955794954")  # Replace with the ID of the target channel
                target_channel = bot.get_channel(target_channel_id)
                data, row_name = sh.getmessageid(payload.message_id)
                #data = sheet.getmessageid(payload.message_id)
                series = sh.getchannelid(data[0])
                #series = datatest.get_key("channel.json", data[0])
                chapter = data[1]
                role = data[2]
                if role in role_dict_reaction:
                    role = role_dict_reaction[role]
                else:
                    logging.info(f"Invalid role at line {line_number}")

                user= data[4]
                
                sh.write(data, "Declined")
                await target_channel.send(f"{series} | CH {chapter} | {role} | sheet updated to status: Declined by: {user}")
                await delete_message(payload.channel_id, payload.message_id)
                print(row_name)
                sh.delete_row(row_name) #clear 
    else: 
        print("Wrong channel")


@bot.tree.command(name="findid")    
@app_commands.describe(user = "User")
async def findid(interaction : discord.Interaction, user: discord.User):
    await interaction.response.send_message("Done")
    sh.findid(user.name, str(user.id))


@bot.event
async def on_member_join(member):
    print("new member")
    print(member.name)
    print(member.id)
    sh.findid(member.name, str(member.id))
    
@bot.tree.command(name="say")
@app_commands.describe(arg = "what to say")
async def say(interaction : discord.Interaction, arg: str):
    user = interaction.user.name
    await interaction.response.send_message(f"Hey{interaction.user.mention}, test 2, {user}")


@bot.tree.command(name="assign")
@app_commands.describe(series = "# of the series", chapter = "What chapter", role = "What needs to be done", who = "Who")
async def assign(interaction : discord.Interaction, series :str, chapter :str, role :str, who: str):
    print("assign")
    first = None
    second = None 
    target_channel_id = int("1218705159614631946")  # Replace with the ID of the target channel
    target_channel = bot.get_channel(target_channel_id)
    role = role.upper()
    if role.upper() in role_dict:
        first, second = role_dict[role]
        print(first)
        print(second)
    if first ==None:
        await interaction.response.send_message(f" '{role.upper()}' is not a valid Role " , ephemeral=True)
    else:
        await interaction.response.defer(ephemeral=True)
        message =await target_channel.send(f"{series}| CH {chapter} | {role.upper()} | {who}")
        await message.add_reaction("✅")
        await message.add_reaction("❌")
        #name = sheet.getuser(who)
        print("done")
        print(sh.getuser(who))
        print(sh.getsheetname(series))
        list= [sh.getsheetname(series), chapter, first, second, who]
        sh.store(message.id, sh.getsheetname(series), chapter, who, first, second)
        #sheet.store(message.id, sheet.getsheetname(series), chapter, sheet.getuser(who), first, second)
        sh.write(list, "Assigned")
        #await interaction.edit_original_interaction_response(content="Assigned")^
        await interaction.followup.send(content="Assigned")
        #await interaction.response.send_message("Assigned", ephemeral=True)

@bot.tree.command(name="channel")
@app_commands.describe(channel = "# of the channel", sheet= "Name of the sheet")
async def channel(interaction : discord.Interaction, channel :str , sheet :str):
    await interaction.response.send_message(f"{channel} was assigned to {sheet}")
    print(channel)
    #datatest.add_to_json_file('channel.json', sheet, channel)
    sh.writechannel(channel, sheet)

@bot.tree.command(name="create")
@app_commands.describe(channelname = "Name of the channel", sheet= "Name of the sheet")
async def create(interaction : discord.Interaction, channelname :str, sheet :str):
    guild = interaction.guild
    category = bot.get_channel(1218035431078236323)
    sh.copy(sheet)

    channel = await guild.create_text_channel(channelname, category=category)
    new_position = 2  # Define new_position here
    await channel.edit(position=new_position)
    channels = sorted(guild.channels, key=lambda c: c.position)
    channels_positions = {channels[i].id: i for i in range(len(channels))}
    channels_positions[channel.id] = new_position
    id = channel.id
    sh.writechannel(f"<@{channel.id}>", sheet)


@bot.tree.command(name="updatechannelname")
@app_commands.describe(channel = "# of the Channel", new_name= "The new name for the sheet")
async def updatechannelname(interaction : discord.Interaction, channel :str, new_name :str):
    await interaction.response.send_message(f"{channel} was reassigned to {new_name}")
    sh.updatesheet(channel, new_name)

@bot.tree.command(name="updatechannelid")
@app_commands.describe(new_channel = "new # of the Channel", name= "Name of the sheet")
async def updatechannelid(interaction : discord.Interaction, new_channel :str, name :str):
    await interaction.response.send_message(f"{name} was reassigned to {new_channel}")
    sh.updatechannel_id(new_channel, name)

@bot.command()
async def foo(ctx, arg):
    await ctx.send(arg)
    

@bot.tree.command(name= "done")
@app_commands.describe(series= "# of the Series", chapter = "What chapter", role = "What role")
async def assign(interaction : discord.Interaction, series :str, chapter : str, role :str):
    first = None 
    second = None
    target_channel_id = int("1218705159614631946")  # change to actual channel 
    target_channel = bot.get_channel(target_channel_id)
    user = interaction.user.id 
    print("now comes user bevore check" )
    print(user)
    
    role = role.upper()
    if role.upper() in role_dict:
        first, second = role_dict[role]
    if first == None:
        if target_channel is None:
            print("Target channel is None")
        else:
            await interaction.response.send_message(f" '{role.upper()}' is not a valid Role ", ephemeral=True)       
    else:        
        #await target_channel.send(f"{interaction.user.mention} | {series}| CH {chapter} | {role.upper()} | Done")
        await target_channel.send(f"{series} | CH {chapter} | {role.upper()} | Done | {interaction.user.mention}")
        list= [sh.getsheetname(series), chapter, first, second, f"<@{user}>"]   
        sh.write(list, "Done")
        #await interaction.response.send_message("Send", ephemeral=True)

@bot.tree.command(name= "ip")
@app_commands.describe()
async def ip(interaction : discord.Interaction):
    if interaction.user.id == 611962086049710120:
        ip = get('https://api.ipify.org').content.decode('utf8')
        await interaction.response.send_message(ip, ephemeral=True)
    else:
        await interaction.response.send_message("You are not allowed to use this command")
bot.run(TOKEN)