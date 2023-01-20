import asyncio
import datetime
import math
import os
import random
import typing
import async_timeout
import discord
import wavelink
import re
from datetime import datetime, timedelta
from typing import Union
from wavelink import LavalinkException, LoadTrackError, YouTubeTrack, YouTubeMusicTrack, YouTubePlaylist, SoundCloudTrack
from discord.ext import commands
from discord import app_commands
from utils.music_utils.source import Source
from utils.music_utils.loop import Loop
from dotenv import load_dotenv

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
        self.track_source = "yt"

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
                    await self.queue.put(self.looped_track)
                    track = await self.queue.get()
                else:
                    track = await self.queue.get()
        except asyncio.TimeoutError:
            return await self.teardown()
        await self.play(track)
        self.looped_track = track
        await self.context.send(embed=self.build_embed(is_now_playing=True), delete_after=track.length)

    async def set_loop(self, loop_type: str) -> None:
        if not self.is_playing():
            await self.context.send(embed=discord.Embed(description="There is no song to loop.", color=self.context.author.top_role.color), delete_after=60)

        if not loop_type:
            if Loop.TYPES.index(self.loop) >= 2:
                loop_type = "NONE"
            else:
                loop_type = Loop.TYPES[Loop.TYPES.index(self.loop) + 1]
            
            if loop_type == "QUEUE" and len(self.queue._queue) < 1:
                loop_type = "NONE"
        if loop_type.upper() == "QUEUE" and len(self.queue._queue) < 1:
            await self.context.send(embed=discord.Embed(description="There must be at least 2 songs in the queue if you want to loop the queue!"))

        self.loop = loop_type.upper()
        return self.loop

    def build_embed(self, **kwargs) -> typing.Optional[discord.Embed]:
        track: Union[Track, YouTubeTrack] = self.source

        if not track:
            return

        channel = self.client.get_channel(self.channel.id)
        queue_count: int = len(self.queue._queue)

        embed: discord.Embed
        is_now_playing = kwargs.get('is_now_playing', False)
        if is_now_playing:
            embed = discord.Embed(title=f'Zen Music | {channel.name}', colour=self.context.author.top_role.color)
            title = (track.title[:30] + '...') if len(track.title) > 50 else track.title
            embed.description = f'**Now Playing:\n`{title}`**\n\n'
            embed.set_thumbnail(url=track.thumb)
            embed.add_field(name='Volume', value=f'**`{self.volume}%`**')
            embed.add_field(name='Duration', value=str(timedelta(seconds=round(track.length))))
            embed.add_field(name='Queue Length', value=str(queue_count))
            embed.add_field(name='Video URL', value=f'[Zen has prepared a link!]({track.uri})')
            embed.add_field(name='Requested By', value=track.requester.mention)

            return embed

    async def teardown(self):
        self.queue = None

        await self.context.send(embed=discord.Embed(description="I'm dipping!", color=self.context.author.top_role.color), delete_after=60)
        await super().disconnect()

