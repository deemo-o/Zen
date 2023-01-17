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

def get_all_battleship_ratings(connection):
    with connection:
        return connection.execute(games_queries.GET_ALL_BATTLESHIP_RATINGS).fetchall()

def create_rps_table(connection):
    with connection:
        connection.execute(games_queries.CREATE_RPS_TABLE)
        
def insert_rps_rating(connection, userid, name, rating):
     with connection:
        connection.execute(games_queries.INSERT_RPS_RATING, (userid, name, rating))

def get_rps_rating(connection, userid):
    with connection:
        return connection.execute(games_queries.GET_RPS_RATING_BY_USERID, (userid,)).fetchall()

def get_all_rps_ratings(connection):
    with connection:
        return connection.execute(games_queries.GET_ALL_RPS_RATINGS).fetchall()