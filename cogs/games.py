import asyncio
import discord
import random
import re
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import Button, View
from utils.games_utils import battleship_dboperations, typeracer_dboperations, rps_dboperations
import random
import asyncio
import random
import nltk
from collections import defaultdict
from nltk.corpus import brown
from utils.games_utils.paragraph_formatter import Formatter
from utils.games_utils.glicko2 import Player

class Games(commands.Cog, description="Games commands."):

    def __init__(self, client: commands.Bot):
        self.client = client
        self.typeracer_games = []
        self.typeracer_unrated_queue = []
        self.typeracer_rated_queue = []
        self.typeracer_cancel_list = []
        self.typeracer_rematch = []
        self.typeracer_challenges = defaultdict(list)
        self.connection = battleship_dboperations.connection()
        self.rps_connection = rps_dboperations.connection()

    def games_embed(self, ctx: commands.Context) -> discord.Embed:
        embed = discord.Embed(title="Zen | Games", color=ctx.author.color)
        return embed

    def expected_rating(self, player1_rating, player2_rating):
        return 1 / (1 + 10 ** ((player2_rating - player1_rating) / 400))

    async def cog_command_error(self, ctx: commands.Context, error: str):
        embed = self.games_embed(ctx)
        if isinstance(error, Exception):
            embed.description = str(error).capitalize()
            return await ctx.send(embed=embed)

    @tasks.loop(minutes=10)
    async def announce_typeracer_queue(self):
        async def join_unrated_queue_button_callback(interaction: discord.Interaction):
            if not self.typeracer_matchmaking.is_running():
                self.typeracer_matchmaking.start()
            await interaction.response.defer()
            if interaction.user not in self.typeracer_unrated_queue and interaction.user in self.typeracer_rated_queue:
                self.typeracer_rated_queue.remove(interaction.user)
            if interaction.user not in self.typeracer_unrated_queue and interaction.user not in self.typeracer_rated_queue:
                self.typeracer_unrated_queue.insert(0, interaction.user)
            embed = interaction.message.embeds[0]
            unrated_queue = ""
            for player in self.typeracer_unrated_queue:
                rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
                unrated_queue += f"{player.mention} - **{rating}**\n"
            rated_queue = ""
            for player in self.typeracer_rated_queue:
                rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
                rated_queue += f"{player.mention} - **{rating}**\n"
            embed.set_field_at(0, name="Current Unrated Queue", value=unrated_queue, inline=True)
            embed.set_field_at(1, name="Current Rated Queue", value=rated_queue, inline=True)
            await interaction.message.edit(embed=embed, view=view)

        async def join_rated_queue_button_callback(interaction: discord.Interaction):
            if not self.typeracer_matchmaking.is_running():
                self.typeracer_matchmaking.start()
            await interaction.response.defer()
            if interaction.user not in self.typeracer_rated_queue and interaction.user in self.typeracer_unrated_queue:
                self.typeracer_unrated_queue.remove(interaction.user)
            if interaction.user not in self.typeracer_rated_queue and interaction.user not in self.typeracer_unrated_queue:
                self.typeracer_rated_queue.insert(0, interaction.user)
            embed = interaction.message.embeds[0]
            unrated_queue = ""
            for player in self.typeracer_unrated_queue:
                rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
                unrated_queue += f"{player.mention} - **{rating}**\n"
            rated_queue = ""
            for player in self.typeracer_rated_queue:
                rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
                rated_queue += f"{player.mention} - **{rating}**\n"
            embed.set_field_at(0, name="Current Unrated Queue", value=unrated_queue, inline=True)
            embed.set_field_at(1, name="Current Rated Queue", value=rated_queue, inline=True)
            await interaction.message.edit(embed=embed, view=view)

        async def leave_queue_button_callback(interaction: discord.Interaction):
            await interaction.response.defer()
            if interaction.user in self.typeracer_unrated_queue:
                self.typeracer_unrated_queue.remove(interaction.user)
            if interaction.user in self.typeracer_rated_queue:
                self.typeracer_rated_queue.remove(interaction.user)
            if interaction.user not in self.typeracer_cancel_list:
                self.typeracer_cancel_list.append(interaction.user)
            embed = interaction.message.embeds[0]
            unrated_queue = ""
            for player in self.typeracer_unrated_queue:
                rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
                unrated_queue += f"{player.mention} - **{rating}**\n"
            rated_queue = ""
            for player in self.typeracer_rated_queue:
                rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
                rated_queue += f"{player.mention} - **{rating}**\n"
            embed.set_field_at(0, name="Current Unrated Queue", value=unrated_queue, inline=True)
            embed.set_field_at(1, name="Current Rated Queue", value=rated_queue, inline=True)
            await interaction.message.edit(embed=embed, view=view)
        
        channels_data = typeracer_dboperations.get_all_queue_announcementchannels(self.connection)
        channels = []
        messages = []
        for channel in channels_data:
            channel = await self.client.fetch_channel(channel[1])
            channels.append(channel)
        embed = discord.Embed(color=discord.Color.from_rgb(248, 175, 175))
        embed.title = "Zen | Typing Race Queue"
        unrated_queue = ""
        for player in self.typeracer_unrated_queue:
            rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
            unrated_queue += f"{player.mention} - **{rating}**\n"
        rated_queue = ""
        for player in self.typeracer_rated_queue:
            rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
            rated_queue += f"{player.mention} - **{rating}**\n"
        embed.add_field(name="Current Unrated Queue", value=unrated_queue, inline=True)
        embed.add_field(name="Current Rated Queue", value=rated_queue, inline=True)
        join_unrated_button = Button(label="Join Unrated Queue", style=discord.ButtonStyle.green)
        join_unrated_button.callback = join_unrated_queue_button_callback
        join_rated_button = Button(label="Join Rated Queue", style=discord.ButtonStyle.green)
        join_rated_button.callback = join_rated_queue_button_callback
        leave_queue_button = Button(label="Leave Queue", style=discord.ButtonStyle.red)
        leave_queue_button.callback = leave_queue_button_callback
        view = View(timeout=None)
        view.add_item(join_unrated_button)
        view.add_item(join_rated_button)
        view.add_item(leave_queue_button)
        for channel in channels:
            message = await channel.send(embed=embed, view=view)
            messages.append(message)
        timer = 0
        while True:
            unrated_queue = ""
            for player in self.typeracer_unrated_queue:
                rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
                unrated_queue += f"{player.mention} - **{rating}**\n"
            rated_queue = ""
            for player in self.typeracer_rated_queue:
                rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
                rated_queue += f"{player.mention} - **{rating}**\n"
            embed.set_field_at(0, name="Current Unrated Queue", value=unrated_queue, inline=True)
            embed.set_field_at(1, name="Current Rated Queue", value=rated_queue, inline=True)
            for message in messages:
                await message.edit(embed=embed)
            await asyncio.sleep(5)
            timer += 5
            if timer == 500:
                for message in messages:
                    await message.delete()
                return

    @tasks.loop(seconds=5)
    async def typeracer_matchmaking(self):
        @tasks.loop(seconds=1, count=120)
        async def timer(embed, message1, message2):
            if timer.current_loop >= 110:
                if timer.current_loop == 119:
                    embed.set_field_at(0, name="Time remaining", value=f"{120 - timer.current_loop} seconds left." if timer.current_loop != 120 else "You ran out of time!", inline=False)
                    await message1.edit(embed=embed)
                    await message2.edit(embed=embed)
                    await asyncio.sleep(1)
                    embed.set_field_at(0, name="Time remaining", value=f"You ran out of time!", inline=False)
                    await message1.edit(embed=embed)
                    return await message2.edit(embed=embed)
                embed.set_field_at(0, name="Time remaining", value=f"{120 - timer.current_loop} seconds left." if timer.current_loop != 120 else "You ran out of time!", inline=False)
                await message1.edit(embed=embed)
                return await message2.edit(embed=embed)
            if timer.current_loop % 5 == 0:
                embed.set_field_at(0, name="Time remaining", value=f"{120 - timer.current_loop} seconds left." if timer.current_loop != 120 else "You ran out of time!", inline=False)
                await message1.edit(embed=embed)
                await message2.edit(embed=embed)

        @tasks.loop(count=1)
        async def wait_for_typeracer_player_1(embed: discord.Embed, player: discord.Member, words, message):
            response = await self.client.wait_for("message", check=lambda m: m.author == player and m.channel == message.channel, timeout=120)
            await player.send("Submitted! Please wait for the result.")
            player_words = response.content.split()
            typo_count = 0
            missing_count = 0
            if timer.is_running():
                player_time = timer.current_loop
                player_score = timer.current_loop
                if len(player_words) < len(words):
                    missing_count += len(words) - len(player_words)
                for x in range(min(len(words), len(player_words))):
                    if "\u034F" in response.content:
                        typo_count = 42069
                        player_words.clear()
                        player_words.append(f"[{player.display_name} is a dirty cheater!]")
                        break
                    if player_words[x] != words[x]:
                        if player_words[x] in words:
                            if words.index(player_words[x]) - x <= 5:
                                continue
                            else:
                                typo_count += 1
                                player_words[x] = f"[{player_words[x]}]"
                        else:
                            typo_count += 1
                            player_words[x] = f"[{player_words[x]}]"
                player_score += (typo_count * 2)
                player_score += (missing_count * 2)
                answer = ""
                for index, word in enumerate(player_words):
                    if index == len(player_words) - 1:
                        answer += word
                    else:
                        answer += f"{word} "
                if missing_count == 0:
                    missing_count = "missed 0 word"
                elif missing_count == 1:
                    missing_count = "missed 1 word"
                else:
                    missing_count = f"missed {missing_count} words"
                if typo_count == 0:
                    typo_count = "made 0 typo"
                elif typo_count == 1:
                    typo_count = "made 1 typo"
                else:
                    typo_count = f"made {typo_count} typos"
                embed.add_field(name=f"{player.display_name.capitalize()}'s Result", value=f"{player.display_name.capitalize()} finished in {player_time} seconds, {typo_count} and {missing_count}!\nFinal score: {player_score}\n```INI\n{answer}\n```", inline=False)

        @tasks.loop(count=1)
        async def wait_for_typeracer_player_2(embed: discord.Embed, player: discord.Member, words, message):
            response = await self.client.wait_for("message", check=lambda m: m.author == player and m.channel == message.channel, timeout=120)
            await player.send("Submitted! Please wait for the result.")
            player_words = response.content.split()
            typo_count = 0
            missing_count = 0
            if timer.is_running():
                player_time = timer.current_loop
                player_score = timer.current_loop
                if len(player_words) < len(words):
                    missing_count += len(words) - len(player_words)
                for x in range(min(len(words), len(player_words))):
                    if "\u034F" in response.content:
                        typo_count = 42069
                        player_words.clear()
                        player_words.append(f"[{player.display_name} is a dirty cheater!]")
                        break
                    if player_words[x] != words[x]:
                        if player_words[x] in words:
                            if words.index(player_words[x]) - x <= 5:
                                continue
                            else:
                                typo_count += 1
                                player_words[x] = f"[{player_words[x]}]"
                        else:
                            typo_count += 1
                            player_words[x] = f"[{player_words[x]}]"
                player_score += (typo_count * 2)
                player_score += (missing_count * 2)
                answer = ""
                for index, word in enumerate(player_words):
                    if index == len(player_words) - 1:
                        answer += word
                    else:
                        answer += f"{word} "
                if missing_count == 0:
                    missing_count = "missed 0 word"
                elif missing_count == 1:
                    missing_count = "missed 1 word"
                else:
                    missing_count = f"missed {missing_count} words"
                if typo_count == 0:
                    typo_count = "made 0 typo"
                elif typo_count == 1:
                    typo_count = "made 1 typo"
                else:
                    typo_count = f"made {typo_count} typos"
                embed.add_field(name=f"{player.display_name.capitalize()}'s Result", value=f"{player.display_name.capitalize()} finished in {player_time} seconds, {typo_count} and {missing_count}!\nFinal score: {player_score}\n```INI\n{answer}\n```", inline=False)
        
        async def rematch_button_callback(interaction: discord.Interaction):
            async def accept_button_callback(interaction: discord.Interaction):
                await interaction.response.defer()
                if interaction.user not in self.typeracer_rematch:
                    self.typeracer_rematch.append(interaction.user)
                    embed = interaction.message.embeds[0]
                    embed.description = "You have accepted the rematch request!"
                    await interaction.message.edit(embed=embed, view=None)
                if player2 in self.typeracer_rematch and player1 in self.typeracer_rematch:
                    self.typeracer_rematch.remove(player1)
                    self.typeracer_rematch.remove(player2)
                    game_start.start()

            async def decline_button_callback(interaction: discord.Interaction):
                await interaction.response.defer()
                if interaction.user not in self.typeracer_rematch:
                    player = player2 if interaction.user == player1 else player1
                    self.typeracer_rematch.remove(player)
                    embed = interaction.message.embeds[0]
                    embed.description = "You have declined the rematch request!"
                    return await interaction.message.edit(embed=embed, view=None)

            await interaction.response.defer()
            await interaction.message.edit(embed=interaction.message.embeds[0], view=None)
            accept_button = Button(label="Accept", style=discord.ButtonStyle.green)
            accept_button.callback = accept_button_callback
            decline_button = Button(label="Decline", style=discord.ButtonStyle.red)
            decline_button.callback = decline_button_callback
            view = View(timeout=None)
            view.add_item(accept_button)
            view.add_item(decline_button)
            embed = discord.Embed()
            if player1 not in self.typeracer_rematch and player2 not in self.typeracer_rematch:
                self.typeracer_rematch.append(player1 if interaction.user == player1 else player2)
                embed.description = f"You have sent {player2.mention if interaction.user == player1 else player1.mention} a rematch request!\nWaiting for their response ."
                message = await player1.send(embed=embed) if player1 == interaction.user else await player2.send(embed=embed)
                if player1 in self.typeracer_rematch and player2 not in self.typeracer_rematch: 
                    embed.description = f"{player1.mention} requested for a rematch!\nWaiting for your response."
                    await player2.send(embed=embed, view=view, delete_after=60)
                if player2 in self.typeracer_rematch and player1 not in self.typeracer_rematch: 
                    embed.description = f"{player2.mention} requested for a rematch!\nWaiting for your response."
                    await player1.send(embed=embed, view=view, delete_after=60)
                timer = 0
                while player1 if player1 == interaction.user else player2 in self.typeracer_rematch:
                    await asyncio.sleep(2)
                    if (player1 if player1 == interaction.user else player2) not in self.typeracer_rematch:
                        break
                    embed.description = f"You have sent {player2.mention if interaction.user == player1 else player1.mention} a rematch request!\nWaiting for their response . ."
                    await message.edit(embed=embed)
                    await asyncio.sleep(2)
                    if (player1 if player1 == interaction.user else player2) not in self.typeracer_rematch:
                        break
                    embed.description = f"You have sent {player2.mention if interaction.user == player1 else player1.mention} a rematch request!\nWaiting for their response . . ."
                    await message.edit(embed=embed)
                    await asyncio.sleep(2)
                    if (player1 if player1 == interaction.user else player2) not in self.typeracer_rematch:
                        break
                    embed.description = f"You have sent {player2.mention if interaction.user == player1 else player1.mention} a rematch request!\nWaiting for their response ."
                    await message.edit(embed=embed)
                    timer += 6
                    if timer == 60:
                        embed.description = f"{player2.mention if interaction.user == player1 else player1.mention} did not respond to your rematch request!"
                        self.typeracer_rematch.remove(player1 if interaction.user == player1 else player2)
                        return await message.edit(embed=embed, delete_after=30)
                if player1 in self.typeracer_games and player2 in self.typeracer_games:
                    embed.description = f"{player2.mention if interaction.user == player1 else player1.mention} has accepted your request for a rematch!"
                    return await message.edit(embed=embed)
                if player1 not in self.typeracer_rematch and player2 not in self.typeracer_rematch:
                    embed.description = f"{player2.mention if interaction.user == player1 else player1.mention} has declined your request for a rematch!"
                    return await message.edit(embed=embed)

        @tasks.loop(count=1)
        async def game_start():
                self.typeracer_games.append(player1)
                self.typeracer_games.append(player2)
                embed = discord.Embed(title="Zen | Typing Race")
                text = brown.words()
                sentences = nltk.sent_tokenize(" ".join(text))
                random_paragraph = ""
                random_paragraph += str(random.choice(sentences))
                while len(random_paragraph) < 250:
                    random_paragraph += str(random.choice(sentences))
                random_paragraph = Formatter.format_paragraph(random_paragraph)
                display_paragraph = random_paragraph.replace(" ", "\u034F ")
                words = random_paragraph.split()
                embed.add_field(name="Rules", value="You have 2 minutes to type the entire paragraph. Write the entire paragraph in 1 message and only send it when you're done. Typos will add extra to your final time.\n\nThe match will start in 10 seconds!", inline=False)
                embed.add_field(name="Match Play", value=f"This is a typing contest between {player1.mention} and {player2.mention}.", inline=False)
                player1_message = await player1.send(embed=embed)
                player2_message = await player2.send(embed=embed)
                await asyncio.sleep(10)
                embed.set_field_at(1, name="Paragraph", value=f"```{display_paragraph}```", inline=False)
                timer.start(embed=embed, message1=player1_message, message2=player2_message)
                result_embed = discord.Embed(title="Zen | Typing Race")
                wait_for_typeracer_player_1.start(embed=result_embed, player=player1, words=words, message=player1_message)
                wait_for_typeracer_player_2.start(embed=result_embed, player=player2, words=words, message=player2_message)
                while True:
                    await asyncio.sleep(1)
                    if wait_for_typeracer_player_1.is_running() and wait_for_typeracer_player_2.is_running() and not timer.is_running():
                        message = Player.update_players(player1, player2, 0.5, matchtype)
                        result_embed.add_field(name="Match Result", value=message, inline=False)
                        await player1.send(embed=result_embed, view=view)
                        await player2.send(embed=result_embed, view=view)
                        break
                    if wait_for_typeracer_player_2.is_running() and not timer.is_running():
                        message = Player.update_players(player1, player2, 1, matchtype)
                        result_embed.add_field(name="Match Result", value=message, inline=False)
                        await player1.send(embed=result_embed, view=view)
                        await player2.send(embed=result_embed, view=view)
                        break
                    if wait_for_typeracer_player_1.is_running() and not timer.is_running():
                        message = Player.update_players(player2, player1, 1, matchtype)
                        result_embed.add_field(name="Match Result", value=message, inline=False)
                        await player2.send(embed=result_embed, view=view)
                        await player1.send(embed=result_embed, view=view)
                        break
                    if not wait_for_typeracer_player_1.is_running() and not wait_for_typeracer_player_2.is_running():
                        timer.cancel()
                        string1 = result_embed.fields[0].value
                        string2 = result_embed.fields[1].value
                        player1_score = re.findall(r'\d+', string1)[3]
                        player1_name = re.findall(r"^\w+", string1)[0]
                        player2_score = re.findall(r'\d+', string2)[3]
                        player2_name = re.findall(r"^\w+", string2)[0]
                        player1_discord = player1 if player1_name == player1.display_name.capitalize() else player2
                        player2_discord = player1 if player2_name == player1.display_name.capitalize() else player2
                        if int(player1_score) < int(player2_score):
                            message = Player.update_players(player1_discord, player2_discord, 1, matchtype)
                            result_embed.add_field(name="Match Result", value=message, inline=False)
                            await player1.send(embed=result_embed, view=view)
                            await player2.send(embed=result_embed, view=view)
                            break
                        if int(player2_score) < int(player1_score):
                            message = Player.update_players(player2_discord, player1_discord, 1, matchtype)
                            result_embed.add_field(name="Match Result", value=message, inline=False)
                            await player1.send(embed=result_embed, view=view)
                            await player2.send(embed=result_embed, view=view)
                            break
                        if player1_score == player2_score:
                            message = Player.update_players(player1_discord, player2_discord, 0.5, matchtype)
                            result_embed.add_field(name="Match Result", value=message, inline=False)
                            await player1.send(embed=result_embed, view=view)
                            await player2.send(embed=result_embed, view=view)
                            break
                self.typeracer_games.remove(player1)
                self.typeracer_games.remove(player2)

        await asyncio.sleep(2)
        if len(self.typeracer_unrated_queue) >= 2:
            matchtype = "unrated"
        elif len(self.typeracer_rated_queue) >= 2:
            matchtype = "rated"
        else:
            matchtype = None
        if matchtype != None:
            if matchtype == "unrated":
                player1, player2 = self.typeracer_unrated_queue.pop(), self.typeracer_unrated_queue.pop()
            if matchtype == "rated":
                player1, player2 = self.typeracer_rated_queue[-1], self.typeracer_rated_queue[-2]
                player1_rating = round(typeracer_dboperations.get_rating(self.connection, player1.id)[0][3]) if typeracer_dboperations.get_rating(self.connection, player1.id) != "Nope" else 1500
                player2_rating = round(typeracer_dboperations.get_rating(self.connection, player2.id)[0][3]) if typeracer_dboperations.get_rating(self.connection, player2.id) != "Nope" else 1500
                counter = 0
                rating_range = 100
                while abs(player1_rating - player2_rating) > rating_range:
                    random.shuffle(self.typeracer_rated_queue)
                    player1, player2 = self.typeracer_rated_queue[-1], self.typeracer_rated_queue[-2]
                    player1_rating = round(typeracer_dboperations.get_rating(self.connection, player1.id)[0][3]) if typeracer_dboperations.get_rating(self.connection, player1.id) != "Nope" else 1500
                    player2_rating = round(typeracer_dboperations.get_rating(self.connection, player2.id)[0][3]) if typeracer_dboperations.get_rating(self.connection, player2.id) != "Nope" else 1500
                    await asyncio.sleep(1)
                    counter += 1
                    if counter % 15 == 0:
                        rating_range += 100
                self.typeracer_rated_queue.remove(player1)
                self.typeracer_rated_queue.remove(player2)
            rematch_button = Button(label="Ask For Rematch", style=discord.ButtonStyle.primary)
            rematch_button.callback = rematch_button_callback
            view = View(timeout=None)
            view.add_item(rematch_button)
            game_start.start()
            if len(self.typeracer_unrated_queue) == 0 and len(self.typeracer_rated_queue) == 0:
                self.typeracer_matchmaking.stop()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Games module has been loaded.")
        battleship_dboperations.create_table(self.connection)
        rps_dboperations.create_table(self.rps_connection)
        typeracer_dboperations.create_table(self.connection)
        typeracer_dboperations.create_queue_announcementchannels_table(self.connection)
        nltk.download("brown")
        nltk.download("punkt")

    @commands.command(aliases=["trqueuechannels", "trqc"])
    async def typeracerqueueannouncementchannels(self, ctx: commands.Context):
        embed = self.games_embed(ctx)
        embed.title = "Zen | Typing Race Queue Announcement Channels"
        channels_data = typeracer_dboperations.get_all_queue_announcementchannels(self.connection)
        channels = []
        for channel in channels_data:
            channel = await self.client.fetch_channel(channel[1])
            if channel in ctx.guild.channels:
                channels.append(channel)
        embed.description = ""
        for index, channel in enumerate(channels):
            embed.description += f"{index + 1} - {channel.mention}\n"
        await ctx.send(embed=embed)

    @commands.command(aliases=["toggletra"])
    async def toggletyperacerannouncement(self, ctx: commands.Context):
        embed = self.games_embed(ctx)
        if not self.announce_typeracer_queue.is_running():
            self.announce_typeracer_queue.start()
            embed.description = f"Enabled typeracer queue announcement for subscribed channels."
            await ctx.send(embed=embed)
        else:
            self.announce_typeracer_queue.cancel()
            embed.description = f"Disabled typeracer queue announcement for subscribed channels."
            await ctx.send(embed=embed)

    @commands.command(aliases=["toggletrq"])
    async def toggletyperacerqueue(self, ctx: commands.Context):
        channels = typeracer_dboperations.get_all_queue_announcementchannels(self.connection)
        channels_id = []
        for channel in channels:
            channels_id.append(channel[1])
        embed = self.games_embed(ctx)
        embed.title = "Zen | Typing Race"
        if ctx.channel.id not in channels_id:
            typeracer_dboperations.insert_queue_announcement_channel(self.connection, ctx.channel.id)
            embed.description = f"Subscribed {ctx.channel.mention} to the list of typeracer queue announcement channels."
            await ctx.send(embed=embed)
        else:
            typeracer_dboperations.delete_queue_announcementchannel(self.connection, ctx.channel.id)
            embed.description = f"Unsubscribed {ctx.channel.mention} from the list of typeracer queue announcement channels."
            await ctx.send(embed=embed)

    @commands.command(brief="Typeracer leaderboard.", description="This command will display the highest typeracer players.")
    async def typeracertop(self, ctx: commands.Context):
        embed = self.games_embed(ctx)
        embed.title = "Zen | Typeracer Leaderboard"
        embed.description = ""
        members_data = typeracer_dboperations.get_leaderboard(self.connection)
        for index, member in enumerate(members_data):
            embed.description += f"{index + 1}. <@{member[1]}> - **{round(member[3])} ELO**\n"
        await ctx.send(embed=embed)

    @commands.command(aliases=["trprofile"])
    async def typeracerprofile(self, ctx: commands.Context, member: discord.Member = None):
        embed = self.games_embed(ctx)
        embed.title = "Zen | Typeracer Profile"
        if member is None:
            if typeracer_dboperations.get_rating(self.connection, ctx.author.id) != "Nope":
                member_data = typeracer_dboperations.get_rating(self.connection, ctx.author.id)[0]
                embed.set_thumbnail(url=ctx.author.avatar)
                embed.add_field(name="Player Name", value=f"**{member_data[2]}**", inline=False)
                embed.add_field(name="Rating", value=f"**{round(member_data[3])} ELO**", inline=False)
                embed.add_field(name="Matches Played / Winrate", value=f"**{member_data[6]} / {round((member_data[7] / member_data[6]) * 100)}%**", inline=False)
                embed.add_field(name="Matches Won / Drawn / Lost", value=f"**{member_data[7]} / {member_data[9]} / {member_data[8]}**", inline=False)
                embed.add_field(name="Last Match", value=f"**{member_data[10]}**", inline=False)
                return await ctx.send(embed=embed)
            embed.description = f"{ctx.author.mention} never played typeracer!"
            return await ctx.send(embed=embed)
        else:
            if typeracer_dboperations.get_rating(self.connection, member.id) != "Nope":
                member_data = typeracer_dboperations.get_rating(self.connection, member.id)[0]
                embed.set_thumbnail(url=member.avatar)
                embed.add_field(name="Player Name", value=f"**{member_data[2]}**", inline=False)
                embed.add_field(name="Rating", value=f"**{round(member_data[3])} ELO**", inline=False)
                embed.add_field(name="Matches Played / Winrate", value=f"**{member_data[6]} / {round((member_data[7] / member_data[6]) * 100)}%**", inline=False)
                embed.add_field(name="Matches Won / Drawn / Lost", value=f"**{member_data[7]} / {member_data[9]} / {member_data[8]}**", inline=False)
                embed.add_field(name="Last Match", value=f"**{member_data[10]}**", inline=False)
                return await ctx.send(embed=embed)
            embed.description = f"{member.mention} never played typeracer!"
            return await ctx.send(embed=embed)

    @commands.command()
    async def typeracerqueue(self, ctx: commands.Context):
        async def join_unrated_queue_button_callback(interaction: discord.Interaction):
            if not self.typeracer_matchmaking.is_running():
                self.typeracer_matchmaking.start()
            await interaction.response.defer()
            if interaction.user not in self.typeracer_unrated_queue and interaction.user in self.typeracer_rated_queue:
                self.typeracer_rated_queue.remove(interaction.user)
            if interaction.user not in self.typeracer_unrated_queue and interaction.user not in self.typeracer_rated_queue:
                self.typeracer_unrated_queue.insert(0, interaction.user)
            embed = interaction.message.embeds[0]
            unrated_queue = ""
            for player in self.typeracer_unrated_queue:
                rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
                unrated_queue += f"{player.mention} - **{rating}**\n"
            rated_queue = ""
            for player in self.typeracer_rated_queue:
                rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
                rated_queue += f"{player.mention} - **{rating}**\n"
            embed.set_field_at(0, name="Current Unrated Queue", value=unrated_queue, inline=True)
            embed.set_field_at(1, name="Current Rated Queue", value=rated_queue, inline=True)
            await interaction.message.edit(embed=embed, view=view)

        async def join_rated_queue_button_callback(interaction: discord.Interaction):
            if not self.typeracer_matchmaking.is_running():
                self.typeracer_matchmaking.start()
            await interaction.response.defer()
            if interaction.user not in self.typeracer_rated_queue and interaction.user in self.typeracer_unrated_queue:
                self.typeracer_unrated_queue.remove(interaction.user)
            if interaction.user not in self.typeracer_rated_queue and interaction.user not in self.typeracer_unrated_queue:
                self.typeracer_rated_queue.insert(0, interaction.user)
            embed = interaction.message.embeds[0]
            unrated_queue = ""
            for player in self.typeracer_unrated_queue:
                rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
                unrated_queue += f"{player.mention} - **{rating}**\n"
            rated_queue = ""
            for player in self.typeracer_rated_queue:
                rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
                rated_queue += f"{player.mention} - **{rating}**\n"
            embed.set_field_at(0, name="Current Unrated Queue", value=unrated_queue, inline=True)
            embed.set_field_at(1, name="Current Rated Queue", value=rated_queue, inline=True)
            await interaction.message.edit(embed=embed, view=view)

        async def leave_queue_button_callback(interaction: discord.Interaction):
            await interaction.response.defer()
            if interaction.user in self.typeracer_unrated_queue:
                self.typeracer_unrated_queue.remove(interaction.user)
            if interaction.user in self.typeracer_rated_queue:
                self.typeracer_rated_queue.remove(interaction.user)
            if interaction.user not in self.typeracer_cancel_list:
                self.typeracer_cancel_list.append(interaction.user)
            embed = interaction.message.embeds[0]
            unrated_queue = ""
            for player in self.typeracer_unrated_queue:
                rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
                unrated_queue += f"{player.mention} - **{rating}**\n"
            rated_queue = ""
            for player in self.typeracer_rated_queue:
                rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
                rated_queue += f"{player.mention} - **{rating}**\n"
            embed.set_field_at(0, name="Current Unrated Queue", value=unrated_queue, inline=True)
            embed.set_field_at(1, name="Current Rated Queue", value=rated_queue, inline=True)
            await interaction.message.edit(embed=embed, view=view)

        embed = self.games_embed(ctx)
        embed.title = "Zen | Typing Race Queue"
        unrated_queue = ""
        for player in self.typeracer_unrated_queue:
            rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
            unrated_queue += f"{player.mention} - **{rating}**\n"
        rated_queue = ""
        for player in self.typeracer_rated_queue:
            rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
            rated_queue += f"{player.mention} - **{rating}**\n"
        embed.add_field(name="Current Unrated Queue", value=unrated_queue, inline=True)
        embed.add_field(name="Current Rated Queue", value=rated_queue, inline=True)
        join_unrated_button = Button(label="Join Unrated Queue", style=discord.ButtonStyle.green)
        join_unrated_button.callback = join_unrated_queue_button_callback
        join_rated_button = Button(label="Join Rated Queue", style=discord.ButtonStyle.green)
        join_rated_button.callback = join_rated_queue_button_callback
        leave_queue_button = Button(label="Leave Queue", style=discord.ButtonStyle.red)
        leave_queue_button.callback = leave_queue_button_callback
        view = View(timeout=None)
        view.add_item(join_unrated_button)
        view.add_item(join_rated_button)
        view.add_item(leave_queue_button)
        message = await ctx.send(embed=embed, view=view)
        timer = 0
        while True:
            if timer == 300:
                return await message.delete()
            unrated_queue = ""
            for player in self.typeracer_unrated_queue:
                rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
                unrated_queue += f"{player.mention} - **{rating}**\n"
            rated_queue = ""
            for player in self.typeracer_rated_queue:
                rating = f"{round(typeracer_dboperations.get_rating(self.connection, player.id)[0][3])} ELO" if typeracer_dboperations.get_rating(self.connection, player.id) != "Nope" else "Never Played"
                rated_queue += f"{player.mention} - **{rating}**\n"
            embed.set_field_at(0, name="Current Unrated Queue", value=unrated_queue, inline=True)
            embed.set_field_at(1, name="Current Rated Queue", value=rated_queue, inline=True)
            await message.edit(embed=embed)
            await asyncio.sleep(5)
            timer += 5

    @commands.command(brief="Lets you search for a typeracer match")
    async def typeracer(self, ctx: commands.Context, matchtype: str = "unrated"):
        async def cancel_button_callback(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                return await interaction.response.defer()
            await interaction.response.defer()
            if ctx.author not in self.typeracer_cancel_list:
                self.typeracer_cancel_list.append(ctx.author)
            if ctx.author in self.typeracer_unrated_queue:
                self.typeracer_unrated_queue.remove(ctx.author)
            if ctx.author in self.typeracer_rated_queue:
                self.typeracer_rated_queue.remove(ctx.author)

        if ctx.author in self.typeracer_cancel_list:
            self.typeracer_cancel_list.remove(ctx.author)
        embed = self.games_embed(ctx)
        cancel_button = Button(label="Cancel Search", style=discord.ButtonStyle.red)
        cancel_button.callback = cancel_button_callback
        view = View(timeout=None)
        view.add_item(cancel_button)
        if ctx.author in self.typeracer_games:
            embed.description = "You are already in an ongoing typeracer match!"
            return await ctx.send(embed=embed)
        if ctx.author in self.typeracer_unrated_queue or ctx.author in self.typeracer_rated_queue:
            embed.title = "Zen | Typing Race"
            embed.description = "You are already in a queue."
            return await ctx.send(embed=embed)
        if not self.typeracer_matchmaking.is_running():
            self.typeracer_matchmaking.start()
        if matchtype not in ["unrated", "unranked", "rated", "ranked"]:
            embed.description = "Please choose a valid type of match!\n- **Rated/Ranked**\n- **Unrated/Unranked**"
            await ctx.send(embed=embed)
        if matchtype in ["unrated", "unranked"]:
            embed.title = "Zen | Typing Race (Unrated)"
            self.typeracer_unrated_queue.insert(0, ctx.author)
            embed.description = f"{ctx.author.mention} is searching for an opponent .\n{len(self.typeracer_unrated_queue)} in queue."
            message = await ctx.send(embed=embed, view=view)
            timer = 0
            while ctx.author in self.typeracer_unrated_queue:
                await asyncio.sleep(2)
                embed.description = f"{ctx.author.mention} is searching for an opponent . .\n{len(self.typeracer_unrated_queue)} in queue."
                if ctx.author not in self.typeracer_unrated_queue:
                    break
                await message.edit(embed=embed)
                await asyncio.sleep(2)
                embed.description = f"{ctx.author.mention} is searching for an opponent . . .\n{len(self.typeracer_unrated_queue)} in queue."
                if ctx.author not in self.typeracer_unrated_queue:
                    break
                await message.edit(embed=embed)
                embed.description = f"{ctx.author.mention} is searching for an opponent .\n{len(self.typeracer_unrated_queue)} in queue."
                await asyncio.sleep(2)
                if ctx.author not in self.typeracer_unrated_queue:
                    break
                await message.edit(embed=embed)
                timer += 6
                if timer > 120:
                    embed.description = "It's been two minutes, it looks like no one is playing right now. Queue up again later!"
                    if ctx.author in self.typeracer_unrated_queue:
                        self.typeracer_unrated_queue.remove(ctx.author)
                    return await message.edit(embed=embed, view=None, delete_after=30)
            if ctx.author not in self.typeracer_cancel_list:
                embed.description = f"{ctx.author.mention} found a game!"
                return await message.edit(embed=embed, view=None, delete_after=30)
            if message:
                await message.delete()
            self.typeracer_cancel_list.remove(ctx.author)
            embed.description = f"{ctx.author.mention}, your search has been cancelled!"
            await ctx.send(embed=embed, delete_after=15)
        if matchtype in ["rated", "ranked"]:
            embed.title = "Zen | Typing Race (Rated)"
            self.typeracer_rated_queue.insert(0, ctx.author)
            embed.description = f"{ctx.author.mention} is searching for an opponent .\n{len(self.typeracer_rated_queue)} in queue."
            message = await ctx.send(embed=embed, view=view)
            timer = 0
            while ctx.author in self.typeracer_rated_queue:
                if timer % 30 == 0 and timer != 0:
                    embed.description += "\n\nIncreased rating interval for search."
                    await message.edit(embed=embed)
                await asyncio.sleep(2)
                embed.description = f"{ctx.author.mention} is searching for an opponent . .\n{len(self.typeracer_rated_queue)} in queue."
                if ctx.author not in self.typeracer_rated_queue:
                    break
                await message.edit(embed=embed)
                await asyncio.sleep(2)
                embed.description = f"{ctx.author.mention} is searching for an opponent . . .\n{len(self.typeracer_rated_queue)} in queue."
                if ctx.author not in self.typeracer_rated_queue:
                    break
                await message.edit(embed=embed)
                embed.description = f"{ctx.author.mention} is searching for an opponent .\n{len(self.typeracer_rated_queue)} in queue."
                await asyncio.sleep(2)
                if ctx.author not in self.typeracer_rated_queue:
                    break
                await message.edit(embed=embed)
                timer += 6
                if timer > 120:
                    embed.description = "It's been two minutes, it looks like no one is playing right now. Queue up again later!"
                    if ctx.author in self.typeracer_rated_queue:
                        self.typeracer_rated_queue.remove(ctx.author)
                    return await message.edit(embed=embed, view=None, delete_after=30)
            if ctx.author not in self.typeracer_cancel_list:
                embed.description = f"{ctx.author.mention} found a game!"
                return await message.edit(embed=embed, view=None, delete_after=30)
            if message:
                await message.delete()
            self.typeracer_cancel_list.remove(ctx.author)
            embed.description = f"{ctx.author.mention}, your search has been cancelled!"
            await ctx.send(embed=embed, delete_after=15)

    @commands.command()
    async def typeracersolo(self, ctx: commands.Context):
        @tasks.loop(seconds=1, count=120)
        async def timer(embed, message):
            if timer.current_loop >= 110:
                if timer.current_loop == 119:
                    embed.set_field_at(0, name="Time remaining", value=f"{120 - timer.current_loop} seconds left." if timer.current_loop != 120 else "You ran out of time!", inline=False)
                    await message.edit(embed=embed)
                    await asyncio.sleep(1)
                    embed.set_field_at(0, name="Time remaining", value=f"You ran out of time!", inline=False)
                    return await message.edit(embed=embed)
                embed.set_field_at(0, name="Time remaining", value=f"{120 - timer.current_loop} seconds left." if timer.current_loop != 120 else "You ran out of time!", inline=False)
                return await message.edit(embed=embed)
            if timer.current_loop % 5 == 0:
                embed.set_field_at(0, name="Time remaining", value=f"{120 - timer.current_loop} seconds left." if timer.current_loop != 120 else "You ran out of time!", inline=False)
                await message.edit(embed=embed)
        embed = self.games_embed(ctx)
        embed.title = "Zen | Typing Race"
        if ctx.author in self.typeracer_games:
            embed.description = "You are already in an ongoing typeracer match!"
            return await ctx.send(embed=embed)
        text = brown.words()
        sentences = nltk.sent_tokenize(" ".join(text))
        random_paragraph = ""
        random_paragraph += str(random.choice(sentences))
        while len(random_paragraph) < 250:
            random_paragraph += str(random.choice(sentences))
        random_paragraph = Formatter.format_paragraph(random_paragraph)
        display_paragraph = random_paragraph.replace(" ", "\u034F ")
        words = random_paragraph.split()
        self.typeracer_games.append(ctx.author)
        embed.add_field(name="Rules", value="You have 2 minutes to type the entire paragraph. Write the entire paragraph in 1 message and only send it when you're done. Typos will add extra to your final time.\n\nThe match will start in 10 seconds!", inline=False)
        embed.add_field(name="Solo Play", value="Your practicing your typing skills alone ;-;", inline=False)
        message = await ctx.send(embed=embed)
        await asyncio.sleep(10)
        embed.set_field_at(1, name="Paragraph", value=f"```{display_paragraph}```", inline=False)
        timer.start(embed=embed, message=message)
        try:
            response: discord.Message = await self.client.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=120)
        except asyncio.TimeoutError:
            pass
        self.typeracer_games.remove(ctx.author)
        author_words = response.content.split()
        await response.delete()
        typo_count = 0
        missing_count = 0
        if timer.is_running():
            author_time = timer.current_loop
            author_score = timer.current_loop
            timer.cancel()
            if len(author_words) < len(words):
                missing_count += len(words) - len(author_words)
            for x in range(min(len(words), len(author_words))):
                if "\u034F" in response.content and x == min(len(words), len(author_words)) - 1:
                    typo_count = 42069
                    author_words.clear()
                    author_words.append(f"[{ctx.author.display_name} is a dirty cheater!]")
                    break
                if author_words[x] != words[x]:
                    if author_words[x] in words:
                        if words.index(author_words[x]) - x <= 5:
                            continue
                        else:
                            typo_count += 1
                            author_words[x] = f"[{author_words[x]}]"
                    else:
                        typo_count += 1
                        author_words[x] = f"[{author_words[x]}]"
            author_score += (typo_count * 2)
            author_score += (missing_count * 2)
            answer = ""
            for index, word in enumerate(author_words):
                if index == len(author_words) - 1:
                    answer += word
                else:
                    answer += f"{word} "
            if missing_count == 0:
                missing_count = "missed 0 word"
            elif missing_count == 1:
                missing_count = "missed 1 word"
            else:
                missing_count = f"missed {missing_count} words"
            if typo_count == 0:
                typo_count = "made 0 typo"
            elif typo_count == 1:
                typo_count = "made 1 typo"
            else:
                typo_count = f"made {typo_count} typos"
            embed.insert_field_at(1, name="Result", value=f"You finished in {author_time} seconds, {typo_count} and {missing_count}!\n\nYour final score is: {author_score}")
            embed.add_field(name="Your Text", value=f"```INI\n{answer}\n```")
            return await message.edit(embed=embed)
        embed.insert_field_at(1, name="Result", value="Your time has ran out!")
        return await message.edit(embed=embed)

    @commands.command()
    async def typeracerduel(self, ctx: commands.Context, member: discord.Member = None, matchtype: str = "unrated"):
        @tasks.loop(seconds=1, count=120)
        async def timer(embed, message):
            if timer.current_loop >= 110:
                if timer.current_loop == 119:
                    embed.set_field_at(0, name="Time remaining", value=f"{120 - timer.current_loop} seconds left." if timer.current_loop != 120 else "You ran out of time!", inline=False)
                    await message.edit(embed=embed)
                    await asyncio.sleep(1)
                    embed.set_field_at(0, name="Time remaining", value=f"You ran out of time!", inline=False)
                    return await message.edit(embed=embed)
                embed.set_field_at(0, name="Time remaining", value=f"{120 - timer.current_loop} seconds left." if timer.current_loop != 120 else "You ran out of time!", inline=False)
                return await message.edit(embed=embed)
            if timer.current_loop % 5 == 0:
                embed.set_field_at(0, name="Time remaining", value=f"{120 - timer.current_loop} seconds left." if timer.current_loop != 120 else "You ran out of time!", inline=False)
                await message.edit(embed=embed)

        @tasks.loop(count=1)
        async def wait_for_typeracer_player_1(embed: discord.Embed, player: discord.Member, words, context: commands.Context):
            response = await self.client.wait_for("message", check=lambda m: m.author == player and m.channel == context.channel, timeout=120)
            player_words = response.content.split()
            await response.delete()
            typo_count = 0
            missing_count = 0
            if timer.is_running():
                player_time = timer.current_loop
                player_score = timer.current_loop
                if len(player_words) < len(words):
                    missing_count += len(words) - len(player_words)
                for x in range(min(len(words), len(player_words))):
                    if "\u034F" in response.content:
                        typo_count = 42069
                        player_words.clear()
                        player_words.append(f"[{player.display_name} is a dirty cheater!]")
                        break
                    if player_words[x] != words[x]:
                        if player_words[x] in words:
                            if words.index(player_words[x]) - x <= 5:
                                continue
                            else:
                                typo_count += 1
                                player_words[x] = f"[{player_words[x]}]"
                        else:
                            typo_count += 1
                            player_words[x] = f"[{player_words[x]}]"
                player_score += (typo_count * 2)
                player_score += (missing_count * 2)
                answer = ""
                for index, word in enumerate(player_words):
                    if index == len(player_words) - 1:
                        answer += word
                    else:
                        answer += f"{word} "
                if missing_count == 0:
                    missing_count = "missed 0 word"
                elif missing_count == 1:
                    missing_count = "missed 1 word"
                else:
                    missing_count = f"missed {missing_count} words"
                if typo_count == 0:
                    typo_count = "made 0 typo"
                elif typo_count == 1:
                    typo_count = "made 1 typo"
                else:
                    typo_count = f"made {typo_count} typos"
                embed.add_field(name=f"{player.display_name.capitalize()}'s Result", value=f"{player.display_name.capitalize()} finished in {player_time} seconds, {typo_count} and {missing_count}!\nFinal score: {player_score}\n```INI\n{answer}\n```", inline=False)

        @tasks.loop(count=1)
        async def wait_for_typeracer_player_2(embed: discord.Embed, player: discord.Member, words, context: commands.Context):
            response = await self.client.wait_for("message", check=lambda m: m.author == player and m.channel == context.channel, timeout=120)
            player_words = response.content.split()
            await response.delete()
            typo_count = 0
            missing_count = 0
            if timer.is_running():
                player_time = timer.current_loop
                player_score = timer.current_loop
                if len(player_words) < len(words):
                    missing_count += len(words) - len(player_words)
                for x in range(min(len(words), len(player_words))):
                    if "\u034F" in response.content:
                        typo_count = 42069
                        player_words.clear()
                        player_words.append(f"[{player.display_name} is a dirty cheater!]")
                        break
                    if player_words[x] != words[x]:
                        if player_words[x] in words:
                            if words.index(player_words[x]) - x <= 5:
                                continue
                            else:
                                typo_count += 1
                                player_words[x] = f"[{player_words[x]}]"
                        else:
                            typo_count += 1
                            player_words[x] = f"[{player_words[x]}]"
                player_score += (typo_count * 2)
                player_score += (missing_count * 2)
                answer = ""
                for index, word in enumerate(player_words):
                    if index == len(player_words) - 1:
                        answer += word
                    else:
                        answer += f"{word} "
                if missing_count == 0:
                    missing_count = "missed 0 word"
                elif missing_count == 1:
                    missing_count = "missed 1 word"
                else:
                    missing_count = f"missed {missing_count} words"
                if typo_count == 0:
                    typo_count = "made 0 typo"
                elif typo_count == 1:
                    typo_count = "made 1 typo"
                else:
                    typo_count = f"made {typo_count} typos"
                embed.add_field(name=f"{player.display_name.capitalize()}'s Result", value=f"{player.display_name.capitalize()} finished in {player_time} seconds, {typo_count} and {missing_count}!\nFinal score: {player_score}\n```INI\n{answer}\n```", inline=False) 
        
        embed = self.games_embed(ctx)
        embed.title = "Zen | Typing Race"
        if member is None:
            embed.description = "Please specify the user you want to challenge!"
            return await ctx.send(embed=embed)
        if member == ctx.author:
            embed.description = "You can't challenge yourself!"
            return await ctx.send(embed=embed)
        if ctx.author in self.typeracer_games:
            embed.description = "You are already in an ongoing typeracer match!"
            return await ctx.send(embed=embed)
        if member in self.typeracer_games:
            embed.description = f"{member.mention} is already in an ongoing typeracer match!"
            return await ctx.send(embed=embed)
        if matchtype.lower() not in ["unrated", "unranked", "rated", "ranked"]:
            embed.description = "Please choose a valid type of match!\n- **Rated**\n- **Unrated**"
            return await ctx.send(embed=embed)
        matchtype = matchtype.lower()
        text = brown.words()
        sentences = nltk.sent_tokenize(" ".join(text))
        random_paragraph = ""
        random_paragraph += str(random.choice(sentences))
        while len(random_paragraph) < 250:
            random_paragraph += str(random.choice(sentences))
        random_paragraph = Formatter.format_paragraph(random_paragraph)
        display_paragraph = random_paragraph.replace(" ", "\u034F ")
        words = random_paragraph.split()
        if member in self.typeracer_challenges.keys():
            for message in self.typeracer_challenges[member]:
                if f"<@{ctx.author.id}>" in message.embeds[0].description.split():
                    embed.description = f"There is already a challenge request involving you and {member.mention}!"
                    return await ctx.send(embed=embed)
        embed.description = f"{ctx.author.mention} has challenged {member.mention} to a typing race.\nType yes to accept the challenge and no to decline."
        challenge = await ctx.send(embed=embed)
        try:
            self.typeracer_challenges[ctx.author].append(challenge)
            response = await self.client.wait_for("message", check=lambda m: m.author == member and m.content.lower() in ["yes", "y", "no", "n"], timeout=30)
            if "cancelled." in challenge.content.split():
                return
            if response.content.lower() in ["yes", "y"]:
                for message in self.typeracer_challenges[ctx.author]:
                    if message != challenge:
                        embed.description = f"The challenge has been cancelled because {ctx.author.mention} found someone else."
                        self.typeracer_challenges[ctx.author].pop()
                        await message.edit(embed=embed)
                embed.description = f"{member.mention} has accepted the challenge!"
                await ctx.send(embed=embed)
                embed = discord.Embed(title="Zen | Typing Race", color=ctx.author.color)
            if response.content.lower() in ["no", "n"]:
                embed.description = f"{member.mention} has declined the challenge!"
                return await ctx.send(embed=embed)
        except asyncio.TimeoutError:
            if challenge not in self.typeracer_challenges[ctx.author]:
                return
            embed.description = "The challenge has timed out!"
            self.typeracer_challenges[ctx.author].pop()
            return await ctx.send(embed=embed)
        self.typeracer_challenges.pop(ctx.author)
        self.typeracer_games.append(ctx.author)
        self.typeracer_games.append(member)
        embed.add_field(name="Rules", value="You have 2 minutes to type the entire paragraph. Write the entire paragraph in 1 message and only send it when you're done. Typos will add extra to your final time.\n\nThe match will start in 10 seconds!", inline=False)
        embed.add_field(name="Match Play", value=f"This is a typing contest between {ctx.author.mention} and {member.mention}.", inline=False)
        message = await ctx.send(embed=embed)
        await asyncio.sleep(10)
        embed.set_field_at(1, name="Paragraph", value=f"```{display_paragraph}```", inline=False)
        timer.start(embed=embed, message=message)
        result_embed = discord.Embed(title="Zen | Typing Race", color=ctx.author.color)
        wait_for_typeracer_player_1.start(embed=result_embed, player=ctx.author, words=words, context=ctx)
        wait_for_typeracer_player_2.start(embed=result_embed, player=member, words=words, context=ctx)
        while True:
            await asyncio.sleep(1)
            if wait_for_typeracer_player_1.is_running() and wait_for_typeracer_player_2.is_running() and not timer.is_running():
                message = Player.update_players(ctx.author, member, 0.5, matchtype)
                result_embed.add_field(name="Match Result", value=message, inline=False)
                await ctx.send(embed=result_embed)
                break
            if wait_for_typeracer_player_2.is_running() and not timer.is_running():
                message = Player.update_players(ctx.author, member, 1, matchtype)
                result_embed.add_field(name="Match Result", value=message, inline=False)
                await ctx.send(embed=result_embed)
                break
            if wait_for_typeracer_player_1.is_running() and not timer.is_running():
                message = Player.update_players(member, ctx.author, 1, matchtype)
                result_embed.add_field(name="Match Result", value=message, inline=False)
                await ctx.send(embed=result_embed)
                break
            if not wait_for_typeracer_player_1.is_running() and not wait_for_typeracer_player_2.is_running():
                timer.cancel()
                string1 = result_embed.fields[0].value
                string2 = result_embed.fields[1].value
                player1_score = re.findall(r'\d+', string1)[3]
                player1_name = re.findall(r"^\w+", string1)[0]
                player2_score = re.findall(r'\d+', string2)[3]
                player2_name = re.findall(r"^\w+", string2)[0]
                player1_discord = ctx.author if player1_name == ctx.author.display_name.capitalize() else member
                player2_discord = ctx.author if player2_name == ctx.author.display_name.capitalize() else member
                if int(player1_score) < int(player2_score):
                    message = Player.update_players(player1_discord, player2_discord, 1, matchtype)
                    result_embed.add_field(name="Match Result", value=message, inline=False)
                    await ctx.send(embed=result_embed)
                    break
                if int(player2_score) < int(player1_score):
                    message = Player.update_players(player2_discord, player1_discord, 1, matchtype)
                    result_embed.add_field(name="Match Result", value=message, inline=False)
                    await ctx.send(embed=result_embed)
                    break
                if player1_score == player2_score:
                    message = Player.update_players(player1_discord, player2_discord, 0.5, matchtype)
                    result_embed.add_field(name="Match Result", value=message, inline=False)
                    await ctx.send(embed=result_embed)
                    break
        self.typeracer_games.remove(ctx.author)
        self.typeracer_games.remove(member)

    @commands.command()
    async def battleshiptop(self, ctx: commands.Context):
        embed = self.games_embed(ctx)
        embed.title = "Zen | BattleShip Leaderboard"
        embed.description = ""
        members_data = battleship_dboperations.get_leaderboard(self.connection)
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
                player1_expected_rating = self.expected_rating(player1_rating, player2_rating)
                player2_expected_rating = self.expected_rating(player2_rating, player1_rating)
                player1_new_rating = player1_rating + 32 * (0 - player1_expected_rating)
                player2_new_rating = player2_rating + 32 * (1 - player2_expected_rating)
                battleship_dboperations.insert_rating(self.connection, ctx.author.id, ctx.author.name, round(player1_new_rating))
                battleship_dboperations.insert_rating(self.connection, member.id, member.name, round(player2_new_rating))
                await ctx.send(f"{member.mention}'s rating change: {player2_rating} -> {round(player2_new_rating)}\n{ctx.author.mention}'s rating change: {player1_rating} - > {round(player1_new_rating)}")
                return

            await member.send(f"It's {ctx.author.mention}'s turn!")
    
    @commands.command()
    async def rpstop(self, ctx: commands.Context):
        embed = self.games_embed(ctx)
        embed.title = "Zen | Rock-Paper-Scissors Leaderboard"
        embed.description = ""
        members_data = rps_dboperations.get_leaderboard(self.rps_connection)
        for index, member in enumerate(members_data):
            embed.description += f"{index + 1}. <@{member[1]}> - **{member[3]} ELO**\n"
        await ctx.send(embed=embed)

    @commands.command(aliases=["rps"], brief="Play Rock-Paper-Scissors, Best of 5", description="""This command will allow you to play a 
    Rock-Paper-Scissors match, @ a user after the command to play against them or you will be matched against the infamous Zen Bot.""")
    async def rockpaperscissors(self, ctx: commands.Context, member: discord.Member = None):
        timeOutEmbed = discord.Embed(title="Zen | Games", description="Too long! Game cancelled.")
        multiplayerMatch = False
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
            if answer.author == member and answer.content.lower() in ["y", "yes", "n", "no"] and answer.channel == ctx.channel:
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
            multiplayerMatch = True
            await ctx.send(embed=discord.Embed(title="Zen | Games", description=f"{member.mention}, You have been challenged to a game of Rock-Paper-Scissors by {player1}! Do you accept? (y/n)"), delete_after=60)
            try:
                ans = await self.client.wait_for('message', check=checkAnswer, timeout=60)
            except asyncio.TimeoutError:
                await ctx.send(embed=timeOutEmbed, delete_after=60)
                return
            if ans.content.lower() in ["y", "yes", ]:
                await ctx.send(embed=discord.Embed(title="Zen | Games", description=f"""{ans.author.name} 
                has accepted the challenge!"""), delete_after=60)
            else:
                await ctx.send(embed=discord.Embed(title="Zen | Games", description=f"""{ans.author.name}
                has declined the challenge!"""), delete_after=60)
                return

        await ctx.send(embed=discord.Embed(title="Zen | Games", description=f"Starting a game of Rock-Paper-Scissors... {player1} will be matched against {player2}. Each player will be privately messaged to get their weapon of choice."), delete_after=60)

        chooseMove = """Choose between: Rock("r"), Paper("p"), or Scissors("s")"""
        p1Points = 0
        p2Points = 0
        gameRound = 1
        finalWinner = None

        while p1Points < 2 or p2Points < 2:
            await ctx.author.send(embed=discord.Embed(title="Zen | Games", description=f"""Round {gameRound}: 
            {chooseMove}"""), delete_after=60)
            try:
                p1Input = await self.client.wait_for("message", check=checkP1Move, timeout=60)
                p1Move = playerMoves[p1Input.content.lower()]
            except asyncio.TimeoutError:
                await ctx.send(embed=timeOutEmbed, delete_after=60)
                return

            if player2 == "The Zen Bot":
                p2Move = botMoves[random.randint(1, 3)]
            else:
                await member.send(embed=discord.Embed(title="Zen | Games", description=f"""Round {gameRound}: 
                {chooseMove}"""), delete_after=60)
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
            gameRound += 1

        await ctx.send(embed=discord.Embed(title="Zen | Games", description=f"{finalWinner} wins the game! Final Score: {max(p1Points, p2Points)} - {min(p1Points, p2Points)}"), delete_after=60)
        
        if multiplayerMatch:
            player1_rating = rps_dboperations.get_rating(self.rps_connection, ctx.author.id)
            player2_rating = rps_dboperations.get_rating(self.rps_connection, member.id)
            player1_expected_rating = self.expected_rating(player1_rating, player2_rating)
            player2_expected_rating = self.expected_rating(player2_rating, player1_rating)
            if finalWinner == player1:
                player1_new_rating = round(player1_rating + 32 * (1 - player1_expected_rating))
                player2_new_rating = round(player2_rating + 32 * (0 - player2_expected_rating))
            else:
                player1_new_rating = round(player1_rating + 32 * (0 - player1_expected_rating))
                player2_new_rating = round(player2_rating + 32 * (1 - player2_expected_rating))
            rps_dboperations.insert_rating(self.rps_connection, ctx.author.id, ctx.author.name, player1_new_rating)
            rps_dboperations.insert_rating(self.rps_connection, member.id, member.name, player2_new_rating)
            await ctx.send(f"""{ctx.author.mention}'s rating change: {player1_rating} -> {player1_new_rating}\n{member.mention}'s rating change: {player2_rating} - > {player2_new_rating}""")

async def setup(client):
    await client.add_cog(Games(client))
