import discord
from discord.ext import commands
from discord import app_commands
 
class Yugioh(commands.Cog, description="Yugioh commands."):
    
    def __init__(self, client: commands.Bot):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Yugioh module has been loaded.")

    @commands.command(aliases=["sc"], brief="Searches a card by name.", description="A command that helps you search a Yugioh card.")
    async def searchcard(self, ctx: commands.Context):
        await ctx.send("tikka masala")

async def setup(client):
    await client.add_cog(Yugioh(client))