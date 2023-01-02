import discord
from discord.ext import commands
from discord import app_commands
from database_utils import economy_database

class Economy(commands.Cog, description="Economy commands."):
    
    def __init__(self, client: commands.Bot):
        self.client = client
        try:
            self.connection = economy_database.connect()
            print("Connected to database")
        except:
            print("Couldn't connect to database")
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Economy module has been loaded.")
        try:
            economy_database.create_table(self.connection)
            print("Table created")
        except:
            print("Something went wrong!")

    @commands.command()
    async def balance(self, ctx: commands.Context):
        try:
            data = economy_database.get_member(self.connection, ctx.author.id)
            await ctx.send(f"You currently have {data[0][3]}$")
            print(data)
        except Exception as e:
            print(e)

    @commands.command()
    async def addmoney(self, ctx: commands.Context, amount: int):
        try:
            economy_database.update_member(self.connection, ctx.author.id, amount)
            await ctx.send(f"Added {amount} to {ctx.author.name}'s account!")
        except Exception as e:
            print(e)

    @commands.command()
    async def createaccount(self, ctx: commands.Context):
        try:
            economy_database.add_member(self.connection, ctx.author.id, ctx.author.name, 500)
            await ctx.send("Account created with 500$")
        except Exception as e:
            print(e)
            if str(e) == "UNIQUE constraint failed: members.userid":
                return await ctx.send("You already have an account!")
            else:
                return await ctx.send("There is an issue right now, sorry!")

async def setup(client):
    await client.add_cog(Economy(client))