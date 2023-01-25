import asyncio
import datetime
import math
import os
import random
import time
import typing
import async_timeout
import discord
import wavelink
import re
from collections import defaultdict
from datetime import datetime
from typing import Union
from wavelink import LavalinkException, LoadTrackError, YouTubeTrack, YouTubeMusicTrack, YouTubePlaylist, SoundCloudTrack
from wavelink.ext import spotify
from wavelink.ext.spotify import SpotifyTrack
from discord.ext import commands, tasks
from discord import app_commands
from utils.music_utils.loop import Loop

class Track(wavelink.Track):

    __slots__ = ("requester")

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.requester: discord.Member = kwargs.get('requester', None)

class Player(wavelink.Player):

    __slots__ = ("context")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queue = asyncio.Queue()
        self.loop = Loop.NONE
        self.looped_track: Union[Track, YouTubeTrack] = None
        self.context: commands.Context = kwargs.get("context", None)
        self.track_source = YouTubeTrack

    async def do_next(self, **kwargs) -> None:
        if self.is_playing():
            return
        try:
            with async_timeout.timeout(300):
                if len(self.queue._queue) == 0 and self.loop == "NONE":
                    await self.context.send(embed=discord.Embed(description="The queue is empty! Zen will be leaving in 5 minutes unless you add more songs.", color=self.context.author.top_role.color), delete_after=305)
                if self.loop == "CURRENT":
                    track = self.looped_track
                elif self.loop == "QUEUE":
                    if kwargs.get("skip_loop") == True:
                        pass
                    else:
                        await self.queue.put(self.looped_track)
                    track = await self.queue.get()
                else:
                    track = await self.queue.get()
        except asyncio.TimeoutError:
            return await self.teardown()
        if isinstance(track, wavelink.PartialTrack):
            track: wavelink.PartialTrack
            requester = track.query
            track = await YouTubeTrack.search(query=track.title, return_first=True)
            track.requester = requester
        await self.play(track)
        if kwargs.get("position") is not None:
            await self.seek(kwargs.get("position"))
            length = track.length - (kwargs.get("position") / 1000)
            await asyncio.sleep(1)
            await self.context.send(embed=self.build_embed(is_now_playing=True), delete_after=length)
            self.looped_track = track
            return
        self.looped_track = track
        await self.context.send(embed=self.build_embed(is_now_playing=True), delete_after=track.length)

    async def set_loop(self, loop_type) -> None:
        if not self.is_playing() and self.queue.empty():
            return await self.context.send(embed=discord.Embed(description="There is no song to loop.", color=self.context.author.top_role.color), delete_after=60)

        if loop_type is None:
            if Loop.TYPES.index(self.loop) >= 2:
                loop_type = Loop.NONE
            else:
                loop_type = Loop.TYPES[Loop.TYPES.index(self.loop) + 1]

        loop_type = loop_type.upper()

        if loop_type == "OFF":
            loop_type = Loop.NONE

        self.loop = loop_type

    def build_embed(self, **kwargs) -> typing.Optional[discord.Embed]:
        def convert(seconds):
            seconds = seconds % (24 * 3600)
            hour = seconds // 3600
            seconds %= 3600
            minutes = seconds // 60
            seconds %= 60
            
            if hour == 0:
                return "%d:%02d" % (minutes, seconds)
            return "%d:%02d:%02d" % (hour, minutes, seconds)

        def music_position(position, length):
            zen = "<:zen:1061021427718950954>"
            circle = ":white_circle:"

            if position < 10 / 100 * length:
                return f"{circle*10}"
            if position < 20 / 100 * length:
                return f"{zen*1}{circle*9}"
            if position < 30 / 100 * length:
                return f"{zen*2}{circle*8}"
            if position < 40 / 100 * length:
                return f"{zen*3}{circle*7}"
            if position < 50 / 100 * length:
                return f"{zen*4}{circle*6}"
            if position < 60 / 100 * length:
                return f"{zen*5}{circle*5}"
            if position < 70 / 100 * length:
                return f"{zen*6}{circle*4}"
            if position < 80 / 100 * length:
                return f"{zen*7}{circle*3}"
            if position < 90 / 100 * length:
                return f"{zen*8}{circle*2}"
            if position < 100 / 100 * length:
                return f"{zen*9}{circle*1}"
            return f"{zen*10}"

        track = self.source

        if not track:
            return

        channel = self.client.get_channel(self.channel.id)
        queue_count: int = len(self.queue._queue)

        embed: discord.Embed
        is_now_playing = kwargs.get("is_now_playing", False)
        if is_now_playing:
            embed = discord.Embed(title=f"Zen Music | {channel.name}", colour=self.context.author.top_role.color)
            title = (track.title[:30] + '...') if len(track.title) > 50 else track.title
            embed.description = f"**Now Playing:\n`{title}`**\n\n"
            if track._search_type == "ytsearch":
                embed.set_thumbnail(url=track.thumb)
            length = convert(round(track.length))
            position = convert(round(self.position)) if convert(round(self.position)) != length else "0:00"
            now_playing_value = f"**{position} [{music_position(self.position if position != '0:00' else 0, track.length)}] {length}**"
            embed.add_field(name="Duration", value=now_playing_value, inline=False)
            embed.add_field(name="Volume", value=f"**`{self.volume}%`**")
            embed.add_field(name="Queue Length", value=f"**{queue_count}**")
            embed.add_field(name="Video URL", value=f"[Stream it!]({track.uri})")
            embed.add_field(name="Requested By", value=track.requester.mention, inline=False)

            return embed

    async def teardown(self):
        self.queue = None

        await self.context.send(embed=discord.Embed(description="I'm dipping!", color=self.context.author.top_role.color), delete_after=60)
        await super().disconnect()

