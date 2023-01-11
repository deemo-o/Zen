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

class Help(commands.HelpCommand):

    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        
        author = await client.fetch_user(172503861477507072)
        description = f'The following is a list of currently available modules. Type {client.command_prefix}help [module] to display all the commands inside a specific module.\n\n'
        for cog in mapping:
            if cog is not None:
                description += f'**`{cog.qualified_name}`** - {cog.description}\n'

        embed = discord.Embed(title="List of modules", description=description, timestamp=datetime.now(), color=discord.Color.from_rgb(248, 175, 175))
        embed.set_footer(text=f'Made by {author.name}#{author.discriminator}', icon_url=author.avatar)
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog: commands.Cog):

        author = await client.fetch_user(172503861477507072)
        description = f'These are all the available commands for the {cog.qualified_name} module. You can get the specific information about a command by typing {client.command_prefix}help [command] (prefix commands only).\n\n'
        if cog.get_commands() == [] and cog.get_app_commands() == []:
            description = f'This module doesn\'t have any commands yet.'
        else:
            description += "**Prefix commands**\n\n"
            if cog.get_commands() == []:
                description += "This module doesn\'t have any prefix commands.\n"
            elif cog.get_commands() != []:
                for command in cog.get_commands():
                    if command.hidden == True:
                        continue
                    if cog is not None:
                        if command.brief is None:
                            description += f'**`{client.command_prefix}{command.name}`**: No brief description\n'
                        else:
                            description += f'**`{client.command_prefix}{command.name}`**: {command.brief}\n'

            description += "\n**Slash commands**\n\n"
            if cog.get_app_commands() == []:
                description += "This module doesn\'t have any slash commands."
            elif cog.get_app_commands() != []:
                for command in cog.get_app_commands():
                    if cog is not None:
                        if command.description == "…":
                            description += f'**`/{command.name}`**: No brief description\n'
                        else:
                            description += f'**`/{command.name}`**: {command.description}\n'

        embed = discord.Embed(title=f'{cog.qualified_name}', description=description, timestamp=datetime.now(), color=discord.Color.from_rgb(248, 175, 175))
        embed.set_footer(text=f'Made by {author.name}#{author.discriminator}', icon_url=author.avatar)
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command: commands.Command):

        description = command.description
        if description == '':
            description = 'There is no description for this command.'
            
        author = await client.fetch_user(172503861477507072)
        aliases = ''
        if command.aliases != []:
            for alias in command.aliases:
                aliases += f'**`{client.command_prefix}{alias}`**\n'
        else:
            aliases = 'This command doesn\'t have any aliases.'
        description += f'\n\n**Aliases:**\n{aliases}'
        embed = discord.Embed(title=command.name.capitalize(), description=description, timestamp=datetime.now(), color=discord.Color.from_rgb(248, 175, 175))
        embed.set_footer(text=f'Made by {author.name}#{author.discriminator}', icon_url=author.avatar)
        await self.get_destination().send(embed=embed)

    async def command_not_found(self, string):
        return string

    async def send_error_message(self, error):
        if client.get_cog(error.capitalize()):
            await self.send_cog_help(client.get_cog(error.capitalize()))
        else:
            return await super().send_error_message(f'**{error}** is not a module nor a command!')

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = commands.Bot(
    command_prefix="#",
    help_command=Help(),
    intents=discord.Intents.all())

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
            
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        asyncio.run(client.load_extension(f"cogs.{filename[:-3]}"))

load_dotenv()

client.run(os.getenv("TOKEN"))
