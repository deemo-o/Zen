import discord
from database_utils import games_database

def connection():
    try:
        connection = games_database.connect()
        print("Connected to Database From Battleship DBOperations!")
        return connection
    except Exception as exception:
        return exception

def create_table(connection):
    try:
        games_database.create_battleship_table(connection)
        print("Created Battleship Table")
    except Exception as exception:
        return exception

def insert_rating(connection, userid, name, rating):
    try:
        games_database.insert_battleship_rating(connection, userid, name, rating)
    except Exception as exception:
        return exception

def get_rating(connection, userid):
    try:
        data = games_database.get_battleship_rating(connection, userid)
        if not data:
            return 1200
        print(data)
        rating = data[0][3]
        print(rating)
        return rating
    except Exception as exception:
        return exception

def get_leaderboard(connection):
    try:
        return games_database.get_all_ratings(connection)
    except Exception as exception:
        return exception