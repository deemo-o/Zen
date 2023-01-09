import io
import discord
import random
import aiohttp
from discord.ext import commands
from discord import app_commands
from PyDictionary import PyDictionary
from wordhoard import Antonyms, Synonyms
import Paginator


class Fun(commands.Cog, description="Fun commands."):

    def __init__(self, client: commands.Bot):
        self.client = client

    def getSynOrAnt(self, method, word):
        methods = {
            "synonym": Synonyms(search_string=word).find_synonyms(),
            "antonym": Antonyms(search_string=word).find_antonyms()
        }
        if "Please verify that the word is spelled correctly." in methods[method]:
            raise Exception
        return methods[method]

    def fillEmbed(self, title, word, results):
        embeds = []
        fields = []
        field = []
        max_char = 1024
        for index, result in enumerate(results):
            max_char -= len(result) + 2
            if max_char > 0:
                field.append(result)
                if index == len(results) - 1:
                    fields.append(field)
                    field = []
            else:
                fields.append(field)
                field = []
                max_char = 1024
        for field in fields:
            page = discord.Embed(title=f"Zen | Thesaurus")
            page.add_field(name="Word", value=f"{word.title()}", inline=False)
            page.add_field(name=f"{title}", value=f"{', '.join(field)}", inline=False)
            embeds.append(page)
        return embeds

    @commands.Cog.listener()
    async def on_ready(self):
        print("Fun module has been loaded.")

    @commands.command(brief="Gets a GIF of a hug from an anime",
                      description="This command will display a GIF of a hug from a random anime")
    async def animehug(self, ctx: commands.Context):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://some-random-api.ml/animu/hug") as response:
                if response.status == 200:
                    data = await response.json()
                    await ctx.send(data["link"])

    @commands.command(brief="Gets a GIF of a facepalm from an anime",
                      description="This command will get a GIF of a facepalm from a random anime")
    async def facepalm(self, ctx: commands.Context):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://some-random-api.ml/animu/face-palm") as response:
                if response.status == 200:
                    data = await response.json()
                    await ctx.send(data["link"])

    @commands.command(brief="Gets a random quote from an anime",
                      description="This command will get a random quote from an anime")
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

    @commands.command(brief="Uploads an image with the specified quote with an oogway template",
                      description="This command will upload an image with the quote you specified with an oogway template")
    async def oogway(self, ctx: commands.Context, *, quote: str):
        choices = ["oogway", "oogway2"]
        choice = choices[random.randint(0, 1)]
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://some-random-api.ml/canvas/misc/{choice}?quote={quote}") as response:
                if response.status == 200:
                    data = io.BytesIO(await response.read())
                    await ctx.send(file=discord.File(data, "oogway_quote.png"))

    @commands.command(aliases=["dict"], brief="Gets the definition(s) of the specified word.",
                      description="This command will get the definition(s) of the word you specified.")
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

    @commands.command(aliases=["syn"], brief="Gets the synonym(s) of the specified word.",
                      description="This command will get the synonym(s) of the word you specified.")
    async def synonym(self, ctx: commands.Context, *, word: str):
        try:
            results = self.getSynOrAnt("synonym", word)
            embeds = self.fillEmbed("Synonyms", word, results)
            await Paginator.Simple().start(ctx, pages=embeds)
        except:
            embed = discord.Embed(title="Zen | Thesaurus", description=f"No synonyms were found for the word: {word}")
            await ctx.send(embed=embed)

    @commands.command(aliases=["ant"], brief="Gets the antonym(s) of the specified word.",
                      description="This command will get the antonym(s) of the word you specified.")
    async def antonym(self, ctx: commands.Context, *, word: str):
        try:
            results = self.getSynOrAnt("antonym", word)
            embeds = self.fillEmbed("Antonyms", word, results)
            await Paginator.Simple().start(ctx, pages=embeds)
        except:
            embed = discord.Embed(title="Zen | Thesaurus", description=f"No antonyms were found for the word: {word}")
            await ctx.send(embed=embed)

    @app_commands.command(name="coinflip")
    async def slash_coinflip(self, interaction: discord.Interaction):
        if random.randint(0, 1) == 0:
            await interaction.response.send_message("Heads", ephemeral=True)
        elif random.randint(0, 1) == 1:
            await interaction.response.send_message("Tails", ephemeral=True)

    @commands.command(aliases=["8ball"], brief="Ask a question, and get an answer from the 8ball",
                      description="This command will take in a prompt and return the probability of it happening")
    async def eightball(self, ctx: commands.Context, *, arg=None):
        if arg is None:
            await ctx.send(embed=discord.Embed(title="Zen | Fun",
                                               description="Seems to me that you forgot to ask your question...Try again!"))
        else:
            rng = random.randrange(1, 8)

            def possibilities(number):
                switcher = {
                    1: "Definately a no!",
                    2: "No.",
                    3: "I don't know about that chief!",
                    4: "Ouh, that is risky!",
                    5: "Maybe!",
                    6: "Most likely!",
                    7: "Yes!",
                    8: "HELL YEAH!",
                }

                return switcher.get(number, "Nothing")

            await ctx.send(embed=discord.Embed(title="Zen | Fun",
                                           description=f"""The eight ball has spoken, the answer is: {possibilities(rng)}"""))


async def setup(client):
    await client.add_cog(Fun(client))
