import json
import discord
import aiohttp
import Paginator
import requests
from forex_python.converter import CurrencyRates
from discord.ext import commands
from discord import app_commands
from yugioh_utils import yugioh_operations
from database_utils import yugioh_database
 
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
        c = CurrencyRates()
        cex = c.get_rate("USD","CAD")
        lvl, xyzlvl = '<:level:1059718470448730192>', '<:blacklevel:1059725946258739231>'
        spell, trap = "<:spell:1060048999765250068>","<:trap:1060049002466381834>"
        for i in range(len(card)):
                if card[i] != card[len(card)-1]:
                    card_str += card[i] + " "
                else:
                    card_str += card[i]

        async with aiohttp.ClientSession() as session:
            found = False
            connected = yugioh_database.connect()
            result = yugioh_database.getCardByName(connected, card_str)
            print(result)
            if result != []:
                
                found = True
                embeds = []
                    #API from http://yugiohprices.com 
                async with session.get(f"https://yugiohprices.com/api/get_card_prices/{card_str}") as response:
                    if response.status == 200:
                        ricon, attricon = [], []
                        race = result[0][5]
                        yugioh_operations.getricon(race, ricon)
                        # description=f"**Type**: {ricon[0]} {data['data'][0]['race']}/{data['data'][0]['type']}{mstype}\n**Attribute**: {attricon[0]} {data['data'][0]['attribute']}\n**Link-{lvl} | ** **ATK**: {data['data'][0]['atk']}\n**Markers**: {'<:link_summon:1062107300489334834>'} {markers} \n")
                        #description=f"**Type**: {ricon[0]} {result[0][5]}/{result[0][3]}{mstype}\n**Attribute**: {attricon[0]} {result[0][4]}\n**Level**: {lvl} {int(result[0][6])} **ATK**: {result[0][8]} **DEF**: {result[0][9]}")
                        if "Monster" in result[0][3]:
                            att = result[0][4]

                            yugioh_operations.getattricon(att, attricon)

                            if result[0][3] != "Normal Monster":
                                mstype = "/Effect"
                                if result[0][3] == "Link Monster":

                                    embed = discord.Embed(
                                    color=0x1abc9c,
                                    title=f"**{result[0][2]}**",
                                    description=f"**Type**: {ricon[0]} {result[0][5]}/{result[0][3]}{mstype}\n**Attribute**: {attricon[0]} {result[0][4]}\n**Link-{result[0][6]} | ** **ATK**: {result[0][9]}\n**Markers**: {'<:link_summon:1062107300489334834>'} {result[0][6]} \n")
                            
                                    embed.insert_field_at(index=1,name="Description", value=f"{result[0][8]}",inline=False)
                                    # embed.set_thumbnail(url=data['data'][0]['card_images'][0]['image_url_cropped'])
                                    embeds.append(embed)
                                else:
                                    if result[0][3] == "XYZ Monster":
                                        mstype = "/Effect"
                                        lvl = xyzlvl  
                                    
                                        yugioh_operations.getattricon(result[0][4], attricon)
                                        embed = discord.Embed(
                                                    color=0x1abc9c,
                                                    title=f"**{result[0][2]}**",
                                                    description=f"**Type**: {ricon[0]} {result[0][5]}/{result[0][3]}{mstype}\n**Attribute**: {attricon[0]} {result[0][4]}\n**Level**: {lvl} {int(result[0][6])} **ATK**: {result[0][9]} **DEF**: {result[0][10]}")

                                        embed.insert_field_at(index=1,name="Description", value=f"{result[0][8]}",inline=False)
                                        # embed.set_thumbnail(url=data['data'][0]['card_images'][0]['image_url_cropped'])
                                        embeds.append(embed)

                        elif result[0][3] == "Trap Card":
                            embed = discord.Embed(
                            color=0x1abc9c,
                            title=f"**{result[0][2]}**",
                            description=f"**Type**: {trap} {result[0][3]} {ricon[0]} \n")
                    
                            embed.insert_field_at(index=1,name="Description", value=f"{result[0][8]}",inline=False)
                            # embed.set_thumbnail(url=data['data'][0]['card_images'][0]['image_url_cropped'])
                            embeds.append(embed)

                        elif result[0][3] == "Spell Card":
                            embed = discord.Embed(
                            color=0x1abc9c,
                            title=f"**{result[0][2]}**",
                            description=f"**Type**: {spell} {result[0][3]} {ricon[0]} \n")
                    
                            embed.insert_field_at(index=1,name="Description", value=f"{result[0][8]}",inline=False)
                            # embed.set_thumbnail(url=data['data'][0]['card_images'][0]['image_url_cropped'])
                            embeds.append(embed)

                        else:
                            mstype = "/Normal"

                        data2 = await response.json()
                        if data2['status'] == "success":
                            embed2 = discord.Embed(
                            title="Card Sets",
                            color=0x1abc9c
                        )
                            for i in range(len(data2['data'])):
                                if (i + 1) % 5 > 0:
                                    if data2['data'][i]['price_data']['status'] == "success":
                                        clow = '%.2f' % (cex * data2['data'][i]['price_data']['data']['prices']['low'])
                                        chigh = '%.2f' % (cex * data2['data'][i]['price_data']['data']['prices']['high'])
                                        cavg = '%.2f' % (cex * data2['data'][i]['price_data']['data']['prices']['average'])
                                        
                                        embed2.add_field(name=data2['data'][i]['name'], value=f"{data2['data'][i]['print_tag']}\n{data2['data'][i]['rarity']}\n**Lowest: **US${data2['data'][i]['price_data']['data']['prices']['low']} | C${str(clow)}**\nHighest: **US${data2['data'][i]['price_data']['data']['prices']['high']} | C${str(chigh)}\n**Average**: US${data2['data'][i]['price_data']['data']['prices']['average']} | C${str(cavg)}\nLast updated on {data2['data'][i]['price_data']['data']['prices']['updated_at']}", inline=False)
                                        if i == len(data2['data'])-1:
                                            embed2.set_image(url= "https://static.wikia.nocookie.net/p__/images/2/2f/Winged-Kuriboh.png/revision/latest?cb=20161213005825&path-prefix=protagonist")
                                            embed2.set_thumbnail(url="https://i.gifer.com/origin/e0/e02ce86bcfd6d1d6c2f775afb3ec8c01_w200.gif")
                                            embeds.append(embed2)
                                            embed2 = discord.Embed(
                                                title="Card Sets",
                                                color=0x1abc9c
                                            )
                                    if data2['data'][i]['price_data']['status'] == "fail":
                                        embed2.add_field(name=data2['data'][i]['name'], value=f"{data2['data'][i]['print_tag']}\n{data2['data'][i]['rarity']}\n **{data2['data'][i]['price_data']['message']}** 🥹", inline=False)
                                        if i == len(data2['data'])-1:
                                            embed2.set_image(url= "https://static.wikia.nocookie.net/p__/images/2/2f/Winged-Kuriboh.png/revision/latest?cb=20161213005825&path-prefix=protagonist")
                                            embed2.set_thumbnail(url="https://i.gifer.com/origin/e0/e02ce86bcfd6d1d6c2f775afb3ec8c01_w200.gif")
                                            embeds.append(embed2)
                                            embed2 = discord.Embed(
                                                title="Card Sets",
                                                color=0x1abc9c
                                            )
                                else:
                                    if data2['data'][i]['price_data']['status'] == "success":
                                            embed2.add_field(name=data2['data'][i]['name'], value=f"{data2['data'][i]['print_tag']}\n{data2['data'][i]['rarity']}\n**Lowest: **US${data2['data'][i]['price_data']['data']['prices']['low']} | C${str(clow)}**\nHighest: **US${data2['data'][i]['price_data']['data']['prices']['high']} | C${str(chigh)}\n**Average**: US${data2['data'][i]['price_data']['data']['prices']['average']} | C${str(cavg)}\nLast updated on {data2['data'][i]['price_data']['data']['prices']['updated_at']}", inline=False)
                                    
                                    if data2['data'][i]['price_data']['status'] == "fail":
                                        embed2.add_field(name=data2['data'][i]['name'], value=f"{data2['data'][i]['print_tag']}\n{data2['data'][i]['rarity']}\n **{data2['data'][i]['price_data']['message']}** 🥹", inline=False)

                                    embed2.set_image(url= "https://static.wikia.nocookie.net/p__/images/2/2f/Winged-Kuriboh.png/revision/latest?cb=20161213005825&path-prefix=protagonist")
                                    embed2.set_thumbnail(url="https://i.gifer.com/origin/e0/e02ce86bcfd6d1d6c2f775afb3ec8c01_w200.gif")
                                    embeds.append(embed2)
                                    embed2 = discord.Embed(
                                        title="Card Sets",
                                        color=0x1abc9c
                                    )


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

            else:
                async with session.get(f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={card_str}") as response:
                    if response.status == 200:
                        found = True
                        data = await response.json()
                        ricon, attricon = [], []
                        race = data['data'][0]['race']
                        
                        yugioh_operations.getricon(race, ricon)
                        
                        if "Monster" in data['data'][0]['type']:
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
                                    
                                    yugioh_database.insertCard(connected, int(data['data'][0]['id']), str(data['data'][0]['name']), str(data['data'][0]['type']), str(data['data'][0]['attribute']), str(data['data'][0]['race']), lvl, markers, str(data['data'][0]['desc']), int(data['data'][0]['atk']), None,"blob")

                                else:
                                    if data["data"][0]["type"] == "XYZ Monster":
                                        lvl = xyzlvl  

                                    embed = discord.Embed(
                                    color=0x1abc9c,
                                    title=f"**{data['data'][0]['name']}**",
                                    description=f"**Type**: {ricon[0]} {data['data'][0]['race']}/{data['data'][0]['type']}{mstype}\n**Attribute**: {attricon[0]} {data['data'][0]['attribute']}\n**Level**: {lvl} {int(data['data'][0]['level'])} **ATK**: {data['data'][0]['atk']} **DEF**: {data['data'][0]['def']}")
                            
                                    embed.insert_field_at(index=1,name="Description", value=f"{data['data'][0]['desc']}",inline=False)
                                    embed.set_thumbnail(url=data['data'][0]['card_images'][0]['image_url_cropped'])

                                    yugioh_database.insertCard(connected, int(data['data'][0]['id']), str(data['data'][0]['name']), str(data['data'][0]['type']), str(data['data'][0]['attribute']), str(data['data'][0]['race']), int(data['data'][0]['level']), None, str(data['data'][0]['desc']), int(data['data'][0]['atk']), int(data['data'][0]['def']),"blob")


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
                        
                        
                    else:
                        embed = discord.Embed(title="Oops! An error occured...",
                                            color=0x1abc9c,     
                                            description="Can't find the following card: **{}**".format(card_str))
                        embed.set_image(url="https://i.pinimg.com/originals/2e/55/85/2e5585721617cb5d596f24b4cf28c0b6.gif")
                    
                if found == True:    
                    embeds = []
                    #API from http://yugiohprices.com 
                    async with session.get(f"https://yugiohprices.com/api/get_card_prices/{card_str}") as response:
                        if response.status == 200:
                            
                            embeds.append(embed)
                            data2 = await response.json()
                            if data2['status'] == "success":
                                embed2 = discord.Embed(
                                title="Card Sets",
                                color=0x1abc9c
                            )
                                for i in range(len(data2['data'])):
                                    if (i + 1) % 5 > 0:
                                        if data2['data'][i]['price_data']['status'] == "success":
                                            clow = '%.2f' % (cex * data2['data'][i]['price_data']['data']['prices']['low'])
                                            chigh = '%.2f' % (cex * data2['data'][i]['price_data']['data']['prices']['high'])
                                            cavg = '%.2f' % (cex * data2['data'][i]['price_data']['data']['prices']['average'])
                                            
                                            embed2.add_field(name=data2['data'][i]['name'], value=f"{data2['data'][i]['print_tag']}\n{data2['data'][i]['rarity']}\n**Lowest: **US${data2['data'][i]['price_data']['data']['prices']['low']} | C${str(clow)}**\nHighest: **US${data2['data'][i]['price_data']['data']['prices']['high']} | C${str(chigh)}\n**Average**: US${data2['data'][i]['price_data']['data']['prices']['average']} | C${str(cavg)}\nLast updated on {data2['data'][i]['price_data']['data']['prices']['updated_at']}", inline=False)
                                            if i == len(data2['data'])-1:
                                                embed2.set_image(url= "https://static.wikia.nocookie.net/p__/images/2/2f/Winged-Kuriboh.png/revision/latest?cb=20161213005825&path-prefix=protagonist")
                                                embed2.set_thumbnail(url="https://i.gifer.com/origin/e0/e02ce86bcfd6d1d6c2f775afb3ec8c01_w200.gif")
                                                embeds.append(embed2)
                                                embed2 = discord.Embed(
                                                    title="Card Sets",
                                                    color=0x1abc9c
                                                )
                                        if data2['data'][i]['price_data']['status'] == "fail":
                                            embed2.add_field(name=data2['data'][i]['name'], value=f"{data2['data'][i]['print_tag']}\n{data2['data'][i]['rarity']}\n **{data2['data'][i]['price_data']['message']}** 🥹", inline=False)
                                            if i == len(data2['data'])-1:
                                                embed2.set_image(url= "https://static.wikia.nocookie.net/p__/images/2/2f/Winged-Kuriboh.png/revision/latest?cb=20161213005825&path-prefix=protagonist")
                                                embed2.set_thumbnail(url="https://i.gifer.com/origin/e0/e02ce86bcfd6d1d6c2f775afb3ec8c01_w200.gif")
                                                embeds.append(embed2)
                                                embed2 = discord.Embed(
                                                    title="Card Sets",
                                                    color=0x1abc9c
                                                )
                                    else:
                                        if data2['data'][i]['price_data']['status'] == "success":
                                                embed2.add_field(name=data2['data'][i]['name'], value=f"{data2['data'][i]['print_tag']}\n{data2['data'][i]['rarity']}\n**Lowest: **US${data2['data'][i]['price_data']['data']['prices']['low']} | C${str(clow)}**\nHighest: **US${data2['data'][i]['price_data']['data']['prices']['high']} | C${str(chigh)}\n**Average**: US${data2['data'][i]['price_data']['data']['prices']['average']} | C${str(cavg)}\nLast updated on {data2['data'][i]['price_data']['data']['prices']['updated_at']}", inline=False)
                                        
                                        if data2['data'][i]['price_data']['status'] == "fail":
                                            embed2.add_field(name=data2['data'][i]['name'], value=f"{data2['data'][i]['print_tag']}\n{data2['data'][i]['rarity']}\n **{data2['data'][i]['price_data']['message']}** 🥹", inline=False)

                                        embed2.set_image(url= "https://static.wikia.nocookie.net/p__/images/2/2f/Winged-Kuriboh.png/revision/latest?cb=20161213005825&path-prefix=protagonist")
                                        embed2.set_thumbnail(url="https://i.gifer.com/origin/e0/e02ce86bcfd6d1d6c2f775afb3ec8c01_w200.gif")
                                        embeds.append(embed2)
                                        embed2 = discord.Embed(
                                            title="Card Sets",
                                            color=0x1abc9c
                                        )


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
                else:
                        await ctx.send(embed=embed)

                    
async def setup(client):
    await client.add_cog(Yugioh(client))
