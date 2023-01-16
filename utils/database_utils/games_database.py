import sqlite3 
from utils.database_utils import games_queries

def connect():
    return sqlite3.connect("utils/database_utils/database.db")

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

def create_typeracer_table(connection):
    with connection:
        connection.execute(games_queries.CREATE_TYPERACER_TABLE)
    
def insert_typeracer_rating(connection, userid, name, rating, ratingdeviation, volatility, matchcount, lastmatch):
    with connection:
        connection.execute(games_queries.INSERT_TYPERACER_RATING, (userid, name, rating, ratingdeviation, volatility, matchcount, lastmatch))

def update_typeracer_rating(connection, rating, ratingdeviation, volatility, matchcount, lastmatch, userid):
    with connection:
        connection.execute(games_queries.UPDATE_TYPERACER_RATING, (rating, ratingdeviation, volatility, matchcount, lastmatch, userid,))

def get_typeracer_rating(connection, userid):
    with connection:
        return connection.execute(games_queries.GET_TYPERACER_RATING_BY_USERID, (userid,)).fetchall()

def get_all_typeracer_ratings(connection):
    with connection:
        return connection.execute(games_queries.GET_ALL_TYPERACER_RATINGS).fetchall()