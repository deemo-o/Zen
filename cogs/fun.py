import io
import discord
import random
import aiohttp
from discord.ext import commands
from discord import app_commands
from PyDictionary import PyDictionary
 
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

    @commands.command(aliases=["dict", "Dict"], brief="Gets the definition(s) of the specified word.", description="This command will ge the definition(s) of the word you specified.")
    async def dictionary(self, ctx: commands.Context, *, word: str):
        dictionary = PyDictionary()
        definitions = dictionary.meaning(word)

        if not definitions:
            return await ctx.send("This word doesn't exist in our dictionary!")
        nouns, adjectives, verbs = "", "", ""
        max_char = 1024
        nouns_char, adj_char, verbs_char = 0, 0, 0

        if "Noun" in definitions.keys():
            for index, definition in enumerate(definitions["Noun"]):
                nouns_char += len(definition)
                if nouns_char > max_char:
                    break
                nouns += f"{index + 1} - {definition.capitalize()}\n"
        if "Adjective" in definitions.keys():
            for index, definition in enumerate(definitions["Adjective"]):
                adj_char += len(definition)
                if adj_char > max_char:
                    break
                adjectives += f"{index + 1} - {definition.capitalize()}\n"
        if "Verb" in definitions.keys():
            for index, definition in enumerate(definitions["Verb"]):
                verbs_char += len(definition)
                if verbs_char > max_char:
                    break
                verbs += f"{index + 1} - {definition.capitalize()}\n"

        embed = discord.Embed(title="Zen | Dictionary", color=ctx.author.color)
        embed.add_field(name="Word", value=word.capitalize(), inline=False)

        if nouns:
            embed.add_field(name="Noun", value=nouns, inline=False)
        if adjectives:
            embed.add_field(name="Adjective", value=adjectives, inline=False)
        if verbs:
            embed.add_field(name="Verb", value=verbs, inline=False)
            
        await ctx.send(embed=embed)
    
    @commands.command(aliases=["Syn", "syn", "Synonym"], brief="Gets the synonym(s) of the specified word.", description="This command will ge the synonym(s) of the word you specified.")
    async def synonym(self, ctx: commands.Context, *, word: str):
        dictionary = PyDictionary()
        synonyms = dictionary.synonym("Life")
        await ctx.send(synonyms)

    @app_commands.command(name="coinflip")
    async def slash_coinflip(self, interaction: discord.Interaction):
        if random.randint(0, 1) == 0:
            await interaction.response.send_message("Heads", ephemeral=True)
        elif random.randint(0, 1) == 1:
            await interaction.response.send_message("Tails", ephemeral=True)

async def setup(client):
    await client.add_cog(Fun(client))