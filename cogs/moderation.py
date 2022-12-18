import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import get
 
class Moderation(commands.Cog, description="Moderation commands."):
    
    def __init__(self, client: commands.Bot):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Moderation module has been loaded.")

    @commands.command()
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