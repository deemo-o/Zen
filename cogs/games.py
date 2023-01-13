import asyncio
import discord
import random
from discord.ext import commands
from discord import app_commands
from utils.games_utils import battleship_dboperations
import random
import asyncio

class Games(commands.Cog, description="Games commands."):

    def __init__(self, client: commands.Bot):
        self.client = client
        self.connection = battleship_dboperations.connection()

    def games_embed(self, ctx: commands.Context) -> discord.Embed:
        embed = discord.Embed(title="Zen | Games", color=ctx.author.color)
        return embed

    def expected_rating(self, player1_rating, player2_rating):
        return 1 / (1 + 10 ** ((player2_rating - player1_rating) / 400))

    def cog_command_error(self, ctx: commands.Context, error):
        print(error)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Games module has been loaded.")
        battleship_dboperations.create_table(self.connection)

    @commands.command()
    async def battleshiptop(self, ctx: commands.Context):
        embed = self.games_embed(ctx)
        embed.title = "Zen | BattleShip Leaderboard"
        embed.description = ""
        members_data = battleship_dboperations.get_leaderboard(self.connection)
        print(members_data)
        for index, member in enumerate(members_data):
            embed.description += f"{index + 1}. <@{member[1]}> - **{member[3]} ELO**\n"

        await ctx.send(embed=embed)

    @commands.command()
    async def battleship(self, ctx: commands.Context, member: discord.Member):
        player1_board = [[0 for _ in range(10)] for _ in range(10)]
        player2_board = [[0 for _ in range(10)] for _ in range(10)]
        coordinates = [
            [":regional_indicator_a:", ":regional_indicator_b:", ":regional_indicator_c:", ":regional_indicator_d:",
             ":regional_indicator_e:", ":regional_indicator_f:", ":regional_indicator_g:", ":regional_indicator_h:",
             ":regional_indicator_i:", ":regional_indicator_j:"],
            [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":keycap_ten:"]]
        string_numbers = ""
        for x in range(len(coordinates[1])):
            string_numbers += coordinates[1][x]

        sizes = [1]

        player1_ships = []
        for size in sizes:
            placed = False
            while not placed:
                row = random.randint(0, 9)
                col = random.randint(0, 9)
                orientation = random.choice(['horizontal', 'vertical'])

                fits = True
                if orientation == 'horizontal':
                    if col + size > 10:
                        fits = False
                    else:
                        for i in range(col, col + size):
                            if player1_board[row][i] != 0:
                                fits = False
                                break
                else:
                    if row + size > 10:
                        fits = False
                    else:
                        for i in range(row, row + size):
                            if player1_board[i][col] != 0:
                                fits = False
                                break
                if fits:
                    occupied_coords = []
                    if orientation == 'horizontal':
                        for i in range(col, col + size):
                            player1_board[row][i] = 1
                            occupied_coords.append((row, i))
                    else:  # orientation == 'vertical'
                        for i in range(row, row + size):
                            player1_board[i][col] = 1
                            occupied_coords.append((i, col))
                    player1_ships.append(occupied_coords)
                    placed = True

        player2_ships = []
        for size in sizes:
            placed = False
            while not placed:
                row = random.randint(0, 9)
                col = random.randint(0, 9)
                orientation = random.choice(['horizontal', 'vertical'])

                fits = True
                if orientation == 'horizontal':
                    if col + size > 10:
                        fits = False
                    else:
                        for i in range(col, col + size):
                            if player2_board[row][i] != 0:
                                fits = False
                                break
                else:
                    if row + size > 10:
                        fits = False
                    else:
                        for i in range(row, row + size):
                            if player2_board[i][col] != 0:
                                fits = False
                                break
                if fits:
                    occupied_coords = []
                    if orientation == 'horizontal':
                        for i in range(col, col + size):
                            player2_board[row][i] = 1
                            occupied_coords.append((row, i))
                    else:  # orientation == 'vertical'
                        for i in range(row, row + size):
                            player2_board[i][col] = 1
                            occupied_coords.append((i, col))
                    player2_ships.append(occupied_coords)
                    placed = True

        while True:
            player1_win = False
            player2_win = False

            def display_player1_board():
                player1_board_message = ""
                for i in range(len(player1_board)):
                    player1_board_message += "\n"
                    for j in range(len(player1_board)):
                        if j == 0:
                            player1_board_message += coordinates[0][i]
                        if player1_board[i][j] == 3:
                            player1_board_message += ":black_large_square:"
                        if player1_board[i][j] == 2:
                            player1_board_message += ":x:"
                        if player1_board[i][j] == 1:
                            player1_board_message += ":ship:"
                        if player1_board[i][j] == 0:
                            player1_board_message += ":blue_square:"
                return player1_board_message

            def display_player1_opponent_board():
                player1_opponent_board_message = ""
                for i in range(len(player2_board)):
                    player1_opponent_board_message += "\n"
                    for j in range(len(player2_board)):
                        if j == 0:
                            player1_opponent_board_message += coordinates[0][i]
                        if player2_board[i][j] == 3:
                            player1_opponent_board_message += ":black_large_square:"
                            continue
                        if player2_board[i][j] == 2:
                            player1_opponent_board_message += ":dart:"
                        else:
                            player1_opponent_board_message += ":blue_square:"
                return player1_opponent_board_message

            await ctx.author.send(f"Your board {ctx.author.mention}:")
            await ctx.author.send(f"<:zen:1061021427718950954>{string_numbers}{display_player1_board()}")
            await ctx.author.send(f"{member.mention}'s board:")
            await ctx.author.send(f"<:zen:1061021427718950954>{string_numbers}{display_player1_opponent_board()}")
            await asyncio.sleep(1)
            await ctx.author.send(f"It's your turn {ctx.author.mention}, target a cell to attack (e.g. `B6`)")

            def check(m):
                if m.content == f"{m.content[0]}10":
                    x = ord(m.content[0].upper()) - 65
                    y = 9
                    if player2_board[x][y] != 2 and player2_board[x][y] != 3:
                        return m.author == ctx.author
                if len(m.content) == 2 and m.content[0].isalpha() and m.content[1].isnumeric():
                    x = ord(m.content[0].upper()) - 65
                    y = int(m.content[1]) - 1
                    if player2_board[x][y] != 2 and player2_board[x][y] != 3:
                        return m.author == ctx.author

            try:
                response = await self.client.wait_for("message", check=check, timeout=60.0)
            except asyncio.TimeoutError:
                await ctx.author.send("You have been timed out!", delete_after=30)
                return

            await asyncio.sleep(1)

            x = ord(response.content[0].upper()) - 65
            if len(response.content) == 3:
                y = 9
            else:
                y = int(response.content[1]) - 1

            if player2_board[x][y] == 1:
                player2_board[x][y] = 2
                await ctx.author.send(f"You hit a ship on {response.content[0].upper()}{y + 1}!")
            else:
                player2_board[x][y] = 3
                await ctx.author.send(f"You didn't hit anything on {response.content[0].upper()}{y + 1}.")

            await asyncio.sleep(1)

            for x in range(len(player2_ships[0])):
                coord = player2_ships[0][x]
                if player2_board[coord[0]][coord[1]] == 2:
                    player1_win = True
                    continue
                else:
                    player1_win = False

            if player1_win:
                await ctx.send(f"{ctx.author.mention} won the game!", delete_after=30)
                player1_rating = battleship_dboperations.get_rating(self.connection, ctx.author.id)
                player2_rating = battleship_dboperations.get_rating(self.connection, member.id)
                player1_expected_rating = self.expected_rating(player1_rating, player2_rating)
                player2_expected_rating = self.expected_rating(player2_rating, player1_rating)
                player1_new_rating = player1_rating + 32 * (1 - player1_expected_rating)
                player2_new_rating = player2_rating + 32 * (0 - player2_expected_rating)
                battleship_dboperations.insert_rating(self.connection, ctx.author.id, ctx.author.name, round(player1_new_rating))
                battleship_dboperations.insert_rating(self.connection, member.id, member.name, round(player2_new_rating))
                await ctx.send(f"{ctx.author.mention}'s rating change: {player1_rating} -> {round(player1_new_rating)}\n{member.mention}'s rating change: {player2_rating} - > {round(player2_new_rating)}")
                return

            await ctx.author.send(f"It's {member.mention}'s turn!")

            # player2's turn
            def display_player2_board():
                player2_board_message = ""
                for i in range(len(player2_board)):
                    player2_board_message += "\n"
                    for j in range(len(player2_board)):
                        if j == 0:
                            player2_board_message += coordinates[0][i]
                        if player2_board[i][j] == 3:
                            player2_board_message += ":black_large_square:"
                        if player2_board[i][j] == 2:
                            player2_board_message += ":x:"
                        if player2_board[i][j] == 1:
                            player2_board_message += ":ship:"
                        if player2_board[i][j] == 0:
                            player2_board_message += ":blue_square:"
                return player2_board_message

            def display_player2_opponent_board():
                player2_opponent_board_message = ""
                for i in range(len(player1_board)):
                    player2_opponent_board_message += "\n"
                    for j in range(len(player1_board)):
                        if j == 0:
                            player2_opponent_board_message += coordinates[0][i]
                        if player1_board[i][j] == 3:
                            player2_opponent_board_message += ":black_large_square:"
                            continue
                        if player1_board[i][j] == 2:
                            player2_opponent_board_message += ":dart:"
                        else:
                            player2_opponent_board_message += ":blue_square:"
                return player2_opponent_board_message

            await member.send(f"Your board {member.mention}:")
            await member.send(f"<:zen:1061021427718950954>{string_numbers}{display_player2_board()}")
            await member.send(f"{ctx.author.mention}'s board:")
            await member.send(f"<:zen:1061021427718950954>{string_numbers}{display_player2_opponent_board()}")
            await asyncio.sleep(1)
            await member.send(f"It's your turn {member.mention}, target a cell to attack (e.g. `B6`)")

            def check(m):
                if m.content == f"{m.content[0]}10":
                    x = ord(m.content[0].upper()) - 65
                    y = 9
                    if player2_board[x][y] != 2 and player2_board[x][y] != 3:
                        return m.author == ctx.author
                if len(m.content) == 2 and m.content[0].isalpha() and m.content[1].isnumeric():
                    x = ord(m.content[0].upper()) - 65
                    y = int(m.content[1]) - 1
                    if player1_board[x][y] != 2 and player1_board[x][y] != 3:
                        return m.author == member

            try:
                response = await self.client.wait_for("message", check=check, timeout=60.0)
            except asyncio.TimeoutError:
                await member.send("You have been timed out!")
                return

            await asyncio.sleep(1)

            x = ord(response.content[0].upper()) - 65
            if len(response.content) == 3:
                y = 9
            else:
                y = int(response.content[1]) - 1

            if player1_board[x][y] == 1:
                player1_board[x][y] = 2
                await member.send(f"You hit a ship on {response.content[0].upper()}{y + 1}!")
            else:
                player1_board[x][y] = 3
                await member.send(f"You didn't hit anything on {response.content[0].upper()}{y + 1}.")

            await asyncio.sleep(1)

            for x in range(len(player1_ships[0])):
                coord = player1_ships[0][x]
                if player1_board[coord[0]][coord[1]] == 2:
                    player2_win = True
                    continue
                else:
                    player2_win = False

            if player2_win:
                await ctx.send(f"{member.mention} won the game!")
                player1_rating = battleship_dboperations.get_rating(self.connection, ctx.author.id)
                player2_rating = battleship_dboperations.get_rating(self.connection, member.id)
                print(player1_rating)
                print(player2_rating)
                player1_expected_rating = self.expected_rating(player1_rating, player2_rating)
                player2_expected_rating = self.expected_rating(player2_rating, player1_rating)
                player1_new_rating = player1_rating + 32 * (0 - player1_expected_rating)
                player2_new_rating = player2_rating + 32 * (1 - player2_expected_rating)
                battleship_dboperations.insert_rating(self.connection, ctx.author.id, ctx.author.name, round(player1_new_rating))
                battleship_dboperations.insert_rating(self.connection, member.id, member.name, round(player2_new_rating))
                await ctx.send(f"{member.mention}'s rating change: {player2_rating} -> {round(player2_new_rating)}\n{ctx.author.mention}'s rating change: {player1_rating} - > {round(player1_new_rating)}")
                return

            await member.send(f"It's {ctx.author.mention}'s turn!")

    @commands.command(aliases=["rps"], brief="Play Rock-Paper-Scissors, Best of 5", description="""This command will allow you to play a 
    Rock-Paper-Scissors match, @ a user after the command to play against them or you will be matched against the infamous Zen Bot.""")
    async def rockpaperscissors(self, ctx: commands.Context, member: discord.Member = None):
        timeOutEmbed = discord.Embed(title="Zen | Games", description="Too long! Game cancelled.")
        botMoves = {
            1: 'Rock',
            2: 'Paper',
            3: 'Scissors'
        }
        playerMoves = {
            'r': 'Rock',
            'rock': 'Rock',
            'p': 'Paper',
            'paper': 'Paper',
            's': 'Scissors',
            'scissors': 'Scissors'
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
            await ctx.send(embed=discord.Embed(title="Zen | Games", description=f"{player1} will play against {player1}! ... Wait, no..."), delete_after=60)
            return
        else:
            player2 = member.name
            await ctx.send(embed=discord.Embed(title="Zen | Games", description=f"""{member.mention}, You have been challenged to a game of Rock-Paper-Scissors by {player1}! Do you accept? (y/n)"""), delete_after=60)
            try:
                ans = await self.client.wait_for('message', check=checkAnswer, timeout=60)
            except asyncio.TimeoutError:
                await ctx.send(embed=timeOutEmbed, delete_after=60)
                return
            if ans.content.lower() in ["y", "yes", ]:
                await ctx.send(embed=discord.Embed(title="Zen | Games", description=f"{ans.author.name} has accepted the challenge!"), delete_after=60)
            else:
                await ctx.send(embed=discord.Embed(title="Zen | Games", description=f"{ans.author.name} has declined the challenge!"), delete_after=60)
                return

        await ctx.send(embed=discord.Embed(title="Zen | Games", description=f"""Starting a game of Rock-Paper-Scissors... {player1} will be matched against {player2}. Each player will be privately messaged to get their weapon of choice."""), delete_after=60)

        chooseMove = "Choose between: Rock('r'), Paper('p'), or Scissors('s')"
        p1Points = 0
        p2Points = 0
        round = 1
        finalWinner = None

        while p1Points < 2 or p2Points < 2:
            await ctx.author.send(embed=discord.Embed(title="Zen | Games", description=f"Round {round}: {chooseMove}"), delete_after=60)
            try:
                p1Input = await self.client.wait_for("message", check=checkP1Move, timeout=60)
                p1Move = playerMoves[p1Input.content.lower()]
            except asyncio.TimeoutError:
                await ctx.send(embed=timeOutEmbed, delete_after=60)
                return

            if player2 == "The Zen Bot":
                p2Move = botMoves[random.randint(1, 3)]
            else:
                await member.send(embed=discord.Embed(title="Zen | Games", description=f"Round {round}: {chooseMove}"), delete_after=60)
                try:
                    p2Input = await self.client.wait_for("message", check=checkP2Move, timeout=60)
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
