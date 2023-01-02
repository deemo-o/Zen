import datetime
from random import randint
import discord
from datetime import date, datetime
from discord.ext import commands
from discord import app_commands
import aiohttp
import typing
import os
from dotenv import load_dotenv
 
class General(commands.Cog, description="Simple commands."):
    
    def __init__(self, client: commands.Bot):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("General module has been loaded.")
    
    @commands.command()
    async def me(self, ctx: commands.Context):
        phrases = [f"A little about {ctx.author.name}.", f"Some information about {ctx.author.name}.", f"{ctx.author.name}'s secret information."]

        embed = discord.Embed(title=f"{ctx.author.name}", color=ctx.author.color, timestamp=datetime.now())
        embed.description = f"{phrases[randint(0, len(phrases) - 1)]}"
        embed.set_thumbnail(url=ctx.author.avatar)
        embed.add_field(name='Joined Discord', value=ctx.author.created_at.date(), inline=True)
        embed.add_field(name='Joined Server', value=ctx.author.joined_at.date(), inline=True)
        for role in ctx.author.roles:
            if role.name in ["Abbot", "Prior", "Dev", "Roundsman"]:
                embed.add_field(name="Rank", value=f"Staff <@&{ctx.author.top_role.id}>", inline=False)
                break
            elif role.name == "Monk":
                embed.add_field(name="Rank", value=f"Special Member <@&{ctx.author.top_role.id}>", inline=False)
                break
            elif role.name == "Meditator":
                embed.add_field(name="Rank", value=f"Member <@&{ctx.author.top_role.id}>", inline=False)
                break
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url="https://cdn-icons-png.flaticon.com/512/1593/1593591.png")

        await ctx.send(embed=embed)

    @commands.command()
    async def whois(self, ctx: commands.Context, member: discord.Member):
        phrases = [f"A little about {member.name}.", f"Some information about {member.name}.", f"{member.name}'s secret information."]

        embed = discord.Embed(title=f"{member.name}", color=ctx.author.color, timestamp=datetime.now())
        embed.description = f"{phrases[randint(0, len(phrases) - 1)]}"
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name='Joined Discord', value=member.created_at.date(), inline=True)
        embed.add_field(name='Joined Server', value=member.joined_at.date(), inline=True)
        for role in member.roles:
            if role.name in ["Abbot", "Prior", "Dev", "Roundsman"]:
                embed.add_field(name="Rank", value=f"Staff <@&{member.top_role.id}>", inline=False)
                break
            elif role.name == "Monk":
                embed.add_field(name="Rank", value=f"Special Member <@&{member.top_role.id}>", inline=False)
                break
            elif role.name =="Bot":
                embed.add_field(name="Rank", value=f"Bot <@&{member.top_role.id}>", inline=False)
                break
            elif role.name == "Meditator":
                embed.add_field(name="Rank", value=f"Member <@&{member.top_role.id}>", inline=False)
                break
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url="https://cdn-icons-png.flaticon.com/512/1593/1593591.png")

        await ctx.send(embed=embed)

    @commands.command(brief='Information about the server.', description='This command will display some information about the current server.')
    async def about(self, ctx: commands.Context):
        serverdesc = ctx.guild.description
        if serverdesc is None:
            serverdesc = 'This server did not enable community or does not have a description.'
        embed = discord.Embed(title=f'About {ctx.guild.name}', description="The best server in the west!", color=ctx.author.top_role.color, timestamp=datetime.now())
        embed.set_author(name=f'{ctx.guild.name}', icon_url=ctx.guild.icon)
        embed.add_field(name='Description', value=serverdesc, inline=False)
        embed.add_field(name='Created at', value=ctx.guild.created_at.date(), inline=False)
        embed.add_field(name='Members', value=ctx.guild.member_count, inline=False)
        embed.add_field(name='Created by', value=ctx.guild.owner.mention, inline=False)

        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url="https://cdn-icons-png.flaticon.com/512/1593/1593591.png")

        await ctx.send(embed=embed)
    
    @commands.command(brief= 'Current weather information.', description = 'Get the current weather information for any city (Defaulted to Monreal).')
    async def weather(self, ctx: commands.Context, city: typing.Optional[str] = "Montreal"):
        load_dotenv()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={os.getenv('WEATHER_API_KEY')}&units=metric") as resp:
                    print(resp.status)
                    data = await resp.json()
                    cityName = data['name']
        except: 
            return await ctx.send("Make sure you wrote the city name correctly.")
        tempInC = round(data['main']['temp'])
        tempInF = round(tempInC * 1.8 + 32) 
        feelsLikeInC = round(data['main']['feels_like'])
        feelsLikeInF = round(feelsLikeInC * 1.8 + 32)
        weatherDesc = data['weather'][0]['description'].title()
        weatherIcon = data['weather'][0]['icon']
        humidity = data['main']['humidity']
        windSpeed = round(data['wind']['speed'] * 3.6)
        windSpeedImp = round(windSpeed / 1.609)
        embed = discord.Embed(title=f'Current Weather in {cityName}:', color=ctx.author.top_role.color)
        embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{weatherIcon}@2x.png")
        embed.add_field(name='Current Temp', value=f"{tempInC} \N{DEGREE SIGN}C | {tempInF}\N{DEGREE SIGN}F", inline=True)
        embed.add_field(name='Feels Like', value=f"{feelsLikeInC}\N{DEGREE SIGN}C | {feelsLikeInF}\N{DEGREE SIGN}F", inline=True)
        embed.add_field(name=chr(173), value=chr(173), inline=True)
        embed.add_field(name='Description', value=f"{weatherDesc}", inline=True)
        embed.add_field(name='Humidity', value=f"{humidity}%", inline=True)
        embed.add_field(name='Wind Speed', value=f"{windSpeed} km/h | {windSpeedImp} m/h", inline=True)
        embed.timestamp = datetime.now()
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar)
        await ctx.send(embed=embed) 
async def setup(client):
    await client.add_cog(General(client))