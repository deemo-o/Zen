import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
 
class Games(commands.Cog, description="Games commands."):
    
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Games module has been loaded.")
    
    @commands.command(aliases=["rps"], brief="Play Rock-Paper-Scissors, Best of 5", description="""This command will allow you to play a 
    Rock-Paper-Scissors match, @ a user after the command to play against them or you will be matched against the infamous Zen Bot.""")
    async def rockpaperscissors(self, ctx: commands.Context, member: discord.Member = None): 
        timeOutEmbed = discord.Embed(title="Zen | Games", description="Too long! Game cancelled.")
        botMoves  = {
            1 : 'Rock',
            2 : 'Paper',
            3 : 'Scissors'
        }
        playerMoves = {
            'r': 'Rock',
            'rock': 'Rock',
            'p' : 'Paper',
            'paper' : 'Paper',
            's' : 'Scissors',
            'scissors' : 'Scissors'
        }
        def checkAnswer(answer):
            if answer.content.lower() in ["y", "yes", "n", "no"] and answer.channel == ctx.channel:
                return True

        def checkP1Move(move):
            if move.content.lower() in ["r", "rock", "p", "paper", "s", "scissors"] and move.channel == ctx.author.dm_channel:
                return True

        def checkP2Move(move):
            if move.content.lower() in ["r", "rock", "p", "paper", "s", "scissors"] and move.channel == member.dm_channel:
                return True

        def checkWinner(p1Move, p2Move):
            if p1Move == p2Move:
                return None
            if p1Move == 'Rock':
                if p2Move == "Paper":
                    return player2
                else: 
                    return player1
            if p1Move == 'Paper':
                if p2Move == "Scissors":
                    return player2
                else: 
                    return player1
            if p1Move == 'Scissors':
                if p2Move == "Rock":
                    return player2
                else: 
                    return player1

        player1 = ctx.author.name
        
        if member is None:
            player2 = "The Zen Bot" 
        elif member == ctx.author:
            await ctx.send(embed=discord.Embed(title="Zen | Games", description = f"{player1} will play against {player1}! ... Wait, no..."), delete_after=60)
            return
        else: 
            player2 = member.name
            await ctx.send(embed=discord.Embed(title= "Zen | Games", description = f"""{member.mention}, You have been challenged to a game of 
            Rock-Paper-Scissors by {player1}! Do you accept? (y/n)"""), delete_after=60)
            try:
                ans = await self.client.wait_for('message', check=checkAnswer, timeout = 60)
            except asyncio.TimeoutError:
                await ctx.send(embed=timeOutEmbed, delete_after=60)
                return
            if ans.content.lower() in ["y", "yes",]:
                await ctx.send(embed=discord.Embed(title="Zen | Games", description =f"{ans.author.name} has accepted the challenge!"), delete_after=60)
            else:
                await ctx.send(embed=discord.Embed(title="Zen | Games", description =f"{ans.author.name} has declined the challenge!"), delete_after=60)
                return

        await ctx.send(embed=discord.Embed(title="Zen | Games", description =f"""Starting a game of Rock-Paper-Scissors... 
        {player1} will be matched against {player2}. Each player will be privately messaged to get their weapon of choice."""), delete_after=60)
        
        chooseMove = "Choose between: Rock('r'), Paper('p'), or Scissors('s')"
        p1Points = 0
        p2Points = 0
        round = 1
        finalWinner = None

        while p1Points < 2 or p2Points < 2:
            await ctx.author.send(embed=discord.Embed(title="Zen | Games", description=f"Round {round}: {chooseMove}"), delete_after=60)
            try:
                p1Input = await self.client.wait_for("message", check=checkP1Move, timeout = 60)
                p1Move = playerMoves[p1Input.content.lower()]
            except asyncio.TimeoutError:
                await ctx.send(embed=timeOutEmbed, delete_after=60)
                return

            if player2 == "The Zen Bot":
                p2Move = botMoves[random.randint(1, 3)]
            else:
                await member.send(embed=discord.Embed(title="Zen | Games", description=f"Round {round}: {chooseMove}"), delete_after=60)
                try:
                    p2Input = await self.client.wait_for("message", check=checkP2Move, timeout = 60)
                    p2Move = playerMoves[p2Input.content.lower()]
                except asyncio.TimeoutError:
                    await ctx.send(embed=timeOutEmbed, delete_after=60)
                    return
            
            winner = checkWinner(p1Move, p2Move)
            if winner == player1:
                p1Points += 1
                roundResult = f"{player1} wins this round! {p1Move} Beats {p2Move}. Score: {p1Points} - {p2Points}"
            elif winner == player2:
                p2Points += 1
                roundResult = f"{player2} wins this round! {p2Move} Beats {p1Move}. Score: {p1Points} - {p2Points}"
            else:
                roundResult = f"Tie! Both players chose {p1Move}. Score: {p1Points} - {p2Points}"

            roundEmbed = discord.Embed(title="Zen | Games", description=f"{roundResult}")
            await ctx.author.send(embed=roundEmbed, delete_after=60)
            if player2 != "The Zen Bot":
                await member.send(embed=roundEmbed, delete_after=60)
            
            if p1Points == 2:
                finalWinner = player1
                break
            elif p2Points == 2:
                finalWinner = player2
                break
            round += 1
        
        if p1Points != p2Points:
            await ctx.send(embed=discord.Embed(title="Zen | Games", description=f"{finalWinner} wins the game! Final Score: {max(p1Points, p2Points)} - {min(p1Points, p2Points)}"), delete_after=60)
        else: 
            await ctx.send(embed=discord.Embed(title="Zen | Games", description=f"Tie! Final Score: {p1Points} - {p2Points}"), delete_after=60)

async def setup(client):
    await client.add_cog(Games(client))