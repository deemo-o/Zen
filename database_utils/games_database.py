import sqlite3 
from database_utils import games_queries

def connect():
    return sqlite3.connect("database_utils/database.db")

def create_battleship_table(connection):
    with connection:
        connection.execute(games_queries.CREATE_BATTLESHIP_TABLE)
    
def insert_battleship_rating(connection, userid, name, rating):
    with connection:
        connection.execute(games_queries.INSERT_BATTLESHIP_RATING, (userid, name, rating))

def get_battleship_rating(connection, userid):
    with connection:
        return connection.execute(games_queries.GET_BATTLE_SHIP_RATING_BY_USERID, (userid,)).fetchall()

def get_all_ratings(connection):
    with connection:
        return connection.execute(games_queries.GET_ALL_RATINGS).fetchall()