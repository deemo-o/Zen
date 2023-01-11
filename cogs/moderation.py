import asyncio
import discord
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from discord.utils import get
 
class Moderation(commands.Cog, description="Moderation commands."):
    
    def __init__(self, client: commands.Bot):
        self.client = client
        self.poll_channel = None
        self.poll_reactions_count = {"Yes": 0, "No": 0}
        
    def moderation_embed(self, ctx: commands.Context) -> discord.Embed:
        embed = discord.Embed(title="Zen | Moderation", color=ctx.author.color, timestamp=datetime.now())
        return embed

    async def cog_command_error(self, ctx: commands.Context, error: str):
        embed = self.moderation_embed(ctx)
        if isinstance(error, Exception):
            embed.description = str(error).capitalize()
            return await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Moderation module has been loaded.")
        self.poll_channel = self.client.get_channel(1059185820424216656)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await member.add_roles(get(member.guild.roles, name="Meditator"), reason="Default role when joining.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        member: discord.Member = payload.member
        channel_id: discord.TextChannel.id = payload.channel_id
        emoji: discord.PartialEmoji = payload.emoji

        study_role = get(member.guild.roles, name="Study")
        movie_role = get(member.guild.roles, name="Movie")
        game_role = get(member.guild.roles, name="Game")
        vibe_role = get(member.guild.roles, name="Vibe")
        karaoke_role = get(member.guild.roles, name="Karaoke")

        if channel_id == 1053501652226813982:
            if str(emoji) == "💚":
                await member.add_roles(study_role)
                print(f"{member} has added the Study role.")
            if str(emoji) == "💛":
                await member.add_roles(movie_role)
                print(f"{member} has added the Movie role.")
            if str(emoji) == "💙":
                await member.add_roles(game_role)
                print(f"{member} has added the Game role.")
            if str(emoji) == "💜":
                await member.add_roles(vibe_role)
                print(f"{member} has added the Vibe role.")
            if str(emoji) == "🤎":
                await member.add_roles(karaoke_role)
                print(f"{member} has added the Karaoke role.")

        if channel_id == self.poll_channel.id:
            if str(payload.emoji) == "👍":
                self.poll_reactions_count["Yes"] += 1
            if str(payload.emoji) == "👎":
                self.poll_reactions_count["No"] += 1

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        member: discord.Member = get(self.client.get_guild(payload.guild_id).members, id=payload.user_id)
        channel_id: discord.TextChannel.id = payload.channel_id
        emoji: discord.PartialEmoji = payload.emoji
        study_role = get(member.guild.roles, name="Study")
        movie_role = get(member.guild.roles, name="Movie")
        game_role = get(member.guild.roles, name="Game")
        vibe_role = get(member.guild.roles, name="Vibe")
        karaoke_role = get(member.guild.roles, name="Karaoke")

        if channel_id == 1053501652226813982:
            if str(emoji) == "💚":
                await member.remove_roles(study_role)
                print(f"{member} has removed the Study role.")
            if str(emoji) == "💛":
                await member.remove_roles(movie_role)
                print(f"{member} has removed the Movie role.")
            if str(emoji) == "💙":
                await member.remove_roles(game_role)
                print(f"{member} has removed the Game role.")
            if str(emoji) == "💜":
                await member.remove_roles(vibe_role)
                print(f"{member} has removed the Vibe role.")
            if str(emoji) == "🤎":
                await member.remove_roles(karaoke_role)
                print(f"{member} has removed the Karaoke role.")

    @commands.command(aliases=["clear", "clearm", "deletemessage", "deletem", "purge"], brief="Clears messages in a channel.", description="This command will clear an amount of messages in a text channel. Is a user is specified, this command will clear all the messages the user sent in the last amount of messages.")
    async def clearmessage(self, ctx: commands.Context, amount: int = 20, member: discord.Member = None):
        embed = self.moderation_embed(ctx)
        if member is None:
            await ctx.channel.purge(limit=amount+1)
            embed.description = f"Cleared `{amount}` messages in {ctx.channel.mention}!"
            await ctx.send(embed=embed, delete_after=15)
        else:
            await ctx.channel.purge(limit=amount+1, check=lambda x: x.author.id == member.id)
            embed.description = f"Cleared all messages sent by {member.mention} in {ctx.channel.mention} in the last {amount} messages!"
            await ctx.send(embed=embed, delete_after=15)

    @commands.command(aliases=["warning", "alert", "inform"], brief="Warn a user with the specified message", description="This command will send a warning message to a user with the specified message.")
    async def warn(self, ctx: commands.Context, member: discord.Member, *, message: str):
        embed = self.moderation_embed(ctx)
        embed.title = "Zen | Warning"
        embed.add_field(name="Message", value=f"**{message}**")
        embed.set_footer(text=f"You have been warned by {ctx.author.name}", icon_url=ctx.author.avatar)
        await member.send(embed=embed)

    @commands.command(aliases=["lock"], brief="Prevents users from sending message in a channel.", description="This command will lock a channel and prevent any users from sending messages in the channel.")
    async def lockchannel(self, ctx: commands.Context):
        embed = self.moderation_embed(ctx)
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        embed.description = f"Locked {ctx.channel.mention}"
        await ctx.send(embed=embed)

    @commands.command(aliases=["unlock"], brief="Removes the prevention allowing users to send messages in a channel.", description="This command will unlock a channel and allow users to send messages in the channel again.")
    async def unlockchannel(self, ctx: commands.Context):
        embed = self.moderation_embed(ctx)
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        embed.description = f"Unlocked {ctx.channel.mention}"
        await ctx.send(embed=embed)

    @commands.command(brief="Asks admins for help.", description="This command will send your call for help message to every admin in the server.")
    async def adminhelp(self, ctx: commands.Context, *, message: str):
        embed = self.moderation_embed(ctx)
        embed.title = "Zen | Admin Help"
        embed.description = "Someone is asking for an admin!"
        embed.add_field(name="Message", value=f"**{message}**")
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar)
        guild = discord.utils.get(self.client.guilds, id=ctx.guild.id)
        for member in guild.members:
            for role in member.roles:
                if role.name == "Admin":
                    await member.send(embed=embed)

    # Yes and No answers only
    @commands.command(brief="Starts a poll with the specified question and time limit.", description="This command will start a poll with the time limit you as the first argument and the question as the second argument.")
    async def poll(self, ctx: commands.Context, timeout: int, *, message: str):
        channel = self.poll_channel
        embed = self.moderation_embed(ctx)
        embed.title = "Zen | Poll"
        embed.add_field(name="Question", value=f"**{message}**", inline=False)
        embed.add_field(name="Duration", value=f"This poll will last {timeout} seconds.", inline=False)
        poll = await channel.send(embed=embed)
        await poll.add_reaction("👍")
        await poll.add_reaction("👎")
        await asyncio.sleep(timeout)
        count = "The poll has ended! Here are the results:\n"
        count += f"**Yes: {self.poll_reactions_count['Yes'] - 1}**\n**No: {self.poll_reactions_count['No'] - 1}**"
        embed.set_field_at(1, name="Result", value=count, inline=False)
        await poll.edit(embed=embed)
            
    @commands.command(brief="Sets up the roles. (work in progress)", description="Work in progress.")
    async def rolesetup(self, ctx: commands.Context, channel: discord.TextChannel):
        study_role = get(ctx.author.guild.roles, name="Study")
        movie_role = get(ctx.author.guild.roles, name="Movie")
        game_role = get(ctx.author.guild.roles, name="Game")
        vibe_role = get(ctx.author.guild.roles, name="Vibe")
        karaoke_role = get(ctx.author.guild.roles, name="Karaoke")

        description = "React with the emoji corresponding to the role you\'d like.\n\n"
        description += f"💚 | <@&{study_role.id}> - Study sessions\n"
        description += f"💛 | <@&{movie_role.id}> - Movie nights\n"
        description += f"💙 | <@&{game_role.id}> - Gaming\n"
        description += f"💜 | <@&{vibe_role.id}> - Vibe with others\n"
        description += f"🤎 | <@&{karaoke_role.id}> - Karaoke nights\n"

        embed = discord.Embed(title="List of available roles", description=description, color=discord.Color.from_rgb(248, 175, 175))
        message: discord.Message = await channel.send(embed=embed)
        await message.add_reaction("💚")
        await message.add_reaction("💛")
        await message.add_reaction("💙")
        await message.add_reaction("💜")
        await message.add_reaction("🤎")

async def setup(client):
    await client.add_cog(Moderation(client))