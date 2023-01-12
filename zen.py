import asyncio
import datetime
import logging
import os
import discord
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from discord.utils import get
from dotenv import load_dotenv
from zen_utils.help import CustomHelpCommand

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

load_dotenv()

client = commands.Bot(
    command_prefix=os.getenv("COMMAND_PREFIX"),
    intents=discord.Intents.all(),
    case_insensitive=True)

client.help_command = CustomHelpCommand(client)

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        asyncio.run(client.load_extension(f"cogs.{filename[:-3]}"))

@client.event
async def on_ready():
    print("Zen is online!")
    try:
        synced = await client.tree.sync()
        print(f'Synced {len(synced)} application command(s)')
    except Exception as e:
        print(e)

@client.event 
async def on_command_error(ctx, error): 
    if isinstance(error, commands.CommandNotFound): 
        await ctx.send(f"This command does not exist! Type {client.command_prefix}help if you are lost.")
    else:
        print(error)

client.run(os.getenv("TOKEN"))
