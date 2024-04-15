import discord
from discord import app_commands
from discord.ext import commands
import sheet as sh
import logging
from dotenv import load_dotenv
import os
from requests import get
from discord.ext import tasks
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Bot information
TOKEN = os.getenv("TOKEN")  # Discord Token. Loads the token from the .env file
BOT_ID = 1218682240947458129  # User id of the bot

# Channel IDs
ASSIGNMENT_CHANNEL = 1218705159614631946  # Channel ID of the assignment channel
CHECKUP_CHANNEL = 1224453260543266907  # Channel ID of Hdydrometer
ONESHOT_CHANNEL = 1225634854390206494  # Channel ID of the oneshot channel


# Role dictionary
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

# Other configurations
COMMAND_PREFIX = '$'
