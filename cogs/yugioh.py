import json
import discord
import aiohttp
from discord.ext import commands
from discord import app_commands
 
class Yugioh(commands.Cog, description="Yugioh commands."):
    
    def __init__(self, client: commands.Bot):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Yugioh module has been loaded.")

    @commands.command(aliases=["scn"], brief="Searches a card by name.", description="A command that helps you search a Yugioh card.")
    async def searchcard(self, ctx: commands.Context):
        # async with aiohttp.ClientSession() as session: 
        #     async with session.get(f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={card}") as response:
        #         if response.status == 200:
        #             data = await response.json()
        #             embed = discord.Embed(title="")
        
        #YGOPRO DUMMY DATA PULLED FROM API GET REQUEST
        data = {"data": [
        {
        "id": 6983839,
        "name": "Tornado Dragon",
        "type": "XYZ Monster",
        "desc": "2 Level 4 monsters\nOnce per turn (Quick Effect): You can detach 1 material from this card, then target 1 Spell/Trap on the field; destroy it.",
        "atk": 2100,
        "def": 2000,
        "level": 4,
        "race": "Wyrm",
        "attribute": "WIND",
        "card_sets": [
        {
        "set_name": "Battles of Legend: Relentless Revenge",
        "set_code": "BLRR-EN084",
        "set_rarity": "Secret Rare",
        "set_rarity_code": "(ScR)",
        "set_price": "4.65"
        },
        {
        "set_name": "Duel Devastator",
        "set_code": "DUDE-EN019",
        "set_rarity": "Ultra Rare",
        "set_rarity_code": "(UR)",
        "set_price": "1.58"
        },
        {
        "set_name": "Legendary Duelists: Synchro Storm",
        "set_code": "LED8-EN055",
        "set_rarity": "Common",
        "set_rarity_code": "(C)",
        "set_price": "0.96"
        },
        {
        "set_name": "Maximum Crisis",
        "set_code": "MACR-EN081",
        "set_rarity": "Secret Rare",
        "set_rarity_code": "(ScR)",
        "set_price": "4.49"
        }
        ],
        "card_images": [
        {
        "id": 6983839,
        "image_url": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fabout.google%2Fproducts%2F&psig=AOvVaw3h69hLWApofuwgBN53SmWp&ust=1672714747216000&source=images&cd=vfe&ved=0CBAQjRxqFwoTCPC4pJTyp_wCFQAAAAAdAAAAABAX",
        "image_url_small": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fabout.google%2Fproducts%2F&psig=AOvVaw3h69hLWApofuwgBN53SmWp&ust=1672714747216000&source=images&cd=vfe&ved=0CBAQjRxqFwoTCPC4pJTyp_wCFQAAAAAdAAAAABAX",
        "image_url_croppped": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fabout.google%2Fproducts%2F&psig=AOvVaw3h69hLWApofuwgBN53SmWp&ust=1672714747216000&source=images&cd=vfe&ved=0CBAQjRxqFwoTCPC4pJTyp_wCFQAAAAAdAAAAABAX"
        }
        ],
        "card_prices": [
        {
        "cardmarket_price": "0.18",
        "tcgplayer_price": "0.19",
        "ebay_price": "1.90",
        "amazon_price": "1.39",
        "coolstuffinc_price": "0.79"
        }
        ]
        }
        ]}

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
        print(data['data'])
        embed = discord.Embed(
            # title=f"{data['data'][0]['name']}, level {data['data'][0]['level']}",
            # description=data['data'][0]['desc']
        )
        embed.set_image(url="https://product-images.tcgplayer.com/fit-in/874x874/131198.jpg")
        # embed.set_thumbnail(url="https://product-images.tcgplayer.com/fit-in/874x874/131198.jpg")
        # nio f"{data['data'][0]['type']}|{data['data'][0]['race']}|{data['data'][0]['attribute']}",
        # embed.insert_field_at(index=1,name="attack",value=data['data'][0]['atk'],inline=False)
        # embed.insert_field_at(index=0,name="defense",value=data['data'][0]['def'],inline=False)
        await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(Yugioh(client))