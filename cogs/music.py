import discord
from discord.ext import commands
from discord import app_commands
 
class Music(commands.Cog, description="Music commands."):
    
    def __init__(self, client: commands.Bot):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Music module has been loaded.")

async def setup(client):
    await client.add_cog(Music(client))