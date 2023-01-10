import json
import discord
import aiohttp
import Paginator
from discord.ext import commands
from discord import app_commands
from yugioh_utils import yugioh_operations
 
class Yugioh(commands.Cog, description="Yugioh commands."):
    
    def __init__(self, client: commands.Bot):
        self.client = client
        
    def cog_command_error(self, ctx: commands.Context, error):
        print(error)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Yugioh module has been loaded.")

    @commands.command(aliases=["scn"], brief="Searches a card by name.", description="A command that helps you search a Yugioh card.")
    async def searchcard(self, ctx: commands.Context, *card: str):
        card_str = ""
        async with aiohttp.ClientSession() as session: 
            for i in range(len(card)):
                if card[i] != card[len(card)-1]:
                    card_str += card[i] + " "
                else:
                    card_str += card[i]

            async with session.get(f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={card_str}") as response:
                if response.status == 200:
                    data = await response.json()

                    lvl, xyzlvl = '<:level:1059718470448730192>', '<:blacklevel:1059725946258739231>'
                    spell, trap = "<:spell:1060048999765250068>","<:trap:1060049002466381834>"
                    ricon, attricon = [], []
                    race = data['data'][0]['race']
                    
                    yugioh_operations.getricon(race,ricon)
                    
                    if "Monster" in data['data'][0]['type']:
                        print("hello", data['data'][0]['type'])
                        att = data['data'][0]['attribute']

                        yugioh_operations.getattricon(att, attricon)

                        if data['data'][0]['type'] != "Normal Monster":
                            mstype = "/Effect"
                            if data["data"][0]["type"] == "Link Monster":
                                lvl = data["data"][0]["linkval"]
                                markers = ''
                                for i in data["data"][0]["linkmarkers"]:
                                    if i != data["data"][0]["linkmarkers"][-1]:
                                        markers += i + " | "
                                    else:
                                        markers += i

                                embed = discord.Embed(
                                color=0x1abc9c,
                                title=f"**{data['data'][0]['name']}**",
                                description=f"**Type**: {ricon[0]} {data['data'][0]['race']}/{data['data'][0]['type']}{mstype}\n**Attribute**: {attricon[0]} {data['data'][0]['attribute']}\n**Link-{lvl} | ** **ATK**: {data['data'][0]['atk']}\n**Markers**: {'<:link_summon:1062107300489334834>'} {markers} \n")
                        
                                embed.insert_field_at(index=1,name="Description", value=f"{data['data'][0]['desc']}",inline=False)
                                embed.set_thumbnail(url=data['data'][0]['card_images'][0]['image_url_cropped'])

                            else:
                                if data["data"][0]["type"] == "XYZ Monster":
                                    lvl = xyzlvl  

                                embed = discord.Embed(
                                color=0x1abc9c,
                                title=f"**{data['data'][0]['name']}**",
                                description=f"**Type**: {ricon[0]} {data['data'][0]['race']}/{data['data'][0]['type']}{mstype}\n**Attribute**: {attricon[0]} {data['data'][0]['attribute']}\n**Level**: {lvl} {int(data['data'][0]['level'])} **ATK**: {data['data'][0]['atk']} **DEF**: {data['data'][0]['def']}")
                        
                                embed.insert_field_at(index=1,name="Description", value=f"{data['data'][0]['desc']}",inline=False)
                                embed.set_thumbnail(url=data['data'][0]['card_images'][0]['image_url_cropped'])


                    elif data['data'][0]['type'] == "Trap Card":
                        embed = discord.Embed(
                        color=0x1abc9c,
                        title=f"**{data['data'][0]['name']}**",
                        description=f"**Type**: {trap} {data['data'][0]['type']} {ricon[0]} \n")
                
                        embed.insert_field_at(index=1,name="Description", value=f"{data['data'][0]['desc']}",inline=False)
                        embed.set_thumbnail(url=data['data'][0]['card_images'][0]['image_url_cropped'])

                    elif data['data'][0]['type'] == "Spell Card":
                        embed = discord.Embed(
                        color=0x1abc9c,
                        title=f"**{data['data'][0]['name']}**",
                        description=f"**Type**: {spell} {data['data'][0]['type']} {ricon[0]} \n")
                
                        embed.insert_field_at(index=1,name="Description", value=f"{data['data'][0]['desc']}",inline=False)
                        embed.set_thumbnail(url=data['data'][0]['card_images'][0]['image_url_cropped'])
                    else:
                        mstype = "/Normal"

                
            #API from http://yugiohprices.com 
            async with session.get(f"https://yugiohprices.com/api/get_card_prices/{card_str}") as response:
                if response.status == 200:
                    embed2 = discord.Embed(
                        title="Card Sets",
                        color=0x1abc9c
                    )
                    data2 = await response.json()
                    if data2['status'] == "success":
                        for i in range(len(data2['data'])):
                            if data2['data'][i]['price_data']['status'] == "success":
                                embed2.add_field(name=data2['data'][i]['name'], value=f"{data2['data'][i]['print_tag']}\n{data2['data'][i]['rarity']}\n**Lowest: **${data2['data'][i]['price_data']['data']['prices']['low']}**\nHighest: **${data2['data'][i]['price_data']['data']['prices']['high']}\n**Average**: ${data2['data'][i]['price_data']['data']['prices']['average']}\nLast updated on {data2['data'][i]['price_data']['data']['prices']['updated_at']}", inline=False)
                                
                    embed2.set_image(url= "https://static.wikia.nocookie.net/p__/images/2/2f/Winged-Kuriboh.png/revision/latest?cb=20161213005825&path-prefix=protagonist")
                    embed2.set_thumbnail(url="https://i.gifer.com/origin/e0/e02ce86bcfd6d1d6c2f775afb3ec8c01_w200.gif")
                    
                    embeds = [embed,embed2,]
                    PreviousButton = discord.ui.Button(emoji='⬅️')
                    NextButton = discord.ui.Button(emoji='➡️')
                    PageCounterStyle = discord.ButtonStyle(value=2)
                    InitialPage = 0
                    timeout = 42069 

                    await Paginator.Simple(
                        PreviousButton=PreviousButton,
                        NextButton=NextButton,
                        PageCounterStyle=PageCounterStyle,
                        InitialPage=InitialPage,
                        timeout=timeout).start(ctx, pages=embeds)

async def setup(client):
    await client.add_cog(Yugioh(client))
