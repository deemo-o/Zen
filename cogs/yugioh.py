import json
import discord
import aiohttp
import Paginator
from discord.ext import commands
from discord import app_commands
 
class Yugioh(commands.Cog, description="Yugioh commands."):
    
    def __init__(self, client: commands.Bot):
        self.client = client
        
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
                print(response)
                if response.status == 200:
                    data = await response.json()
        
                    #NOTES:
                    #1 - WE CAN GET BLACKLISTED IF WE CALL TOO MANY IMAGES
                    #2 - EMBED.SET_IMAGE(), ONLY SETS URLS, LEADING TO AN INEVITABLE BLACKLISTING
                
                    #SOLUTION:
                    #3 - WE CAN CREATE OUR OWN API AND INSERT DIRECTLY IN OUR DATABASE
                    #4 - DOING SO WILL ALLOW US TO DISPLAY BLOB DATA ENTRIES UNDER AN URL
                    #5 - ALSO WE'LL BE ABLE TO AVOID BEING BLACKLISTED

                    #ADDITIONAL INFORMATION:
                    #6 - DISPLAYING THE YUGIOH CARD WILL FILL OUT ALL THE NECESSARY FIELDS.
                    #7 - WE MAY CONSIDER KEEPING THE YUGIOH CARD OR ONLY THE NON-GRAPHICAL PROPERTIES. TO REDUCE THE WEIGHT OF OUR DATABASE.
                


                    # UNDER CONSTRUCTION !!!!!!!!!!

                    # print(data.data.id)
                    lvl, xyzlvl = '<:level:1059718470448730192>', '<:blacklevel:1059725946258739231>'
                    
                    continuous, field, equip, counter, ritual, quick_play = '<:continuous:1060059486091489300>','<:field:1060061606727385128>', '<:equip:1060060942609690747>'\
                                                                            ,'<:counter:1060060902570856559>', '<:ritual:1060061076957450341>','<:quick_play:1060061028022485052>'
                    
                    aqua, beast, beast_warrior, dinosaur, divine_beast, dragon, fairy, fiend,\
                    fish, insect, machine, plant, psychic, pyro, reptile, rock, sea_serpent,\
                    spellcaster, thunder, warrior, winged_beast, wyrm, zombie = \
                    "<:aqua:1060056550191939616>",\
                    "<:beast:1060056513189781514>", "<:beast_warrior:1060056473096433685>",\
                    "<:dinosaur:1060056438476636251>", "<:divine_beast:1060056388920934510>",\
                    "<:dragon:1060056349167329300>", "<:fairy:1060056312827879474>",\
                    "<:fiend:1060056266061398097>", "<:fish:1060056223791206451>",\
                    "<:insect:1060056164118827149>", "<:machine:1060056124499427358>",\
                    "<:plant:1060056072917876856>", "<:psychic:1060056019637653594>",\
                    "<:pyro:1060055977510055936>", "<:reptile:1060055927178403901>",\
                    "<:rock:1060055879971524658>", "<:sea_serpent:1060055774744817725>",\
                    "<:spellcaster:1060055685276123266>", "<:thunder:1060055623640817724>",\
                    "<:warrior:1060055520381247588>", "<:winged_beast:1060055427540324372>",\
                    "<:wyrm:1060055319927078954>", "<:zombie:1060055023058419722>"

                    dark, divine, earth, fire, light, water, wind, spell, trap = \
                        "<:dark:1060047681545830530>", "<:divine:1060048064750047323>",\
                        "<:earth:1060048304316104744>", "<:fire:1060048511099482112>",\
                        "<:light:1060045885070913556>", "<:water:1060049005108797512>",\
                        "<:wind:1060049169894625310>", "<:spell:1060048999765250068>",\
                        "<:trap:1060049002466381834>"

                    ricon, attricon = [], []
                    race = data['data'][0]['race']
                    
                    if race == "Aqua":
                        ricon.append(aqua)
                    elif race == "Beast":
                        ricon.append(beast)
                    elif race == "Beast-Warrior":
                        ricon.append(beast_warrior)
                    elif race == "Dinosaur":
                        ricon.append(dinosaur)
                    elif race == "Divine-Beast":
                        ricon.append(divine_beast)
                    elif race == "Dragon":
                        ricon.append(dragon)
                    elif race == "Fairy":
                        ricon.append(fairy)
                    elif race == "Fiend":
                        ricon.append(fiend)
                    elif race == "Fish":
                        ricon.append(fish)
                    elif race == "Insect":
                        ricon.append(insect)
                    elif race == "Machine":
                        ricon.append(machine)
                    elif race == "Plant":
                        ricon.append(plant)
                    elif race == "Psychic":
                        ricon.append(psychic)
                    elif race == "Pyro":
                        ricon.append(pyro)
                    elif race == "Reptile":
                        ricon.append(reptile)
                    elif race == "Rock":
                        ricon.append(rock)
                    elif race == "Sea Serpent":
                        ricon.append(sea_serpent)
                    elif race == "Spellcaster":
                        ricon.append(spellcaster)
                    elif race == "Thunder":
                        ricon.append(thunder)
                    elif race == "Warrior":
                        ricon.append(warrior)
                    elif race == "Winged Beast":
                        ricon.append(winged_beast)
                    elif race == "Wyrm":
                        ricon.append(wyrm)
                    elif race == "Zombie":
                        ricon.append(zombie)
                    elif race == "Continuous":
                        ricon.append(continuous)
                    elif race == "Field":
                        ricon.append(field)
                    elif race == "Equip":
                        ricon.append(equip)
                    elif race == "Counter":
                        ricon.append(counter)
                    elif race == "Ritual":
                        ricon.append(ritual)
                    elif race == "Quick Play":
                        ricon.append(quick_play)
                    elif race == "Normal":
                        ricon.append("")
                    

                    #https://db.ygoprodeck.com/api/v7/cardinfo.php?name=Blacking+-+Zephyros+the+elite
                    #https://db.ygoprodeck.com/api/v7/cardinfo.php?name=Blackwing%20-%20Zephyros%20the%20Elite
                    if "Monster" in data['data'][0]['type']:
                        print("hello", data['data'][0]['type'])
                        att = data['data'][0]['attribute']
                        if att == "DARK":
                            attricon.append(dark)
                        elif att == "DIVINE":
                            attricon.append(divine)
                        elif att == "FIRE":
                            attricon.append(fire)
                        elif att == "LIGHT":
                            attricon.append(light)
                        elif att == "EARTH":
                            attricon.append(earth)
                        elif att == "WIND":
                            attricon.append(wind)
                        elif att == "WATER":
                            attricon.append(water)

                        if data['data'][0]['type'] != "Normal Monster":
                            mstype = "/Effect"
                            if data["data"][0]["type"] == "Link Monster":
                                lvl = "RANK " + data['data'][0]['level']
                            elif data["data"][0]["type"] == "XYZ Monster":
                                lvl = xyzlvl  

                            embed = discord.Embed(
                            color=0x1abc9c,
                            title=f"**{data['data'][0]['name']}**",
                            description=f"**Type**: {ricon[0]} {data['data'][0]['race']}/{data['data'][0]['type']}{mstype}\n**Attribute**: {attricon[0]} {data['data'][0]['attribute']}\n**Level**: {lvl} {int(data['data'][0]['level'])} **ATK**: {data['data'][0]['atk']} **DEF**: {data['data'][0]['def']}")
                    
                            embed.insert_field_at(index=1,name="Description", value=f"{data['data'][0]['desc']}",inline=False)
                            embed.set_thumbnail(url=data['data'][0]['card_images'][0]['image_url_croppped'])

                    elif data['data'][0]['type'] == "Trap Card":
                        embed = discord.Embed(
                        color=0x1abc9c,
                        title=f"**{data['data'][0]['name']}**",
                        description=f"**Type**: {trap} {data['data'][0]['type']} {ricon[0]} \n")
                
                        embed.insert_field_at(index=1,name="Description", value=f"{data['data'][0]['desc']}",inline=False)
                        embed.set_thumbnail(url=data['data'][0]['card_images'][0]['image_url_croppped'])

                    elif data['data'][0]['type'] == "Spell Card":
                        embed = discord.Embed(
                        color=0x1abc9c,
                        title=f"**{data['data'][0]['name']}**",
                        description=f"**Type**: {spell} {data['data'][0]['type']} {ricon[0]} \n")
                
                        embed.insert_field_at(index=1,name="Description", value=f"{data['data'][0]['desc']}",inline=False)
                        embed.set_thumbnail(url=data['data'][0]['card_images'][0]['image_url_croppped'])
                    else:
                        mstype = "/Normal"

                    embed2 = discord.Embed(
                        title="Card Sets"
                    )
                    for i in range(len(data['data'][0]['card_sets'])):
                        embed2.add_field(name=data['data'][0]['card_sets'][i]['set_name'], value=f"{data['data'][0]['card_sets'][i]['set_code']}\n{data['data'][0]['card_sets'][i]['set_rarity']}\n**${data['data'][0]['card_sets'][i]['set_price']}**", inline=False)
                    
                    embed3 = discord.Embed(
                        title="Card Prices",
                        description=f"Card Market: **${data['data'][0]['card_prices'][0]['cardmarket_price']}**\n TCGPlayer: **${data['data'][0]['card_prices'][0]['tcgplayer_price']}**\n Ebay: **${data['data'][0]['card_prices'][0]['ebay_price']}**\n Amazon: **${data['data'][0]['card_prices'][0]['amazon_price']}**\n Cool Stuff Inc **${data['data'][0]['card_prices'][0]['coolstuffinc_price']}**")
                    embed3.set_image(url= "https://static.wikia.nocookie.net/p__/images/2/2f/Winged-Kuriboh.png/revision/latest?cb=20161213005825&path-prefix=protagonist")
                    embed3.set_thumbnail(url="https://i.gifer.com/origin/e0/e02ce86bcfd6d1d6c2f775afb3ec8c01_w200.gif")
                    embeds = [embed,embed2,embed3,]
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
                    await ctx.send(embed=embeds)

async def setup(client):
    await client.add_cog(Yugioh(client))
