import io
import discord
import random
import aiohttp
from discord.ext import commands
from discord import app_commands
from PyDictionary import PyDictionary
from wordhoard import Antonyms, Synonyms
import Paginator
import googletrans
from googletrans import Translator
import typing

class Fun(commands.Cog, description="Fun commands."):
    
    def __init__(self, client: commands.Bot):
        self.client = client
    
    def getSynOrAnt(self, method, word):
        methods = {
            "synonym" : Synonyms(search_string=word).find_synonyms(),
            "antonym" : Antonyms(search_string=word).find_antonyms()
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

    @commands.command(aliases=["dict"], brief="Gets the definition(s) of the specified word.", description="This command will get the definition(s) of the word you specified.")
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

    @commands.command(aliases=["syn"], brief="Gets the synonym(s) of the specified word.", description="This command will get the synonym(s) of the word you specified.")
    async def synonym(self, ctx: commands.Context, *, word: str):
        try:
            results = self.getSynOrAnt("synonym", word)
            embeds = self.fillEmbed("Synonyms", word, results)
            await Paginator.Simple().start(ctx, pages=embeds)
        except:
            embed = discord.Embed(title="Zen | Thesaurus", description=f"No synonyms were found for the word: {word}")
            await ctx.send(embed=embed)
            
    @commands.command(aliases=["ant"], brief="Gets the antonym(s) of the specified word.", description="This command will get the antonym(s) of the word you specified.")
    async def antonym(self, ctx: commands.Context, *, word: str):
        try:
            results = self.getSynOrAnt("antonym", word)
            embeds = self.fillEmbed("Antonyms", word, results)
            await Paginator.Simple().start(ctx, pages=embeds)
        except:
            embed = discord.Embed(title="Zen | Thesaurus", description=f"No antonyms were found for the word: {word}")
            await ctx.send(embed=embed)

    @commands.command(aliases=["trans"], brief="Translates what the user inputs.", description="")
    async def translate(self, ctx: commands.Context, *, text_to_translate: typing.Optional[str] = None):
        user = ctx.author
        translator = Translator()
    
        async def invalid_input_message():
            error_message = discord.Embed(title="Zen | Translation", description="Couldn't find anything that matches your input. Try again.")
            await ctx.send(embed=error_message, delete_after=120)

        async def exit_message():
            exit_message = discord.Embed(title="Zen | Translation", description="Exiting now. See you next time.")
            await ctx.send(embed=exit_message, delete_after=120)

        async def switch_to_default_input(input):
            if input == 'source':
                notification = discord.Embed(title="Zen | Translation", description="I will do my best to detect the language your text is in.")
                await ctx.send(embed=notification, delete_after=120)
                return 'auto'
            else: 
                notification = discord.Embed(title="Zen | Translation", description="Your text will be translated into English.")
                await ctx.send(embed=notification, delete_after=120)
                return 'en'

        def print_all_languages(languages):
            pages=[]
            field = ""
            field_count = 0
            page = discord.Embed(title=f"Zen | Translation")
            for index, (language, iso_code) in enumerate(languages.items()):
                if index % 20 == 0 and index != 0:
                    page.add_field(name='Languages', value=field, inline=True)
                    field_count += 1
                    if field_count == 2:
                        field_count = 0
                        pages.append(page)
                        page = discord.Embed(title=f"Zen | Translation")
                        field = "" + f"{language} : {iso_code}\n"
                    else: 
                        page.add_field(name=chr(173), value=chr(173), inline=True)
                        field = "" + f"{language} : {iso_code}\n"
                else:
                    field += f"{language} : {iso_code}\n"
            return pages

        def check(msg):
            return msg.channel == ctx.channel and msg.author == user

        async def ask_input(answer_for):
            if answer_for == 'source':
                source_language_input_explanation = discord.Embed(title="Zen | Translation", description="""Let's get started: \n
                Type the ISO 639 code of the language your text is in (Most will be ISO 639-1, i.e 2 letters).\n
                Type "n", and I will do my best to detect the language myself.\n  
                Type the language in whole if you don't know the code for your language, and I will check for you.\n
                Type "all", and I will show you all the languages I know and their respective ISO 639 code.\n
                Type "e" to exit.""")
                await ctx.send(embed= source_language_input_explanation, delete_after=120)
            else:
                destination_language_input_explanation = discord.Embed(title="Zen | Translation", description="""Moving on: \n
                Type the ISO 639 code of the language you wish to translate the text in.\n
                Type "n", and I will translate it into English by default.\n  
                Type the language in whole if you don't know the code for the language, and I will check for you.\n
                Type "all", and I will show you all the languages I know and their respective ISO 639 code.\n
                Type "e" to exit.""")
                await ctx.send(embed=destination_language_input_explanation, delete_after=120)

            input_object = await self.client.wait_for("message", check=check, timeout=60)
            input = input_object.content.lower()
            
            if input in ['e', 'exit']:
                await exit_message()
            elif input in ["n", "none"]:
                return await switch_to_default_input(answer_for)
            elif input in ["a", "all"]:
                await Paginator.Simple().start(ctx, pages=print_all_languages(googletrans.LANGCODES))
                return await ask_input(answer_for)
            else:
                if input in googletrans.LANGUAGES:
                    return input
                elif input in googletrans.LANGCODES:
                    await ctx.send(embed=discord.Embed(title="Zen | Translation", description=f"Found it! {input} : {googletrans.LANGCODES[input]}"), delete_after=120)
                    input = googletrans.LANGCODES[input]
                    return input 
                else:
                    await invalid_input_message()
                    return await ask_input(answer_for)

        async def get_text():
            notification = discord.Embed(title="Zen | Translation", description="Woops! Don't forget to type in want you want me to translate next time. Type it in now, I'll note it dow.")
            await ctx.send(embed=notification, delete_after=120)
            input_object = await self.client.wait_for("message", check=check, timeout=60)
            input = input_object.content
            return input

        async def translate_text(original_text, source, destination):
            translate_object = translator.translate(original_text, src=source, dest=destination)
            result, pronounciation = translate_object.text, translate_object.pronunciation 
            await ctx.send(embed=discord.Embed(title="Zen | Translation", description=f"{original_text}\n> {result}\n> {pronounciation}"), delete_after=120)

        async def start():
            source_language = await ask_input('source')
            if not source_language: return
            destination_language = await ask_input('destination')
            if not destination_language: return
            await translate_text(text_to_translate, source_language, destination_language)

        if not text_to_translate:
                text_to_translate = await get_text()
        await start()
            
    @app_commands.command(name="coinflip")
    async def slash_coinflip(self, interaction: discord.Interaction):
        if random.randint(0, 1) == 0:
            await interaction.response.send_message("Heads", ephemeral=True)
        elif random.randint(0, 1) == 1:
            await interaction.response.send_message("Tails", ephemeral=True)

async def setup(client):
    await client.add_cog(Fun(client))