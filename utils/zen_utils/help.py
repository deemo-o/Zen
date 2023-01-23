import discord
from discord.ext import commands
from datetime import datetime

class CustomHelpCommand(commands.HelpCommand):

    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client

    async def send_bot_help(self, mapping):
        description = f'The following is a list of currently available modules. Type {self.client.command_prefix}help [module] to display all the commands inside a specific module.\n\n'
        for cog in mapping:
            if cog is not None:
                if cog.qualified_name == "Moderation" or cog.qualified_name == "System":
                    if self.context.author.guild_permissions.ban_members:
                        description += f'**`{cog.qualified_name}`** - {cog.description}\n'
                else:
                    description += f'**`{cog.qualified_name}`** - {cog.description}\n'

        embed = discord.Embed(title="List of modules", description=description, timestamp=datetime.now(), color=discord.Color.from_rgb(248, 175, 175))
        embed.set_footer(text=f'Made by Debo#4828', icon_url="https://cdn.discordapp.com/avatars/172503861477507072/c9caab2bdc40c15c27d3983dca7f9071.png?size=1024")
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog: commands.Cog):
        description = f'These are all the available commands for the {cog.qualified_name} module. You can get the specific information about a command by typing {self.client.command_prefix}help [command] (prefix commands only).\n\n'
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
                            description += f'**`{self.client.command_prefix}{command.name}`**: No brief description\n'
                        else:
                            if "Staff" in command.brief:
                                if self.context.author.guild_permissions.ban_members:
                                    description += f'**`{self.client.command_prefix}{command.name}`**: {command.brief}\n'
                            else:
                                description += f'**`{self.client.command_prefix}{command.name}`**: {command.brief}\n'

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
        embed.set_footer(text=f'Made by Debo#4828', icon_url="https://cdn.discordapp.com/avatars/172503861477507072/c9caab2bdc40c15c27d3983dca7f9071.png?size=1024")
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command: commands.Command):
        description = command.description
        if description == '':
            description = 'There is no description for this command.'
            
        aliases = ''
        if command.aliases != []:
            for alias in command.aliases:
                aliases += f'**`{self.client.command_prefix}{alias}`**\n'
        else:
            aliases = 'This command doesn\'t have any aliases.'
        description += f'\n\n**Aliases:**\n{aliases}'
        embed = discord.Embed(title=command.name.capitalize(), description=description, timestamp=datetime.now(), color=discord.Color.from_rgb(248, 175, 175))
        embed.set_footer(text=f'Made by Debo#4828', icon_url="https://cdn.discordapp.com/avatars/172503861477507072/c9caab2bdc40c15c27d3983dca7f9071.png?size=1024")
        await self.get_destination().send(embed=embed)

    async def command_not_found(self, string):
        return string

    async def send_error_message(self, error):
        try:
            for cog in self.get_bot_mapping():
                if error.capitalize() == cog.qualified_name:
                    return await self.send_cog_help(cog)
        except:
            return await super().send_error_message(f'**{error}** is not a module nor a command!')