class Music(commands.Cog, description="Music commands."):
    
    def __init__(self, client: commands.Bot):
        self.client = client
        self.lavalink_disconnected_players = defaultdict(list)
        self.player_volume = 10
        self.switching_node = False
        self.lavalink_server = 1
        self.return_first = True
        if not self.handle_lavalink_connection.is_running():
            self.handle_lavalink_connection.start()

    def cog_unload(self):
        self.handle_lavalink_connection.cancel()

    def music_embed(self, ctx: commands.Context) -> discord.Embed:
        embed = discord.Embed(title="Zen | Music", color=ctx.author.color, timestamp=datetime.now())
        return embed

    def convert(self, seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        if hour == 0:
            return "%d:%02d" % (minutes, seconds)
        return "%d:%02d:%02d" % (hour, minutes, seconds)

    def get_nodes(self):
        return sorted(wavelink.NodePool._nodes.values(), key=lambda n: len(n.players))

    async def cog_command_error(self, ctx: commands.Context, error: str):
        embed = self.music_embed(ctx)
        if isinstance(error, Exception):
            embed.description = str(error)
            return await ctx.send(embed=embed)

    async def create_wavelink_node(self):
            if self.lavalink_server not in [1, 2, 3, 4, 5]:
                self.lavalink_server = 1
            while True:
                try:
                    await self.client.wait_until_ready()
                    with async_timeout.timeout(5): 
                        await wavelink.NodePool.create_node(
                        bot=self.client,
                        host=os.getenv(f"HOST{self.lavalink_server}"),
                        port=os.getenv(f"PORT{self.lavalink_server}"),
                        password=os.getenv(f"PASSWORD{self.lavalink_server}"),
                        https=True if os.getenv(f"SSL{self.lavalink_server}") == "True" else False,
                        identifier=f"Zen #{self.lavalink_server}",
                        spotify_client=spotify.SpotifyClient(client_id=os.getenv("SPOTIFY_CLIENT_ID"), client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")))
                    if len(self.get_nodes()) > 0:
                        break
                except asyncio.TimeoutError:
                    print(f"Timed out creating node: Zen#{self.lavalink_server}")
                    await self.get_nodes()[0].disconnect()
                    if self.lavalink_server == 5:
                        self.lavalink_server = 1
                    else:
                        self.lavalink_server += 1

    async def play_track(self, ctx: commands.Context, query: str):
        player: Player = ctx.voice_client
        player.context = ctx
        track_source = player.track_source

        if ctx.author.voice.channel.id != player.channel.id:
            return ctx.send(embed=discord.Embed(description="You must be in the same voice channel as the music player.", color=ctx.author.color), delete_after=60)

        query = query.strip("<>")

        if track_source == YouTubeTrack and "youtube.com/playlist" in query:
            track_source = YouTubePlaylist

        if "spotify.com" in query:
            track_source = SpotifyTrack

        if "soundcloud.com" in query:
            track_source = SoundCloudTrack

        node = self.get_nodes()[0]
        tracks = list()
        embed = discord.Embed(description=f"Searching for `{query}`", color=ctx.author.color)
        message = await ctx.send(embed=embed)

        try:
            with async_timeout.timeout(60):
                if track_source == YouTubeTrack:
                    tracks = await YouTubeTrack.search(query=query, node=node)
                elif track_source == YouTubePlaylist:
                    tracks = await YouTubePlaylist.search(query=query, node=node)
                elif track_source == SpotifyTrack and "spotify.com/playlist" in query:
                    embed.description = "Adding Spotify Playlist..."
                    await message.edit(embed=embed)
                    async for track in SpotifyTrack.iterator(query=query, node=node, partial_tracks=True):
                        tracks.append(track)
                elif track_source == SpotifyTrack and "spotify.com/album" in query:
                    embed.description = "Adding Spotify Album..."
                    await message.edit(embed=embed)
                    async for track in spotify.SpotifyTrack.iterator(query=query, type=spotify.SpotifySearchType.album, partial_tracks=True):
                        tracks.append(track)
                elif track_source == SpotifyTrack:
                    tracks = await SpotifyTrack.search(query=query, node=node)
                else:
                    query = query.split("/")
                    query = query[-1]
                    tracks = await SoundCloudTrack.search(query=query, node=node)
        except asyncio.TimeoutError:
            print("Music player search timed out!")
        except (LavalinkException, LoadTrackError):
            pass
        
        if not tracks:
            embed.description = "No song found!"
            await message.delete()
            return await ctx.send(embed=embed, delete_after=60)
            
        if isinstance(tracks, list) and "spotify.com/playlist" in query or "spotify.com/album" in query:
            for track in tracks:
                track.query = ctx.author
                await player.queue.put(track)
            type = "playlist" if "playlist" in query else "album"
            embed.description = f"Added the spotify {type}, with `{len(tracks)}` songs, to the queue."
            await message.delete()
            message = await ctx.send(embed=embed)

        elif isinstance(tracks, list) and track_source == YouTubeTrack:
            track = tracks[0]
            track.requester = ctx.author
            await player.queue.put(track)

            embed.description = f"Added `{track.title}` to the queue."
            await message.delete()
            message = await ctx.send(embed=embed)

        elif isinstance(tracks, YouTubePlaylist):
            if "index" in query:
                index = re.search("([^=]+$)", query)
                track: Union[Track, YouTubeTrack] = tracks.tracks[int(index.group()) - 1]
                track.requester = ctx.author
                await player.queue.put(track)
                embed.description = f"Added `{track.title}` to the queue."

                await message.delete()
                message = await ctx.send(embed=embed)
            else:
                playlist = tracks.tracks
                for track in playlist:
                    track.requester = ctx.author
                    await player.queue.put(track)

                embed.description = f"Added the playlist `{tracks.name}`, with `{len(tracks.tracks)}` songs, to the queue."
                await message.delete()
                message = await ctx.send(embed=embed)

        else:
            track = tracks[0]
            track.requester = ctx.author
            await player.queue.put(track)

            embed.description = f"Added `{track.title}` to the queue."

            await message.delete()
            message = await ctx.send(embed=embed)

        if not player.is_playing():
            await asyncio.sleep(1)
            await player.do_next()       

    @tasks.loop(seconds=5)
    async def handle_lavalink_connection(self):
        nodes = self.get_nodes()
        if len(nodes) < 1:
            await self.create_wavelink_node()
        for node in nodes:
            if not node.is_connected() or self.switching_node:
                for guild in self.client.guilds:
                    player = node.get_player(guild)
                    if player is not None and player.is_playing():
                        current_track: Union[Track, YouTubeTrack] = player.source
                        position = player.position
                        new_queue = asyncio.Queue()
                        new_queue.put_nowait(current_track)
                        for track in player.queue._queue:
                            new_queue.put_nowait(track)
                        self.lavalink_disconnected_players[guild].append(player)
                        self.lavalink_disconnected_players[guild].append(new_queue)
                        self.lavalink_disconnected_players[guild].append(position)
                        embed = self.music_embed(player.context)
                        embed.description = "Oops, it looks like we've lost connection. Zen Music will try to reconnect as soon as possible!"
                        await player.context.send(embed=embed, delete_after=30)
                        await player.disconnect()
                self.switching_node = False
                return await node.disconnect()
            if node.is_connected():
                for guild in self.client.guilds:
                    player = node.get_player(guild)
                    if player is not None and len(player.channel.members) == 1:
                        embed = self.music_embed(player.context)
                        embed.description = "I'm alone ;-;\nGuess it's time to go!"
                        await player.context.send(embed=embed)
                        await asyncio.sleep(1)
                        await player.disconnect()
                    if guild in self.lavalink_disconnected_players.keys():
                        player_info = self.lavalink_disconnected_players.pop(guild)
                        player: Player = player_info[0]
                        queue: asyncio.Queue() = player_info[1]
                        track_position: int = player_info[2]
                        channel: discord.VoiceChannel = player.channel
                        new_player: Player = await channel.connect(cls=Player, self_deaf=True)
                        new_player.context = player.context
                        new_player.queue = queue
                        new_player.looped_track = player.looped_track
                        new_player.loop = player.loop
                        await new_player.set_volume(self.player_volume)
                        await new_player.do_next(position=track_position*1000, skip_loop=True)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music module has been loaded.")
        self.handle_lavalink_connection.start()

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"Node: {node.identifier} is ready!")

    @commands.Cog.listener()
    async def on_wavelink_websocket_closed(self, player: Player, reason, code):
        print(f"Lavalink closed node: {player.node.identifier}\nReason: {reason}\nCode: {code}")
        self.switching_node = True

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: Player, track: Union[Track, YouTubeTrack]):
        print(f"'{player.guild.name}' is now playing: {track.title}")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: Player, track: YouTubeTrack, reason):
        print(f"'{player.guild.name}' {reason.lower()}: {track.title}")
        await player.do_next()
    
    @commands.Cog.listener()
    async def on_wavelink_track_stuck(self, player: Player, track: YouTubeTrack, threshold):
        print(f"'{player.guild.name}' encountered Track Stuck\nTitle: {track.title}\nThreshold: {threshold}")
    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, player: Player, track: YouTubeTrack, error):
        print(f"'{player.guild.name}' encountered Track Exception\nTitle: {track.title}\nError: {error}")

    @commands.command(brief="Displays which node is currently connected to Lavalink **(Staff)**.", description="This command will dispay the node that is currently connected to Lavalink.")
    @commands.has_permissions(ban_members=True)
    async def node(self, ctx: commands.Context):
        if self.get_nodes():
            node : wavelink.Node = self.get_nodes()[0]
            return await ctx.send(embed=discord.Embed(description=f"Currently on node: {node.identifier}", color=ctx.author.color))
        await ctx.send(embed=discord.Embed(description="There is currently no connected node!", color=ctx.author.color))
    
    @commands.command(aliases=["changenode", "nodeswitch", "destroynode"], brief="Switch to the specified node or the next node **(Staff)**", description="This command will disconnect the current node and switch to the one you specified, or the very next one if no node was specified.")
    @commands.has_permissions(ban_members=True)
    async def switchnode(self, ctx: commands.Context, node_number: int = None):
        if self.get_nodes():
            node: wavelink.Node = self.get_nodes()[0]
            self.switching_node = True
            if node_number is None:
                if self.lavalink_server == 5:
                    self.lavalink_server = 1
                else:
                    self.lavalink_server += 1
            else:
                self.lavalink_server = node_number
            return await ctx.send(embed=discord.Embed(description=f"Disconnected node: {node.identifier}", color=ctx.author.color), delete_after=60)
        await ctx.send(embed=discord.Embed(description="There is currently no node to disconnect!", color=ctx.author.color))

    @commands.command(brief="Lets you seek to a given position in the track.", description="This command will let you seek to a given position in the currently playing track.")
    async def seek(self, ctx: commands.Context, seconds: str):
        player: Player = ctx.voice_client
        if player is None:
            return await ctx.send(embed=discord.Embed(description="I'm not connected to any voice channel!", color=ctx.author.color), delete_after=60)
        if ":" in seconds:
            hour_minute_second = seconds.split(":")
            if len(hour_minute_second) > 3:
                return await ctx.send(embed=discord.Embed(description=f"The position you're trying to seek to doesn't exist in the track!", color=ctx.author.color), delete_after=60)
            minutes = int(hour_minute_second[-2])
            seconds = int(hour_minute_second[-1])
            seconds: int = (60 * minutes) + seconds
            if len(hour_minute_second) == 3:
                hours = int(hour_minute_second[-3])
                seconds += (3600 * hours)
            seconds = str(seconds)
        if seconds.isdigit():
            seconds = int(seconds)
        if 0 <= seconds < player.source.length:
            await player.seek(seconds*1000)
            return await ctx.send(embed=discord.Embed(description=f"Seeked to position **{self.convert(seconds)}** in `{player.source.title}`", color=ctx.author.color), delete_after=60)
        await ctx.send(embed=discord.Embed(description=f"The position you're trying to seek to doesn't exist in the track!", color=ctx.author.color), delete_after=60)

    @commands.command(aliases=["join"], brief='Connects the bot to your channel.', description=f'This command will connect the bot to the channel you are in.')
    async def connect(self, ctx: commands.Context):
        embed = self.music_embed(ctx)
        if not ctx.author.voice:
            embed.description = "You need to be in a voice channel!"
            return await ctx.send(embed=embed)
        if not ctx.voice_client:
            embed.description = f"Connected to {ctx.author.voice.channel.mention}!"
            player: Player = await ctx.author.voice.channel.connect(cls=Player, self_deaf=True)
            await ctx.send(embed=embed)
            return await player.set_volume(self.player_volume)
        if ctx.author.voice.channel != ctx.voice_client.channel:
            embed.description = "I'm already in a different voice channel!"
            return await ctx.send(embed=embed)

    @commands.command(aliases=['leave'], brief='Disconnects the bot from your channel.', description='This command will disconnect the bot from the channel you are in.')
    async def disconnect(self, ctx: commands.Context):
        player: Player = ctx.voice_client
        if player is None:
            return await ctx.send(embed=discord.Embed(description="I'm not connected to any voice channel!", color=ctx.author.color), delete_after=60)
        await player.disconnect()
        return await ctx.send(embed=discord.Embed(description="I'm dipping!", color=ctx.author.color), delete_after=60)

    @commands.command(aliases=['p'], brief='Plays music.', description='This command will play the music you chose.')
    async def play(self, ctx: commands.Context, *, query: str):
        embed = self.music_embed(ctx)
        if not ctx.author.voice:
            embed.description = "You need to be in a voice channel!"
            return await ctx.send(embed=embed)
        if not ctx.voice_client:
            player: Player = await ctx.author.voice.channel.connect(cls=Player, self_deaf=True)
            await player.set_volume(self.player_volume)
        if ctx.author.voice.channel != ctx.voice_client.channel:
            embed.description = "I'm in a different voice channel!"
            return await ctx.send(embed=embed)
        await self.play_track(ctx, query)

    @commands.command(aliases=['np'], brief='Shows the current playing song.', description='This command will display the currently playing song.')
    async def nowplaying(self, ctx: commands.Context):
        player: Player = ctx.voice_client
        if player is None:
            return await ctx.send(embed=discord.Embed(description="I'm not connected to any voice channel!", color=ctx.author.color), delete_after=60)
        if player.is_playing():
            return await ctx.send(embed=player.build_embed(is_now_playing=True), delete_after=60)
        await ctx.send(embed=discord.Embed(description="Nothing is playing!", color=ctx.author.color), delete_after=60)

    @commands.command(brief='Skips the current music.', description='This command will skip the current music.')
    async def skip(self, ctx: commands.Context):
        player: Player = ctx.voice_client
        if player is None:
            return await ctx.send(embed=discord.Embed(description="I'm not connected to any voice channel!", color=ctx.author.color), delete_after=60)
        if player.is_playing():
            await ctx.send(embed=discord.Embed(description=f"Skipped `{player.source}`.", color=ctx.author.top_role.color), delete_after=60)
            return await player.stop()
        await ctx.send(embed=discord.Embed(description="Nothing is currently playing!", color=ctx.author.top_role.color), delete_after=60)

    @commands.command(brief='Removes a song.', description='This command will remove a song in the queue.')
    async def remove(self, ctx: commands.Context, index: int = None):
        player: Player = ctx.voice_client
        if player is None:
            return await ctx.send(embed=discord.Embed(description="I'm not connected to any voice channel!", color=ctx.author.color), delete_after=60)
        if index is None:
            index = player.queue.qsize()
        if 0 < index <= player.queue.qsize():
            await ctx.send(embed=discord.Embed(description=f"Removed `{player.queue._queue[index - 1].title}` from the queue."), delete_after=60)
            del player.queue._queue[index - 1]
            return
        await ctx.send(embed=discord.Embed(description="The song you're trying to remove doesn't exist!"), delete_after=60)

    @commands.command(aliases=['mv', 'swap'], brief='Swaps two songs in the queue.', description='This command will swap the order of two specified songs in the queue.\nIf no second song is specified, your song will be swapped with the next song in the queue.')
    async def move(self, ctx: commands.Context, first_index: int = None, second_index: int = None):
        player: Player = ctx.voice_client
        if player is None:
            return await ctx.send(embed=discord.Embed(description="I'm not connected to any voice channel!", color=ctx.author.color), delete_after=60)
        if first_index is None and second_index is None:
            return await ctx.send(embed=discord.Embed(description="Please specify two songs!", color=ctx.author.color), delete_after=60)
        if not player.queue.qsize() < (first_index and second_index) < player.queue.qsize():
            first_song: Union[Track, YouTubeTrack] = player.queue._queue[first_index - 1]
            second_song: Union[Track, YouTubeTrack] = player.queue._queue[second_index - 1]
            del player.queue._queue[first_index - 1]
            player.queue._queue.insert(first_index - 1, second_song)
            del player.queue._queue[second_index - 1]
            player.queue._queue.insert(second_index - 1, first_song)
            return await ctx.send(embed=discord.Embed(description=f"Swapped `{first_song.title}` and `{second_song.title}`", color=ctx.author.top_role.color), delete_after=60)
        await ctx.send(embed=discord.Embed(description=f"One of the songs you specified doesn't exist!", color=ctx.author.top_role.color), delete_after=60)

    @commands.command(brief="Lets you check if the track you specified is already in the queue or not.", description="This command will let tell you if the track you specified is already in the queue or not. If it is in the queue it will display the position of the track in the queue.")
    async def find(self, ctx: commands.Context, *, query: str):
        player: Player = ctx.voice_client
        if player is None:
            return await ctx.send(embed=discord.Embed(description="I'm not connected to any voice channel!", color=ctx.author.color), delete_after=60)
        query = query.strip("<>")
        track_to_find = await YouTubeTrack.search(query=query, node=player.node, return_first=True)
        for index, track in enumerate(player.queue._queue):
            if isinstance(track, wavelink.PartialTrack):
                track = await YouTubeTrack.search(query=f"{track.title}", node=player.node, return_first=True)
            if track.title == track_to_find.title:
                return await ctx.send(embed=discord.Embed(description=f"`{track.title}` is in the queue at position `{index + 1}`.", color=ctx.author.top_role.color), delete_after=60)
            if query in track.title.lower():
                return await ctx.send(embed=discord.Embed(description=f"`{query}` is in the queue at position `{index + 1}`.", color=ctx.author.top_role.color), delete_after=60)
        await ctx.send(embed=discord.Embed(description=f"`{track_to_find.title}` isn't in the queue.", color=ctx.author.top_role.color), delete_after=60)
    
    @commands.command(aliases=['random'], brief='Shuffles the queue.', description='This command will shuffle the queue.')
    async def shuffle(self, ctx: commands.Context):
        player: Player = ctx.voice_client
        if player is None:
            return await ctx.send(embed=discord.Embed(description="I'm not connected to any voice channel!", color=ctx.author.color), delete_after=60)
        if player.queue.qsize() > 1:
            random.shuffle(player.queue._queue)
            await ctx.send(embed=discord.Embed(description="The queue has been shuffled!", color=ctx.author.top_role.color), delete_after=60)
        await ctx.send(embed=discord.Embed(description="You need at least two songs in the queue to be able to use this command!", color=ctx.author.top_role.color), delete_after=60)

    @commands.command(aliases=["repeat"], brief="Loops the current playing song", description="This command will loop the song that is currently playing.")
    async def loop(self, ctx: commands.Context, loop_type: str = None):
        player: Player = ctx.voice_client
        if player is None:
            return await ctx.send(embed=discord.Embed(description="I'm not connected to any voice channel!", color=ctx.author.color), delete_after=60)
        if loop_type is not None:
            if loop_type.lower() not in ["none", "current", "queue", "off"]:
                return await ctx.send(embed=discord.Embed(description="The loop type can only be `None/Off`, `Current`, or `Queue`"))
        
        await player.set_loop(loop_type)
        await ctx.send(embed=discord.Embed(description=f"Loop has been set to `{player.loop.capitalize()}`.", color=ctx.author.top_role.color))

    @commands.command(aliases=['cq', 'clearq', 'clearqueue', 'qc', 'qclear'], brief='Clears the queue.', description='This command will clear the queue.')
    async def queueclear(self, ctx: commands.Context):
        player: Player = ctx.voice_client
        if player is None:
            return await ctx.send(embed=discord.Embed(description="I'm not connected to any voice channel!", color=ctx.author.color), delete_after=60)
        if player.queue.qsize() == 0:
            return await ctx.send(embed=discord.Embed(description="The queue is already empty!", color=ctx.author.top_role.color), delete_after=60)

        for _ in range(player.queue.qsize()):
            player.queue.get_nowait()
            player.queue.task_done()
        await ctx.send(embed=discord.Embed(description="Queue has been cleared!", color=ctx.author.top_role.color), delete_after=60)

    @commands.command(aliases=['v', 'vol'], brief='Changes the volume of the player.', description='This command will change the volume of the music player.\nThe music player allows a volume ranging from 1% to 100%.')
    async def volume(self, ctx : commands.Context, *, vol: int):
        """Change the players volume, between 1 and 100."""
        player: Player = ctx.voice_client
        if player is None:
            return await ctx.send(embed=discord.Embed(description="I'm not connected to any voice channel!", color=ctx.author.color), delete_after=60)
        if not player.is_connected():
            return

        if not 0 < vol < 101:
            return await ctx.send('Please enter a value between 1 and 100.')

        await player.set_volume(vol)
        await ctx.send(f'Set the volume to **{vol}**%', delete_after=10)

    @commands.command(aliases=["q"], brief='Displays the queue.', description='This command will display the queue.')
    async def queue(self, ctx: commands.Context, page: int = 1):
        player: Player = ctx.voice_client
        if player is None:
            return await ctx.send(embed=discord.Embed(description="I'm not connected to any voice channel!", color=ctx.author.color), delete_after=60)
        if player.queue.qsize() == 0 and not player.is_playing():
            return await ctx.send(embed=discord.Embed(description="The queue is empty!", color=ctx.author.top_role.color), delete_after=60)
        track: Union[Track, YouTubeTrack] = player.source
        counter = 0
        total_page = 1
        display = f'```SML\nCurrently Playing: {track.title}\nQueue Length: {len(player.queue._queue)}\nLoop: {player.loop.lower().capitalize()}\nUpcoming Songs ⇓\n\n'
        entries = [track.title for track in player.queue._queue]
        if len(player.queue._queue) <= 15:
            if page > total_page:
                return await ctx.send(f'There is only {total_page} page.')
            for song in entries:
                counter += 1
                display += f'{counter}: {song}\n'
            display += f'\nPage {page}/{total_page}'

        else:
            total_page = math.ceil(len(player.queue._queue) / 15)
            start_page = (page - 1) * 15
            is_more_than_one = False
            if page > total_page:
                return await ctx.send(f'There are only {total_page} pages.')
            for song in entries:
                counter += 1
                if len(song) > 50:
                    title = song[:50] + '...'
                else:
                    title = song
                display += f'{counter}: {title}\n'
                if counter % 15 == 0 and counter == start_page and total_page > 1 and page != 1:
                    is_more_than_one = True
                    display = f'```SML\nCurrently Playing: {track.title}\n\nLoop: {player.loop.lower().capitalize()}\nUpcoming Songs ⇓\n\n'
                    continue
                if counter % 15 == 0 and page == 1:
                    break
                if counter % 15 == 0 and is_more_than_one == True:
                    break
            display += f'\nPage {page}/{total_page}'
                
        display += '```'
        await ctx.send(f'{display}')

async def setup(client):
    await client.add_cog(Music(client))