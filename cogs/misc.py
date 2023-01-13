import discord
import sqlite3
from discord.ext import commands, tasks
from discord import app_commands
from utils.misc_utils import todo_dboperations 

class Misc(commands.Cog, description="Misc commands."):

    def __init__(self, client: commands.Bot):
        self.client = client
        self.connection = todo_dboperations.connection()
        self.remind_members = []

    def cog_unload(self):
        self.remind_todo_to_members.cancel()

    def misc_embed(self, ctx: commands.Context):
        embed = discord.Embed(title="Zen | Misc", color=ctx.author.color)
        return embed

    async def cog_command_error(self, ctx: commands.Context, error: str):
        embed = self.misc_embed(ctx)
        if isinstance(error, Exception):
            embed.description = str(error).capitalize()
            return await ctx.send(embed=embed)

    @tasks.loop(seconds=2700)
    async def remind_todo_to_members(self):
        for member in self.remind_members:
            content = f"```SML\n{member.display_name}'s Task(s) in Todo List ⇓\n\n"
            counter = 1
            todo_dboperations.create_table(self.connection, member.id)
            tasks = todo_dboperations.get_todo_list(self.connection, member.id)
            for task in tasks:
                content += f"{counter} - {task[1]}\n"
                counter += 1
            content += "```"
            await member.send(content, delete_after=60)
            print(f"Sent todo reminder to {member.display_name}")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Misc module has been loaded.")

    @commands.command()
    async def reminderlist(self, ctx: commands.Context):
        embed = self.misc_embed(ctx)
        embed.title = "Zen | Reminder List"
        embed.description = ""
        for index, member in enumerate(self.remind_members):
            embed.description += f"{index + 1} - {member.mention}\n"
        await ctx.send(embed=embed)

    @commands.command(aliases=["remindtodo", "remindtodolist", "notifytodo", "todonotify"], brief="Will subscribe you to the todo list reminder.", description="This command will subscribe you to the todo list reminder, letting you see your todo list every 30 minutes.")
    async def todoreminder(self, ctx: commands.Context):
        todo_dboperations.create_table(self.connection, ctx.author.id)
        embed = self.misc_embed(ctx)
        embed.title = "Zen | Todo Reminder"
        if ctx.author not in self.remind_members:
            self.remind_members.append(ctx.author)
            embed.description = "Todo Reminder has been enabled."
            await ctx.send(embed=embed)
        else:
            self.remind_members.remove(ctx.author)
            embed.description = "Todo Reminder has been disabled."
            await ctx.send(embed=embed)

    @commands.command(brief="Turns on the global reminder.", description="This command will enable the reminder loop.")
    async def enablereminder(self, ctx: commands.Context):
        embed = self.misc_embed(ctx)
        embed.title = "Zen | Reminder"
        embed.description = "Reminder has been enabled and will notify users that are subscribed."
        self.remind_todo_to_members.start()
        await ctx.send(embed=embed)

    @commands.command(brief="Turns off the global reminder.", description="This command will disable the reminder loop.")
    async def disablereminder(self, ctx: commands.Context):
        embed = self.misc_embed(ctx)
        embed.title = "Zen | Reminder"
        embed.description = "Reminder has been disabled and will stop notifying users that are subscribed."
        self.remind_todo_to_members.cancel()
        await ctx.send(embed=embed)

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