import sqlite3 
from utils.database_utils import todo_queries

def connect():
    return sqlite3.connect("utils/database_utils/database.db")

def create_tasks_table(connection, memberid):
    with connection:
        connection.execute(todo_queries.CREATE_TASKS_TABLE.format(memberid))
    
def drop_tasks_table(connection, memberid):
    with connection:
        connection.execute(todo_queries.DROP_TASKS_TABLE.format(memberid))

def create_task(connection, memberid, task):
    with connection:
        connection.execute(todo_queries.CREATE_TASK.format(memberid), (task,))

def delete_task(connection, memberid, task):
    with connection:
        connection.execute(todo_queries.DELETE_TASK.format(memberid), (task,))

def update_task(connection, memberid, task, task_name):
    with connection:
        connection.execute(todo_queries.UPDATE_TASK.format(memberid), (task, task_name,))

def get_all_tasks(connection, memberid):
    with connection:
        return connection.execute(todo_queries.GET_ALL_TASKS.format(memberid)).fetchall()