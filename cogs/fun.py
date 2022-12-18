import discord
import random
from discord.ext import commands
from discord import app_commands
 
class Fun(commands.Cog, description="Fun commands."):
    
    def __init__(self, client: commands.Bot):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Fun module has been loaded.")

    @app_commands.command(name="coinflip")
    async def slash_coinflip(self, interaction: discord.Interaction):
        if random.randint(0, 1) == 0:
            await interaction.response.send_message("Heads", ephemeral=True)
        elif random.randint(0, 1) == 1:
            await interaction.response.send_message("Tails", ephemeral=True)

async def setup(client):
    await client.add_cog(Fun(client))