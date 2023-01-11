import random
import discord
from discord.ext import commands
from discord import app_commands
from economy_utils import economy_dboperations

class Economy(commands.Cog, description="Economy commands."):

    def __init__(self, client: commands.Bot):
        self.client = client
        self.starting_money = 500
        self.displayed_currency = "$"
        self.connection = economy_dboperations.connection()

    def economy_embed(self, ctx: commands.Context) -> discord.Embed:
        embed = discord.Embed(title="Zen | Economy", color=ctx.author.color)
        return embed

    def db_exception_embed(self, ctx: commands.Context, operation):
        if isinstance(operation, Exception):
            embed = self.economy_embed(ctx)
            embed.description = "You already have an account!" if str(operation) == "UNIQUE constraint failed: members.userid" else str(operation).capitalize()
            return embed
            
    async def cog_command_error(self, ctx: commands.Context, error: str):
        embed = self.economy_embed(ctx)
        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = str(error).capitalize()
            return await ctx.send(embed=embed)
        if isinstance(error, commands.MemberNotFound):
            embed.description = str(error).capitalize()
            return await ctx.send(embed=embed)
        if isinstance(error, commands.BadArgument):
            embed.description = str(error).capitalize()
            return await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Economy module has been loaded.")
        economy_dboperations.create_tables(self.connection)

    @commands.command(aliases=["bal", "money", "networth"])
    async def balance(self, ctx: commands.Context, member: discord.Member = None):
        embed = self.economy_embed(ctx)
        if member is None:
            if economy_dboperations.check_member_exists(self.connection, ctx.author):
                money = economy_dboperations.get_member_money(self.connection, ctx.author)
                embed.description = f"You currently have **{money}**{self.displayed_currency}"
                return await ctx.send(embed=self.db_exception_embed(ctx, money)) if self.db_exception_embed(ctx, money) else await ctx.send(embed=embed)
            embed.description = f"{ctx.author.mention} doesn't have an account!\nType {self.client.command_prefix}createaccount to create an account."
            return await ctx.send(embed=embed)
        else:
            if economy_dboperations.check_member_exists(self.connection, member):
                money = economy_dboperations.get_member_money(self.connection, member)
                embed.description = f"{member.mention} has **{money}**{self.displayed_currency}"
                return await ctx.send(embed=self.db_exception_embed(ctx, money)) if self.db_exception_embed(ctx, money) else await ctx.send(embed=embed)
            embed.description = f"{member.mention} doesn't have an account!\nType {self.client.command_prefix}createaccount to create an account."
            return await ctx.send(embed=embed)

    @commands.command()
    async def addmoney(self, ctx: commands.Context, amount: int, member: discord.Member = None):
        embed = self.economy_embed(ctx)
        if amount < 0:
            embed.description = "The amount has to be positive!"
            return await ctx.send(embed=embed)
        if member is None:
            if economy_dboperations.check_member_exists(self.connection, ctx.author):
                money = economy_dboperations.add_member_money(self.connection, ctx.author, amount)
                embed.description = f"Added **{amount}**{self.displayed_currency} to {ctx.author.mention}'s account!"
                return await ctx.send(embed=self.db_exception_embed(ctx, money)) if self.db_exception_embed(ctx, money) else await ctx.send(embed=embed)
            embed.description = f"{ctx.author.mention} doesn't have an account!\nType {self.client.command_prefix}createaccount to create an account."
            return await ctx.send(embed=embed)
        else:
            if economy_dboperations.check_member_exists(self.connection, member):
                money = economy_dboperations.add_member_money(self.connection, member, amount)
                embed.description = f"Added **{amount}**{self.displayed_currency} to {member.mention}'s account!"
                return await ctx.send(embed=self.db_exception_embed(ctx, money)) if self.db_exception_embed(ctx, money) else await ctx.send(embed=embed)
            embed.description = f"{member.mention} doesn't have an account!\nType {self.client.command_prefix}createaccount to create an account."
            return await ctx.send(embed=embed)

    @commands.command()
    async def removemoney(self, ctx: commands.Context, amount: int, member: discord.Member = None):
        embed = self.economy_embed(ctx)
        if amount < 0:
            embed.description = "The amount has to be positive!"
            return await ctx.send(embed=embed)
        if member is None:
            if economy_dboperations.check_member_exists(self.connection, ctx.author):
                networth = economy_dboperations.get_member_money(self.connection, ctx.author)
                if amount > networth:
                    amount = networth
                money = economy_dboperations.add_member_money(self.connection, ctx.author, -amount)
                embed.description = f"Removed **{amount}**{self.displayed_currency} from {ctx.author.mention}'s account!"
                return await ctx.send(embed=self.db_exception_embed(ctx, money)) if self.db_exception_embed(ctx, money) else await ctx.send(embed=embed)
            embed.description = f"{ctx.author.mention} doesn't have an account!\nType {self.client.command_prefix}createaccount to create an account."
            return await ctx.send(embed=embed)
        else:
            if economy_dboperations.check_member_exists(self.connection, member):
                networth = economy_dboperations.get_member_money(self.connection, ctx.author)
                if amount > networth:
                    amount = networth
                money = economy_dboperations.add_member_money(self.connection, member, -amount)
                embed.description = f"Removed **{amount}**{self.displayed_currency} from {member.mention}'s account!"
                return await ctx.send(embed=self.db_exception_embed(ctx, money)) if self.db_exception_embed(ctx, money) else await ctx.send(embed=embed)
            embed.description = f"{member.mention} doesn't have an account!\nType {self.client.command_prefix}createaccount to create an account."
            return await ctx.send(embed=embed)

    @commands.command()
    async def work(self, ctx: commands.Context):
        embed = self.economy_embed(ctx)
        if economy_dboperations.check_member_exists(self.connection, ctx.author):
            rank = economy_dboperations.get_member_rank(self.connection, ctx.author)
            minmax = economy_dboperations.get_rank_minmax_salary(self.connection, rank)
            salary = random.randint(minmax[0], minmax[1])
            operation = economy_dboperations.add_member_money(self.connection, ctx.author, salary)
            embed.description = f"You worked hard today and earned **{salary}**{self.displayed_currency} as {rank.capitalize()}!"
            return await ctx.send(embed=self.db_exception_embed(ctx, operation)) if self.db_exception_embed(ctx, operation) else await ctx.send(embed=embed)
        embed.description = embed.description = f"{ctx.author.mention} doesn't have an account!\nType {self.client.command_prefix}createaccount to create an account."
        return await ctx.send(embed=embed)

    @commands.command()
    async def createaccount(self, ctx: commands.Context):
        embed = self.economy_embed(ctx)
        rank = economy_dboperations.get_rank_with_position(self.connection, 1)
        if not rank:
            embed.description = "A staff member needs to set up the default rank before members can create an account."
            return await ctx.send(embed=embed)
        operation = economy_dboperations.create_member(self.connection, ctx.author.id, ctx.author.name, self.starting_money, rank[0][1])
        embed.description = f"Account created with **{self.starting_money}**{self.displayed_currency}, starting as {rank[0][1].capitalize()}."
        return await ctx.send(embed=self.db_exception_embed(ctx, operation)) if self.db_exception_embed(ctx, operation) else await ctx.send(embed=embed)

    @commands.command()
    async def deleteaccount(self, ctx: commands.Context):
        embed = self.economy_embed(ctx)
        operation = economy_dboperations.delete_member(self.connection, ctx.author.id)
        embed.description = "Your account has been succesfully deleted!"
        return await ctx.send(embed=self.db_exception_embed(ctx, operation)) if self.db_exception_embed(ctx, operation) else await ctx.send(embed=embed)

    @commands.command()
    async def createrank(self, ctx: commands.Context, rank: str, minsalary: int, maxsalary: int, required: int = 0, position: int = 1):
        embed = self.economy_embed(ctx)
        operation = economy_dboperations.create_rank(self.connection, rank.lower(), minsalary, maxsalary, required, position)
        embed.description = f"Created {rank.capitalize()} with a minimum daily salary of {minsalary}{self.displayed_currency} and a maximum daily salary of {maxsalary}{self.displayed_currency}."
        return await ctx.send(embed=self.db_exception_embed(ctx, operation)) if self.db_exception_embed(ctx, operation) else await ctx.send(embed=embed)

    # @commands.command()
    # async def modifyrank(self, ctx: commands.Context, position: int = 1):
    #     embed = self.economy_embed(ctx)

    @commands.command()
    async def deleterank(self, ctx: commands.Context, rank):
        embed = self.economy_embed(ctx)
        default_rank = economy_dboperations.get_default_rank(self.connection)[0][1]
        if rank == default_rank:
            embed.description = f"You cannot delete the default rank!\nUse {self.client.command_prefix}modifyrank to modify the default rank"
            return await ctx.send(embed=embed)
        operation = economy_dboperations.delete_rank(self.connection, rank.lower())
        embed.description = f"You have successfully deleted {rank.capitalize()}!"
        return await ctx.send(embed=self.db_exception_embed(ctx, operation)) if self.db_exception_embed(ctx, operation) else await ctx.send(embed=embed)

    @commands.command()
    async def startingmoney(self, ctx: commands.Context, money: int = None):
        embed = self.economy_embed(ctx)
        if money is None:
            embed.description = f"The starting money is currently **{self.starting_money}**{self.displayed_currency}"
        else:
            self.starting_money = money
            embed.description = f"Successfully changed starting money to **{money}**{self.displayed_currency}"
        await ctx.send(embed=embed)

    @commands.command()
    async def currency(self, ctx: commands.Context, currency = None):
        embed = self.economy_embed(ctx)
        if currency is None:
            embed.description = f"The current currency is {self.displayed_currency}"
        else:
            self.displayed_currency = currency
            embed.description = f"Successfully changed the currency to {currency}!"
        await ctx.send(embed=embed)

    @commands.command()
    async def profile(self, ctx: commands.Context, member: discord.Member = None):
        embed = self.economy_embed(ctx)
        if member is None:
            if economy_dboperations.check_member_exists(self.connection, ctx.author):
                member_data = economy_dboperations.get_member(self.connection, ctx.author)[0]
                embed.set_thumbnail(url=ctx.author.avatar)
                embed.add_field(name="Account Name", value=f"**{member_data[2]}**", inline=False)
                embed.add_field(name="Net Worth", value=f"**{member_data[3]}**{self.displayed_currency}", inline=False)
                embed.add_field(name="Rank", value=f"**{member_data[4].capitalize()}**", inline=False)

                return await ctx.send(embed=self.db_exception_embed(ctx, member_data)) if self.db_exception_embed(ctx, member_data) else await ctx.send(embed=embed)
            embed.description = embed.description = f"{ctx.author.mention} doesn't have an account!\nType {self.client.command_prefix}createaccount to create an account."
            return await ctx.send(embed=embed)
        else:
            if economy_dboperations.check_member_exists(self.connection, member):
                member_data = economy_dboperations.get_member(self.connection, member)[0]
                embed.set_thumbnail(url=member.avatar)
                embed.add_field(name="Account Name", value=f"**{member_data[2]}**", inline=False)
                embed.add_field(name="Net Worth", value=f"**{member_data[3]}**{self.displayed_currency}", inline=False)
                embed.add_field(name="Rank", value=f"**{member_data[4].capitalize()}**", inline=False)

                return await ctx.send(embed=self.db_exception_embed(ctx, member_data)) if self.db_exception_embed(ctx, member_data) else await ctx.send(embed=embed)
            embed.description = embed.description = f"{member.mention} doesn't have an account!\nType {self.client.command_prefix}createaccount to create an account."
            return await ctx.send(embed=embed)

    @commands.command()
    async def leaderboard(self, ctx: commands.Context):
        embed = self.economy_embed(ctx)
        embed.description = ""
        members_data = economy_dboperations.get_leaderboard(self.connection)
        print(members_data)
        for index, member in enumerate(members_data):
            embed.description += f"{index + 1}. <@{member[1]}> - **{member[3]}**{self.displayed_currency}\n"
        
        await ctx.send(embed=embed)
async def setup(client):
    await client.add_cog(Economy(client))