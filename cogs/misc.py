import discord
from discord.ext import commands
from discord import app_commands
 
class Misc(commands.Cog, description="Misc commands."):
    
    def __init__(self, client: commands.Bot):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Misc module has been loaded.")

async def setup(client):
    await client.add_cog(Misc(client))