class Music(commands.Cog, description="Music commands."):
    
    def __init__(self, client: commands.Bot):
        self.client = client

    def music_embed(self, ctx: commands.Context) -> discord.Embed:
        embed = discord.Embed(title="Zen | Music", color=ctx.author.color, timestamp=datetime.now())
        return embed

    async def cog_command_error(self, ctx: commands.Context, error: str):
        embed = self.music_embed(ctx)
        if isinstance(error, Exception):
            embed.description = str(error).capitalize()
            return await ctx.send(embed=embed)

    async def start_nodes(self):
        await self.client.wait_until_ready()

        load_dotenv()

        await wavelink.NodePool.create_node(
            bot=self.client,
            host=os.getenv("HOST"),
            port=os.getenv("PORT"),
            password=os.getenv("PASSWORD"),
            https=os.getenv("SSL"),
            identifier="Zen")

    def get_nodes(self):
        return sorted(wavelink.NodePool._nodes.values(), key=lambda n: len(n.players))

    async def play_track(self, ctx: commands.Context, query: str, source=None):
        player: Player = ctx.voice_client
        player.context = ctx

        await player.set_volume(10)

        if ctx.author.voice.channel.id != player.channel.id:
            ctx.send("You must be in the same voice channel as the music player.")

        track_sources = {
            "yt": YouTubeTrack,
            "ytplaylist": YouTubePlaylist,
            "ytmusic": YouTubeMusicTrack,
            "soundcloud": SoundCloudTrack
        }

        query = query.strip("<>")

        track_source = source if source else player.track_source

        embed: discord.Embed
        embed = discord.Embed(description= f"Searching for `{query}`", color=ctx.author.top_role.color)

        message = await ctx.send(embed=embed)

        if track_source == "yt" and "playlist" in query:
            source = "ytplaylist"

        source: Source = (
            track_sources.get(source)
            if source else track_sources.get(player.track_source)
        )

        nodes = self.get_nodes()
        tracks = list()

        for node in nodes:
            try:
                with async_timeout.timeout(20):
                    tracks = await source.search(query, node=node)
                    break
            except asyncio.TimeoutError:
                wavelink.NodePool._nodes.pop(node.identifier)
                continue
            except (LavalinkException, LoadTrackError):
                continue

        if not tracks:
            embed.description = "No song found!"
            await message.delete()
            return await ctx.send(embed=embed, delete_after=60)
            
        if isinstance(tracks, YouTubePlaylist):
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
            track: Union[Track, YouTubeTrack] = tracks[0]
            track.requester = ctx.author
            await player.queue.put(track)

            embed.description = f"Added `{track.title}` to the queue."

            await message.delete()
            message = await ctx.send(embed=embed)

        if not player.is_playing():
            await player.do_next()       

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music module has been loaded.")
        self.client.loop.create_task(self.start_nodes())
    
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"Node: {node.identifier} is ready!")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: Player, track: Union[Track, YouTubeTrack]):
        print(f"'{player.guild.name}' is now playing: {track.title}")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: Player, track: YouTubeTrack, reason):
        await player.do_next()
    
    @commands.Cog.listener()
    async def on_wavelink_track_stuck(self, player: Player, track: YouTubeTrack, threshold):
        await player.do_next()

    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, player: Player, track: YouTubeTrack, error):
        await player.do_next()

    @commands.command(aliases=["join"], brief='Connects the bot to your channel.', description=f'This command will connect the bot to the channel you are in.')
    async def connect(self, ctx: commands.Context):
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel!")
        if not ctx.voice_client:
            player: Player = await ctx.author.voice.channel.connect(cls=Player, reconnect=True)
        else:
            player: Player = ctx.voice_client

    @commands.command(aliases=['leave'], brief='Disconnects the bot from your channel.', description='This command will disconnect the bot from the channel you are in.')
    async def disconnect(self, ctx: commands.Context):
        player: Player = ctx.voice_client()

        player.teardown()
        await ctx.voice_client.disconnect()

    @commands.command(aliases=['p'], brief='Plays music.', description='This command will play the music you chose.')
    async def play(self, ctx: commands.Context, *, query: str):
        await ctx.invoke(self.connect)
        await self.play_track(ctx, query)

    @commands.command(aliases=['np'], brief='Shows the current playing song.', description='This command will display the currently playing song.')
    async def nowplaying(self, ctx: commands.Context):
        player: Player = ctx.voice_client
        await ctx.send(embed=player.build_embed(is_now_playing=True), delete_after=60)

    @commands.command(brief='Skips the current music.', description='This command will skip the current music.')
    async def skip(self, ctx: commands.Context):
        player: Player = ctx.voice_client

        await ctx.send(embed=discord.Embed(description=f"Skipped `{player.source}`.", color=ctx.author.top_role.color), delete_after=60)
        await player.stop()

    @commands.command(brief='Removes a song.', description='This command will remove a song in the queue.')
    async def remove(self, ctx: commands.Context, index: int):
        player: Player = ctx.voice_client

        await ctx.send(embed=discord.Embed(description=f"Removed `{player.queue._queue[index - 1].title}` from the queue."), delete_after=60)
        del player.queue._queue[index - 1]

    @commands.command(aliases=['mv', 'swap'], brief='Swaps two songs in the queue.', description='This command will swap the order of two specified songs in the queue.\nIf no second song is specified, your song will be swapped with the next song in the queue.')
    async def move(self, ctx: commands.Context, first_index: int, second_index: int):
        player: Player = ctx.voice_client

        first_song: Union[Track, YouTubeTrack] = player.queue._queue[first_index - 1]
        second_song: Union[Track, YouTubeTrack] = player.queue._queue[second_index - 1]

        del player.queue._queue[first_index - 1]
        player.queue._queue.insert(first_index - 1, second_song)
        del player.queue._queue[second_index - 1]
        player.queue._queue.insert(second_index - 1, first_song)

        await ctx.send(embed=discord.Embed(description=f"Swapped `{first_song.title}` and `{second_song.title}`", color=ctx.author.top_role.color), delete_after=60)

    @commands.command(aliases=['random'], brief='Shuffles the queue.', description='This command will shuffle the queue.')
    async def shuffle(self, ctx: commands.Context):
        player: Player = ctx.voice_client
        random.shuffle(player.queue._queue)

        await ctx.send(embed=discord.Embed(description="The queue has been shuffled!", color=ctx.author.top_role.color), delete_after=60)

    @commands.command(aliases=["repeat"], brief="Loops the current playing song", description="This command will loop the song that is currently playing.")
    async def loop(self, ctx: commands.Context, loop_type: str = None):
        player: Player = ctx.voice_client

        if loop_type.lower() not in ["none", "current", "queue"]:
            return await ctx.send(embed=discord.Embed(description="The loop type can only be `None`, `Current`, or `Queue`"))

        result = await player.set_loop(loop_type)
        await ctx.send(embed=discord.Embed(description=f"Loop has been set to {result.lower()}.", color=ctx.author.top_role.color))

    @commands.command(aliases=['cq', 'clearq', 'clearqueue', 'qc', 'qclear'], brief='Clears the queue.', description='This command will clear the queue.')
    async def queueclear(self, ctx: commands.Context):
        player: Player = ctx.voice_client

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

        if not player.is_connected():
            return

        if not 0 < vol < 101:
            return await ctx.send('Please enter a value between 1 and 100.')

        await player.set_volume(vol)
        await ctx.send(f'Set the volume to **{vol}**%', delete_after=10)

    @commands.command(aliases=["q"], brief='Displays the queue.', description='This command will display the queue.')
    async def queue(self, ctx: commands.Context, page: int = 1):
        player: Player = ctx.voice_client
        if not player.is_connected():
            return await ctx.send('Bruh I aint even there...')
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