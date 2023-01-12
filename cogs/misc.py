import discord
import sqlite3
from discord.ext import commands
from discord import app_commands
from misc_utils import todo_dboperations 

class Misc(commands.Cog, description="Misc commands."):

    def __init__(self, client: commands.Bot):
        self.client = client
        self.connection = todo_dboperations.connection()

    def misc_embed(self, ctx: commands.Context):
        embed = discord.Embed(title="Zen | Misc", color=ctx.author.color)
        return embed

    async def cog_command_error(self, ctx: commands.Context, error: str):
        embed = self.misc_embed(ctx)
        if isinstance(error, Exception):
            embed.description = str(error).capitalize()
            return await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Misc module has been loaded.")

    @commands.command(aliases=["tasklist", "todolist", "todo"], brief="Lists all your tasks.", description="This command will list all of your current tasks.")
    async def tasks(self, ctx: commands.Context):
        embed = self.misc_embed(ctx)
        embed.title = "Zen | Todo List"
        content = f"```SML\n{ctx.author.display_name}'s Task(s) in Todo List ⇓\n\n"
        member = ctx.author
        counter = 1
        todo_dboperations.create_table(self.connection, member.id)
        tasks = todo_dboperations.get_todo_list(self.connection, member.id)
        for task in tasks:
            content += f"{counter} - {task[1]}\n"
            counter += 1
        content += "```"
        await ctx.send(content, delete_after=60)
        print(tasks)

    @commands.command(aliases=["cleartask", "cleartodo", "todoclear"], brief="Clears your todo list.", description="This command will clear all the task(s) in your to do list.")
    async def taskclear(self, ctx: commands.Context):
        member = ctx.author
        todo_dboperations.drop_table(self.connection, member.id)
        todo_dboperations.create_table(self.connection, member.id)
        await ctx.invoke(self.tasks)

    @commands.command(aliases=["checktask", "todocheck", "checktodo"], brief="Mark a task as done.", description="This command will mark the checkbox of the task you specified.")
    async def taskcheck(self, ctx: commands.Context, task_index: int):
        member = ctx.author
        todo_dboperations.create_table(self.connection, member.id)
        tasks = todo_dboperations.get_todo_list(self.connection, member.id)
        for index, task in enumerate(tasks):
            if task_index == index + 1:
                todo_dboperations.update_task(self.connection, member.id, f"[X] {task[1][4:].upper()}", task[1])
                await ctx.invoke(self.tasks)

    @commands.command(aliases=["createtask", "addtask", "taskadd"], brief="Adds a task in your todo list.", description="This command will add a new task in your todo list.")
    async def taskcreate(self, ctx: commands.Context, *, task: str):
        member = ctx.author
        todo_dboperations.create_table(self.connection, member.id)
        task_index = len(todo_dboperations.get_todo_list(self.connection, member.id))
        todo_dboperations.create_task(self.connection, member.id, f"[ ] [{task.upper()}]")
        await ctx.invoke(self.tasks)

    @commands.command(aliases=["deletetask", "removetask", "taskremove"], brief="Removes a task from your todo list.", description="This command will remove a task from your todo list.")
    async def taskdelete(self, ctx: commands.Context, task_index: int):
        member = ctx.author
        todo_dboperations.create_table(self.connection, member.id)
        tasks = todo_dboperations.get_todo_list(self.connection, member.id)
        for index, task in enumerate(tasks):
            if task_index == index + 1:
                todo_dboperations.delete_task(self.connection, member.id, task[1])
                await ctx.invoke(self.tasks)

async def setup(client):
    await client.add_cog(Misc(client))