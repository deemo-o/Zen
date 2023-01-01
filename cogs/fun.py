import io
import discord
import random
import aiohttp
from discord.ext import commands
from discord import app_commands
 
class Fun(commands.Cog, description="Fun commands."):
    
    def __init__(self, client: commands.Bot):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Fun module has been loaded.")

    @commands.command(brief="Gets a GIF of a hug from an anime", description="This command will display a GIF of a hug from a random anime")
    async def animehug(self, ctx: commands.Context):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://some-random-api.ml/animu/hug") as response:
                if response.status == 200:
                    data = await response.json()
                    await ctx.send(data["link"])

    @commands.command(brief="Gets a GIF of a facepalm from an anime", description="This command will get a GIF of a facepalm from a random anime")
    async def facepalm(self, ctx: commands.Context):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://some-random-api.ml/animu/face-palm") as response:
                if response.status == 200:
                    data = await response.json()
                    await ctx.send(data["link"])

    @commands.command(brief="Gets a random quote from an anime", description="This command will get a random quote from an anime")
    async def animequote(self, ctx: commands.Context):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://some-random-api.ml/animu/quote") as response:
                if response.status == 200:
                    data = await response.json()

                    embed = discord.Embed(title="Zen | Anime Quote", color=ctx.author.top_role.color)
                    embed.description = f"{data['sentence']}"
                    embed.add_field(name="By", value=data["character"], inline=True)
                    embed.add_field(name="From", value=data["anime"], inline=True)
                    
                    await ctx.send(embed=embed)

    @commands.command(brief="Uploads an image with the specified quote with an oogway template", description="This command will upload an image with the quote you specified with an oogway template")
    async def oogway(self, ctx: commands.Context, *, quote: str):
        choices = ["oogway", "oogway2"]
        choice = choices[random.randint(0, 1)]
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://some-random-api.ml/canvas/misc/{choice}?quote={quote}") as response:
                if response.status == 200:
                    data = io.BytesIO(await response.read())
                    await ctx.send(file=discord.File(data, "oogway_quote.png"))

    @commands.command(aliases=["dict"], brief="Gets the definition(s) of the specified word.", description="This command will ge the definition(s) of the word you specified.")
    async def dictionary(self, ctx: commands.Context, *, word: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://some-random-api.ml/others/dictionary?word={word}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    embed = discord.Embed(title="Zen | Dictionary", color=ctx.author.color)
                    embed.add_field(name="Word", value=data["word"].capitalize(), inline=False)
                    embed.add_field(name="Definition", value=data["definition"], inline=False)

                    await ctx.send(embed=embed)

    @app_commands.command(name="coinflip")
    async def slash_coinflip(self, interaction: discord.Interaction):
        if random.randint(0, 1) == 0:
            await interaction.response.send_message("Heads", ephemeral=True)
        elif random.randint(0, 1) == 1:
            await interaction.response.send_message("Tails", ephemeral=True)

async def setup(client):
    await client.add_cog(Fun(client))