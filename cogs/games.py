import asyncio
import discord
import random
from discord.ext import commands
from discord import app_commands
from games_utils import battleship_dboperations
 
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
        coordinates = [[":regional_indicator_a:", ":regional_indicator_b:", ":regional_indicator_c:", ":regional_indicator_d:", ":regional_indicator_e:", ":regional_indicator_f:", ":regional_indicator_g:", ":regional_indicator_h:", ":regional_indicator_i:", ":regional_indicator_j:"], [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":keycap_ten:"]]
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
                        for i in range(col, col+size):
                            if player1_board[row][i] != 0:
                                fits = False
                                break
                else:
                    if row + size > 10:
                        fits = False
                    else:
                        for i in range(row, row+size):
                            if player1_board[i][col] != 0:
                                fits = False
                                break
                if fits:
                    occupied_coords = []
                    if orientation == 'horizontal':
                        for i in range(col, col+size):
                            player1_board[row][i] = 1
                            occupied_coords.append((row, i))
                    else:  # orientation == 'vertical'
                        for i in range(row, row+size):
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
                        for i in range(col, col+size):
                            if player2_board[row][i] != 0:
                                fits = False
                                break
                else:
                    if row + size > 10:
                        fits = False
                    else:
                        for i in range(row, row+size):
                            if player2_board[i][col] != 0:
                                fits = False
                                break
                if fits:
                    occupied_coords = []
                    if orientation == 'horizontal':
                        for i in range(col, col+size):
                            player2_board[row][i] = 1
                            occupied_coords.append((row, i))
                    else:  # orientation == 'vertical'
                        for i in range(row, row+size):
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

            #player2's turn
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

async def setup(client):
    await client.add_cog(Games(client))