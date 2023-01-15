import asyncio
import random
import time
import discord
from discord.ext import commands, tasks
from discord import app_commands
from utils.economy_utils import economy_dboperations

class Economy(commands.Cog, description="Economy commands."):

    def __init__(self, client: commands.Bot):
        self.client = client
        self.starting_money = 500
        self.displayed_currency = "$"
        self.connection = economy_dboperations.connection()
        self.gift_question.start()

    def cog_unload(self):
        self.gift_question.cancel()

    def get_random_seconds(self) -> int:
        return random.randint(300, 600) # Currently set between 5-10 minutes

    def simple_math_addition(self):
        a = random.randint(1, 999)
        b = random.randint(1, 999)
        c = a + b
        d = "+"
        e = random.randint(450, 750)
        return a, b, c, d, e

    def simple_math_subtraction(self):
        a = random.randint(1, 999)
        b = random.randint(1, 999)
        while b > a:
            b = random.randint(1, 999)
        c = a - b
        d = "-"
        e = random.randint(500, 800)
        return a, b, c, d, e

    def simple_math_multiplication(self):
        a = random.randint(1, 99)
        b = random.randint(1, 99)
        c = a * b
        d = "*"
        e = random.randint(650, 950)
        return a, b, c, d, e

    def convert(self, seconds):
        return time.strftime("**%Mm%Ss**", time.gmtime(seconds))

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
        if isinstance(error, Exception):
            if isinstance(error, commands.CommandOnCooldown):
                return
            embed.description = str(error).capitalize()
            return await ctx.send(embed=embed)

    @tasks.loop(seconds=60)
    async def gift_question(self):
        await asyncio.sleep(self.get_random_seconds())
        embed = discord.Embed(title="Zen | Gift Question", color=discord.Color.from_rgb(248, 175, 175))
        questions = [self.simple_math_addition(), self.simple_math_subtraction(), self.simple_math_multiplication()]
        question = random.choices(questions)
        embed.description = f"What is the answer to this question?:\n\n{question[0][0]} {question[0][3]} {question[0][1]} = ?\n\nYou need to have an account to participate.\nType {self.client.command_prefix}createaccount if you don't already have one."
        guilds = economy_dboperations.get_all_guilds(self.connection)
        channels = []
        for guild in guilds:
            giftchannels = economy_dboperations.get_all_giftchannels(self.connection, guild[1])
            for channel in giftchannels:
                channels.append(await self.client.fetch_channel(channel[1]))
        for channel in channels:
            await channel.send(embed=embed, delete_after=60)
        try:
            answer = await self.client.wait_for("message", check=lambda x: x.content == f"{question[0][2]}" and economy_dboperations.get_member(self.connection, x.author) != [], timeout=60.0)
            money = economy_dboperations.add_member_money(self.connection, answer.author, question[0][4])
            embed.description = f"{answer.author.mention} got the right answer and won **{question[0][4]}{self.displayed_currency}**!\n\n{money}"
            for channel in channels:
                await channel.send(embed=embed, delete_after=60)
        except asyncio.TimeoutError:
            embed.description = "No one answered. Better luck next time!"
            for channel in channels:
                await channel.send(embed=embed, delete_after=60)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Economy module has been loaded.")
        economy_dboperations.create_tables(self.connection)
        economy_dboperations.create_guilds_table(self.connection)
        for guild in self.client.guilds:
            economy_dboperations.add_guild(self.connection, guild.id, guild.name)
            economy_dboperations.create_giftchannels_table(self.connection, guild.id)

    @commands.command(aliases=["togglegq", "tgq"], brief="Toggle gift questions in subscribed channels.", description="This command will enable/disable the gift questions in the channels that are subscribed.")
    async def togglegiftquestion(self, ctx: commands.Context):
        embed = self.economy_embed(ctx)
        if not self.gift_question.is_running():
            self.gift_question.start()
            embed.description = f"Enabled gift questions for subscribed channels."
            await ctx.send(embed=embed)
        else:
            self.gift_question.cancel()
            embed.description = f"Disabled gift questions for subscribed channels."
            await ctx.send(embed=embed)

    @commands.command(aliases=["gqstatus"], brief="Shows if gift questions are enabled or disabled.", description="This command will display whether gift questions are currently enabled or disabled.")
    async def giftquestionstatus(self, ctx: commands.Context):
        embed = self.economy_embed(ctx)
        if self.gift_question.is_running():
            embed.description = "Currently Enabled."
            return await ctx.send(embed=embed)
        if not self.gift_question.is_running():
            embed.description = "Currently Disabled."
            return await ctx.send(embed=embed)

    @commands.command(aliases=["tgc", "togglegc"], brief="Subscribes or unsubscribes the current channel to the list of gift channels.", description="This command will subscribe or unsubscribe the current channel to the list of gift channels.")
    async def togglegiftchannel(self, ctx: commands.Context):
        giftchannels = economy_dboperations.get_all_giftchannels(self.connection, ctx.guild.id)
        print(giftchannels)
        giftchannels_id_list = []
        for channel in giftchannels:
            giftchannels_id_list.append(channel[1])
        embed = self.economy_embed(ctx)
        if ctx.channel.id not in giftchannels_id_list:
            economy_dboperations.add_giftchannel(self.connection, ctx.guild.id, ctx.channel.id)
            embed.description = f"Subscribed {ctx.channel.mention} to the list of gift channels."
            await ctx.send(embed=embed)
        else:
            economy_dboperations.delete_giftchannel(self.connection, ctx.guild.id, ctx.channel.id)
            embed.description = f"Unsubscribed {ctx.channel.mention} from the list of gift channels."
            await ctx.send(embed=embed)

    @commands.command(aliases=["gclist"], brief="Displays a list of channels that are subscribed to gift questions.", description="This command will display a list of channels that are subscribed to gift questions.")
    async def giftchannels(self, ctx: commands.Context):
        embed = self.economy_embed(ctx)
        embed.title = "Zen | Gift Channels"
        giftchannels = economy_dboperations.get_all_giftchannels(self.connection, ctx.guild.id)
        print(giftchannels)
        channels = []
        for channel in giftchannels:
            channels.append(await self.client.fetch_channel(channel[1]))
        embed.description = ""
        for index, channel in enumerate(channels):
            embed.description += f"{index + 1} - {channel.mention}\n"
        await ctx.send(embed=embed)

    @commands.command(aliases=["bal", "money", "networth"], brief="Displays your balance or the balance of someone you specified.", description="This command will display your balance or the balance of someone you specified.")
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

    @commands.command(aliases=["giftmoney", "transfer", "transfermoney", "send", "gift"], brief="Sends `amount` of money to someone.", description="This command will send the amount of money you speficied to someone.")
    async def sendmoney(self, ctx: commands.Context, amount: int, member: discord.Member):
        embed = self.economy_embed(ctx)
        if amount < 0:
            embed.description = "The amount has to be positive!"
            return await ctx.send(embed=embed)
        if economy_dboperations.check_member_exists(self.connection, ctx.author) and economy_dboperations.check_member_exists(self.connection, member):
            money = economy_dboperations.get_member_money(self.connection, ctx.author)
            if amount > money:
                embed.description = "You don't have that much money!"
                return await ctx.send(embed=embed)
            member_status = economy_dboperations.add_member_money(self.connection, member, amount)
            author_status = economy_dboperations.add_member_money(self.connection, ctx.author, -amount)
            embed.description = f"You have sent **{amount}{self.displayed_currency}** to {member.mention}.\n{author_status}\n{member_status}"
            return await ctx.send(embed=embed)
        if not economy_dboperations.check_member_exists(self.connection, ctx.author):
            embed.description = f"You need an account to be able to send money!\nType {self.client.command_prefix}createaccount to create an account."
            return await ctx.send(embed=embed)
        if not economy_dboperations.check_member_exists(self.connection, member):
            embed.description = f"{member.mention} doesn't have an account!\nType {self.client.command_prefix}createaccount to create an account."
            return await ctx.send(embed=embed)

    @commands.command(aliases=["moneyadd", "addbalance", "addbal", "balanceadd"], brief="Adds the amount of money to the specified user.", description="This command will let you add the amount of money you specified to a user you specified.")
    async def addmoney(self, ctx: commands.Context, amount: int, member: discord.Member = None):
        embed = self.economy_embed(ctx)
        if amount < 0:
            embed.description = "The amount has to be positive!"
            return await ctx.send(embed=embed)
        if member is None:
            if economy_dboperations.check_member_exists(self.connection, ctx.author):
                money = economy_dboperations.add_member_money(self.connection, ctx.author, amount)
                embed.description = f"Added **{amount}**{self.displayed_currency} to {ctx.author.mention}'s account!\n{money}"
                return await ctx.send(embed=self.db_exception_embed(ctx, money)) if self.db_exception_embed(ctx, money) else await ctx.send(embed=embed)
            embed.description = f"{ctx.author.mention} doesn't have an account!\nType {self.client.command_prefix}createaccount to create an account."
            return await ctx.send(embed=embed)
        else:
            if economy_dboperations.check_member_exists(self.connection, member):
                money = economy_dboperations.add_member_money(self.connection, member, amount)
                embed.description = f"Added **{amount}**{self.displayed_currency} to {member.mention}'s account!\n{money}"
                return await ctx.send(embed=self.db_exception_embed(ctx, money)) if self.db_exception_embed(ctx, money) else await ctx.send(embed=embed)
            embed.description = f"{member.mention} doesn't have an account!\nType {self.client.command_prefix}createaccount to create an account."
            return await ctx.send(embed=embed)

    @commands.command(aliases=["moneyremove", "removebalance", "removebal", "balremove", "balanceremove"], brief="Removes the amount of money from the specified user.", description="This command will remove the amount of money you specified from a user you specified.")
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
                embed.description = f"Removed **{amount}**{self.displayed_currency} from {ctx.author.mention}'s account!\n{money}"
                return await ctx.send(embed=self.db_exception_embed(ctx, money)) if self.db_exception_embed(ctx, money) else await ctx.send(embed=embed)
            embed.description = f"{ctx.author.mention} doesn't have an account!\nType {self.client.command_prefix}createaccount to create an account."
            return await ctx.send(embed=embed)
        else:
            if economy_dboperations.check_member_exists(self.connection, member):
                networth = economy_dboperations.get_member_money(self.connection, ctx.author)
                if amount > networth:
                    amount = networth
                money = economy_dboperations.add_member_money(self.connection, member, -amount)
                embed.description = f"Removed **{amount}**{self.displayed_currency} from {member.mention}'s account!\n{money}"
                return await ctx.send(embed=self.db_exception_embed(ctx, money)) if self.db_exception_embed(ctx, money) else await ctx.send(embed=embed)
            embed.description = f"{member.mention} doesn't have an account!\nType {self.client.command_prefix}createaccount to create an account."
            return await ctx.send(embed=embed)

    @commands.command(brief="Work with your current rank and earn your rank's salary", description="This command will let you earn money based on the minimum and maximum salary of your current rank.")
    @commands.cooldown(1, 900, commands.BucketType.user)
    async def work(self, ctx: commands.Context):
        embed = self.economy_embed(ctx)
        if economy_dboperations.check_member_exists(self.connection, ctx.author):
            rank = economy_dboperations.get_member_rank(self.connection, ctx.author)
            minmax = economy_dboperations.get_rank_minmax_salary(self.connection, rank)
            salary = random.randint(minmax[0], minmax[1])
            operation = economy_dboperations.add_member_money(self.connection, ctx.author, salary)
            embed.description = f"You worked hard today and earned **{salary}**{self.displayed_currency} as {rank.capitalize()}!\n{operation}"
            return await ctx.send(embed=self.db_exception_embed(ctx, operation)) if self.db_exception_embed(ctx, operation) else await ctx.send(embed=embed)
        embed.description = f"{ctx.author.mention} doesn't have an account!\nType {self.client.command_prefix}createaccount to create an account."
        return await ctx.send(embed=embed)

    @commands.command(brief="Gives you your daily gift based on your rank.", description="This command will give you a daily gift containing around 10 times the salary of your current rank.")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx: commands.Context):
        embed = self.economy_embed(ctx)
        if economy_dboperations.check_member_exists(self.connection, ctx.author):
            rank = economy_dboperations.get_member_rank(self.connection, ctx.author)
            minmax = economy_dboperations.get_rank_minmax_salary(self.connection, rank)
            salary = random.randint(minmax[0]*10, minmax[1]*10)
            operation = economy_dboperations.add_member_money(self.connection, ctx.author, salary)
            embed.description = f"You opened your daily gift and earned **{salary}**{self.displayed_currency}!\n{operation}"
            return await ctx.send(embed=self.db_exception_embed(ctx, operation)) if self.db_exception_embed(ctx, operation) else await ctx.send(embed=embed)
        embed.description = f"{ctx.author.mention} doesn't have an account!\nType {self.client.command_prefix}createaccount to create an account."
        return await ctx.send(embed=embed)        

    @commands.command(aliases=["createacc"], brief="Lets you create an account.", description="This command will let you create an account in the economy module.")
    async def createaccount(self, ctx: commands.Context):
        embed = self.economy_embed(ctx)
        rank = economy_dboperations.get_rank_with_position(self.connection, 1)
        if not rank:
            embed.description = "A staff member needs to set up the default rank before members can create an account."
            return await ctx.send(embed=embed)
        operation = economy_dboperations.create_member(self.connection, ctx.author.id, ctx.author.name, self.starting_money, rank[0][1])
        embed.description = f"Account created with **{self.starting_money}**{self.displayed_currency}, starting as {rank[0][1].capitalize()}."
        return await ctx.send(embed=self.db_exception_embed(ctx, operation)) if self.db_exception_embed(ctx, operation) else await ctx.send(embed=embed)

    @commands.command(aliases=["deleteacc", "delacc"], brief="Deletes your current account.", description="This command will delete your current account in the economy module.")
    async def deleteaccount(self, ctx: commands.Context):
        embed = self.economy_embed(ctx)
        operation = economy_dboperations.delete_member(self.connection, ctx.author.id)
        embed.description = "Your account has been succesfully deleted!"
        return await ctx.send(embed=self.db_exception_embed(ctx, operation)) if self.db_exception_embed(ctx, operation) else await ctx.send(embed=embed)

    @commands.command(brief="Lets staff create a rank.", description="This command will let a staff member create a rank in the economy module.")
    async def createrank(self, ctx: commands.Context, rank: str, minsalary: int, maxsalary: int, required: int = 0, position: int = 1):
        embed = self.economy_embed(ctx)
        if minsalary <=0 or maxsalary <= 0:
            embed.description = "The minimum and the maximum salary can't be negative or 0$"
            return await ctx.send(embed=embed)
        if minsalary >= maxsalary:
            embed.description = "The minimum salary can't be higher or equal to the maximum salary."
            return await ctx.send(embed=embed)
        operation = economy_dboperations.create_rank(self.connection, rank.lower(), minsalary, maxsalary, required, position)
        embed.description = f"Created {rank.capitalize()} with a minimum daily salary of {minsalary}{self.displayed_currency} and a maximum daily salary of {maxsalary}{self.displayed_currency}."
        return await ctx.send(embed=self.db_exception_embed(ctx, operation)) if self.db_exception_embed(ctx, operation) else await ctx.send(embed=embed)

    @commands.command(aliases=["updaterank"], brief="Lets staff modify a rank.", description="This command will let a staff member modify an existing rank in the economy module.")
    async def modifyrank(self, ctx: commands.Context, position: int):
        embed = self.economy_embed(ctx)
        ranks = economy_dboperations.get_all_ranks(self.connection)
        positions_list = []
        for rank in ranks:
            positions_list.append(rank[5])
        if position not in positions_list:
            embed.description = "The rank you're trying to delete doesn't exist."
            return await ctx.send(embed=embed)
        rank = economy_dboperations.get_rank_with_position(self.connection, position)[0]
        try:
            embed.description = "Enter a new name for the rank:"
            await ctx.send(embed=embed)
            new_name = await self.client.wait_for("message", check=lambda x: x.author == ctx.author, timeout=60.0)
            while not new_name.content.isalpha():
                await ctx.send(embed=embed)
                new_name = await self.client.wait_for("message", check=lambda x: x.author == ctx.author, timeout=60.0)
            embed.description = f"Enter a new minimum salary for {new_name.content.capitalize()}:"
            await ctx.send(embed=embed)
            new_minsalary = await self.client.wait_for("message", check=lambda x: x.author == ctx.author, timeout=60.0)
            while not new_minsalary.content.isnumeric():
                await ctx.send(embed=embed)
                new_minsalary = await self.client.wait_for("message", check=lambda x: x.author == ctx.author, timeout=60.0)
                if new_minsalary.content.isnumeric():
                    while int(new_minsalary.content) <= 0:
                        embed.description = f"The minimum salary has to be higher than 0{self.displayed_currency}\nEnter a new minimum salary for {new_name.content.capitalize()}:"
                        await ctx.send(embed=embed)
                        new_minsalary = await self.client.wait_for("message", check=lambda x: x.author == ctx.author, timeout=60.0)
            embed.description = f"Enter a new maximum salary for {new_name.content.capitalize()}:"
            await ctx.send(embed=embed)
            new_maxsalary = await self.client.wait_for("message", check=lambda x: x.author == ctx.author, timeout=60.0)
            while not new_maxsalary.content.isnumeric():
                await ctx.send(embed=embed)
                new_maxsalary = await self.client.wait_for("message", check=lambda x: x.author == ctx.author, timeout=60.0)
                if new_maxsalary.content.isnumeric():
                    while int(new_maxsalary.content) <= int(new_minsalary.content):
                        embed.description = f"The maximum salary has to be higher than the minimum salary!\nEnter a new maximum salary for {new_name.content.capitalize()}:"
                        await ctx.send(embed=embed)
                        new_maxsalary = await self.client.wait_for("message", check=lambda x: x.author == ctx.author, timeout=60.0)
            embed.description = f"Enter a new required net worth for {new_name.content.capitalize()}:"
            await ctx.send(embed=embed)
            new_required = await self.client.wait_for("message", check=lambda x: x.author == ctx.author, timeout=60.0)
            while not new_required.content.isnumeric():
                await ctx.send(embed=embed)
                new_required = await self.client.wait_for("message", check=lambda x: x.author == ctx.author, timeout=60.0)
                if new_required.content.isnumeric():
                    while int(new_required.content) < 0:
                        embed.description = f"The required net worth cannot be negative.\nEnter a new required net worth for {new_name.capitalize()}:"
                        await ctx.send(embed=embed)
                        new_required = await self.client.wait_for("message", check=lambda x: x.author == ctx.author, timeout=60.0)
            if position == 1:
                new_required.content = "0"
        except asyncio.TimeoutError:
            await ctx.send("You have been timed out!")
            return
        economy_dboperations.update_rank(self.connection, new_name.content.lower(), int(new_minsalary.content), int(new_maxsalary.content), int(new_required.content), position)
        embed.description = f"You have successfully modified {rank[1]} to {new_name.content.capitalize()}!"
        await ctx.send(embed=embed)

    @commands.command(aliases=["removerank"], brief="Lets staff delete a rank.", description="This command will let a staff member delete a rank in the economy module")
    async def deleterank(self, ctx: commands.Context, position: int):
        embed = self.economy_embed(ctx)
        default_rank = economy_dboperations.get_default_rank(self.connection)[0][1]
        ranks = economy_dboperations.get_all_ranks(self.connection)
        ranks_list = []
        for p in ranks:
            ranks_list.append(p[5])
        print(ranks_list)
        if position not in ranks_list:
            embed.description = "The rank you're trying to delete doesn't exist."
            return await ctx.send(embed=embed)
        if position.lower() == default_rank:
            embed.description = f"You cannot delete the default rank!\nUse {self.client.command_prefix}modifyrank to modify the default rank"
            return await ctx.send(embed=embed)
        operation = economy_dboperations.delete_rank(self.connection, position)
        embed.description = "You have successfully deleted the rank!"
        return await ctx.send(embed=self.db_exception_embed(ctx, operation)) if self.db_exception_embed(ctx, operation) else await ctx.send(embed=embed)

    @commands.command(aliases=["showrank", "rankinfo"], brief="Displays specific information about a rank.", description="This command will display all the information about a specific rank such as the minimum salary, maximum salary, required net worth and rank level.")
    async def rank(self, ctx: commands.Context, position: int):
        embed = self.economy_embed(ctx)
        ranks = economy_dboperations.get_all_ranks(self.connection)
        positions_list = []
        for p in ranks:
            positions_list.append(p[5])
        if position not in positions_list:
            embed.description = "The rank you're trying display doesn't exist."
            return await ctx.send(embed=embed)
        rank = economy_dboperations.get_rank_with_position(self.connection, position)[0]
        embed.add_field(name="Rank Name", value=f"**{rank[1].capitalize()}**", inline=False)
        embed.add_field(name="Salary Range", value=f"**{rank[2]}{self.displayed_currency} to {rank[3]}{self.displayed_currency}**", inline=False)
        embed.add_field(name="Required Net Worth", value=f"**{rank[4]}{self.displayed_currency}**", inline=False)
        embed.add_field(name="Rank Level", value=f"**{rank[5]}**", inline=False)
        await ctx.send(embed=embed)

    @commands.command(brief="Lets a staff change the starting balance/money.", description="This command will let a staff member change the starting balance/money of new members.")
    async def startingmoney(self, ctx: commands.Context, money: int = None):
        embed = self.economy_embed(ctx)
        if money is None:
            embed.description = f"The starting money is currently **{self.starting_money}**{self.displayed_currency}"
        else:
            self.starting_money = money
            embed.description = f"Successfully changed starting money to **{money}**{self.displayed_currency}"
        await ctx.send(embed=embed)

    @commands.command(brief="Displays the currency that is currently used.", description="This command will display the currency that is currently being used.")
    async def currency(self, ctx: commands.Context, currency = None):
        embed = self.economy_embed(ctx)
        if currency is None:
            embed.description = f"The current currency is {self.displayed_currency}"
        else:
            self.displayed_currency = currency
            embed.description = f"Successfully changed the currency to {currency}!"
        await ctx.send(embed=embed)

    @commands.command(brief="Displays information about your economy profile or the one of a user you specified.", description="This command will display the information of your economy profile or the one of a user you specified.")
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

    @commands.command(aliases=["economytop"], brief="Displays the richest members registered in the economy module.", description="This command will display the richest registered members and their respective ranks in the economy module.")
    async def leaderboard(self, ctx: commands.Context):
        embed = self.economy_embed(ctx)
        embed.description = ""
        members_data = economy_dboperations.get_leaderboard(self.connection)
        for index, member in enumerate(members_data):
            embed.description += f"{index + 1}. <@{member[1]}> **{member[3]}**{self.displayed_currency} - **{member[4].capitalize()}**\n"
        await ctx.send(embed=embed)

    @commands.command(brief="Displays the ranks currently available.", description="This command will display a list of currently available ranks.")
    async def ranks(self, ctx: commands.Context):
        embed = self.economy_embed(ctx)
        embed.description = ""
        ranks_data = economy_dboperations.get_ranks_by_position(self.connection)
        for rank in ranks_data:
            embed.description += f"{rank[5]}. **{rank[1].capitalize()}** (Requires: **{rank[4]}**{self.displayed_currency})\n"
        await ctx.send(embed=embed)

    @work.error
    async def work_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = self.economy_embed(ctx)
            embed.description = f"You can't work yet! Try again in {self.convert(error.retry_after)}"
            await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(Economy(client))