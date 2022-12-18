import discord
from discord.ext import commands
from discord.ext.commands.errors import ExtensionAlreadyLoaded, ExtensionNotLoaded, ExtensionNotFound
from discord import app_commands
 
class System(commands.Cog, description="System commands."):
    
    def __init__(self, client: commands.Bot):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("System module has been loaded.")

    @commands.command(brief='Loads a module.', description='This command will load a module.')
    async def load(self, ctx, module):
        try:
            await self.client.load_extension(f'cogs.{module.lower()}')
            await ctx.send(f'Loaded the {module} module.')
        except ExtensionAlreadyLoaded:
            await ctx.send(f'The {module} module is already loaded.')
        except ExtensionNotFound:
            await ctx.send(f"The {module} module does not exist.")

    @commands.command(brief='Unloads a module.', description='This command will unload a module.')
    async def unload(self, ctx, module):
        try:
            if module == "system":
                await ctx.send(f"The system module cannot be unloaded since loading and unloading modules are both done within the system module. Use {self.client.command_prefix}reload instead.")
            else:
                await self.client.unload_extension(f'cogs.{module.lower()}')
                await ctx.send(f'Unloaded the {module} module.')
        except ExtensionNotLoaded:
            await ctx.send(f'The {module} module is already unloaded.')
        except ExtensionNotFound:
            await ctx.send(f"The {module} module does not exist.")
    
    @commands.command(brief='Reloads a module.', description='This command will reload a module.')
    async def reload(self, ctx, module):
        try:
            await self.client.unload_extension(f'cogs.{module.lower()}')
            await self.client.load_extension(f'cogs.{module.lower()}')
            await ctx.send(f"The {module} module has been reloaded.")
        except ExtensionNotLoaded:
            await ctx.send(f'The {module} module is already unloaded.')
        except ExtensionNotFound:
            await ctx.send(f"The {module} module does not exist.")


async def setup(client):
    await client.add_cog(System(client))