import discord
from discord.ext import commands
from utils.economy_utils import economy_dboperations


class Gambling(commands.Cog, description="Gambling module"):

    def __init__(self, client):
        self.client = client
    
    def gambling_embed(self, ctx: commands.Context):
        embed = discord.Embed(title="Zen | Gambling", color=ctx.author.color)
        return embed

    async def cog_command_error(self, ctx: commands.Context, error):
        embed = self.gambling_embed(ctx)
        if isinstance(error, Exception):
            embed.description = str(error)
            return await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Gambling module is ready!")

    @commands.command()
    async def blackjack(self, ctx: commands.Context, amount: int = None):
        

