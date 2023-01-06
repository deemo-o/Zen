import discord
from database_utils import games_database

def connection():
    try:
        games_database.connect()
    except Exception as exception:
        return exception

def create_table(connection):
    try:
        games_database.create_battleship_table(connection)
        print("Created Battleship Table")
    except Exception as exception:
        return exception

def insert_rating(connection, userid, rating):
    try:
        games_database.insert_battleship_rating(connection, userid, rating)
    except Exception as exception:
        return exception

def get_rating(connection, userid):
    try:
        return games_database.get_battleship_rating(connection, userid)
    except Exception as exception:
        return exception