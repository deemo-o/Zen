import discord
from database_utils import todo_database

def connection():
    try:
        connection = todo_database.connect()
        print("Connected to Database From Todo DBOperations!")
        return connection
    except Exception as exception:
        return exception

def create_table(connection, memberid):
    try:
        todo_database.create_tasks_table(connection, memberid)
    except Exception as exception:
        return exception

def drop_table(connection, memberid):
    try:
        todo_database.drop_tasks_table(connection, memberid)
    except Exception as exception:
        return exception

def create_task(connection, memberid, task):
    try:
        todo_database.create_task(connection, memberid, task)
    except Exception as exception:
        return exception

def delete_task(connection, memberid, task):
    try:
        todo_database.delete_task(connection, memberid, task)
    except Exception as exception:
        return exception

def update_task(connection, memberid, task, task_name):
    try:
        todo_database.update_task(connection, memberid, task, task_name)
    except Exception as exception:
        return exception

def get_todo_list(connection, memberid):
    try:
        return todo_database.get_all_tasks(connection, memberid)
    except Exception as exception:
        return exception