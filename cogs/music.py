import asyncio
import random
import async_timeout
import discord
import wavelink
from wavelink import LavalinkException, LoadTrackError, YouTubeTrack, YouTubeMusicTrack, YouTubePlaylist, SoundCloudTrack
from discord.ext import commands
from discord import app_commands
from music_utils.source import Source

class Player(wavelink.Player):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.track_source = "yt"

    async def do_next(self, **kwargs) -> None:
        if self.is_playing():
            return
        try:
            with async_timeout.timeout(300):
                track = self.queue.get()
        except asyncio.TimeoutError:
            return await self.teardown()
        await self.play(track)

    async def teardown(self):
        try:
            await self.teardown()
        except KeyError:
            pass

class Music(commands.Cog, description="Music commands."):
    
    def __init__(self, client: commands.Bot):
        self.client = client

    async def start_nodes(self):
        await self.client.wait_until_ready()

        await wavelink.NodePool.create_node(
            bot=self.client,
            host="localhost",
            port=8079,
            password="zen")

    def get_nodes(self):
        return sorted(wavelink.NodePool._nodes.values(), key=lambda n: len(n.players))

    async def play_track(self, ctx: commands.Context, query: str, source=None):
        player: Player = ctx.voice_client

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
        message = await ctx.send(f"Searching for `{query}`")

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
            return await message.edit("No song found.")

        if isinstance(tracks, YouTubePlaylist):
            tracks = tracks.tracks
            for track in tracks:
                player.queue.put(track)
            
            await ctx.send(f"Added {len(tracks)} songs to the queue.")
        else:
            track = tracks[0]
            player.queue.put(track)
            await ctx.send(f"Added {track.title} to the queue.")

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
    async def on_wavelink_track_end(self, player: Player, track: wavelink.YouTubeTrack, reason):
        await player.do_next()
    
    @commands.Cog.listener()
    async def on_wavelink_track_stuck(self, player: Player, track: wavelink.YouTubeTrack, threshold):
        await player.do_next()

    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, player: Player, track: wavelink.YouTubeTrack, error):
        await player.do_next()

    @commands.command()
    async def connect(self, ctx: commands.Context):
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel!")
        if not ctx.voice_client:
            player: Player = await ctx.author.voice.channel.connect(cls=Player)
        else:
            player: Player = ctx.voice_client

    @commands.command()
    async def disconnect(self, ctx: commands.Context):
        channel = ctx.author.voice.channel

        await ctx.voice_client.disconnect()

    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str):
        await ctx.invoke(self.connect)
        await self.play_track(ctx, query)

    @commands.command()
    async def skip(self, ctx: commands.Context):
        if not ctx.voice_client:
            await ctx.send(".")
        else:
            player: Player = ctx.voice_client

        await player.stop()

    @commands.command()
    async def shuffle(self, ctx: commands.Context):
        player: Player = ctx.voice_client
        random.shuffle(player.queue._queue)
        await ctx.send("The queue has been shuffled.")

    @commands.command()
    async def queueclear(self, ctx: commands.Context):
        if not ctx.voice_client:
            player: Player = await ctx.author.voice.channel.connect(cls=Player)
        else:
            player: Player = ctx.voice_client
        player.queue.clear()

        await ctx.send("Queue has been cleared.")

    @commands.command()
    async def queue(self, ctx: commands.Context):
        if not ctx.voice_client:
            await ctx.send(".")
        else:
            player: Player = ctx.voice_client

            queue = ""
            for track in player.queue:
                queue += f"{track}\n"
            if not queue:
                await ctx.send("Queue is empty!")
            else:
                await ctx.send(queue)

async def setup(client):
    await client.add_cog(Music(client))