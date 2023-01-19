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

def create_typeracer_table(connection):
    with connection:
        connection.execute(games_queries.CREATE_TYPERACER_TABLE)
    
def create_typeracer_queue_announcementchannels(connection):
    with connection:
        connection.execute(games_queries.CREATE_TYPERACER_QUEUE_ANNOUNCEMENTCHANNELS_TABLE)

def insert_typeracer_rating(connection, userid, name, rating, ratingdeviation, volatility, matchcount, wins, losses, draws, lastmatch):
    with connection:
        connection.execute(games_queries.INSERT_TYPERACER_RATING, (userid, name, rating, ratingdeviation, volatility, matchcount, wins, losses, draws, lastmatch))

def insert_typeracer_queue_announcementchannel(connection, channelid):
    with connection:
        connection.execute(games_queries.INSERT_TYPERACER_QUEUE_ANNOUNCEMENTCHANNEL, (channelid,))

def update_typeracer_rating(connection, rating, ratingdeviation, volatility, matchcount, lastmatch, wins, losses, draws, userid):
    with connection:
        connection.execute(games_queries.UPDATE_TYPERACER_RATING, (rating, ratingdeviation, volatility, matchcount, lastmatch, wins, losses, draws, userid,))

def get_typeracer_rating(connection, userid):
    with connection:
        return connection.execute(games_queries.GET_TYPERACER_RATING_BY_USERID, (userid,)).fetchall()

def get_typeracer_queue_announcementchannel(connection, channelid):
    with connection:
        return connection.execute(games_queries.GET_TYPERACER_QUEUE_ANNOUNCEMENTCHANNEL_BY_ID, (channelid,)).fetchall()

def get_all_typeracer_ratings(connection):
    with connection:
        return connection.execute(games_queries.GET_ALL_TYPERACER_RATINGS).fetchall()

def get_all_typeracer_queue_announcementchannels(connection):
    with connection:
        return connection.execute(games_queries.GET_ALL_TYPERACER_QUEUE_ANNOUNCEMENTCHANNELS).fetchall()

def delete_typeracer_rating(connection, userid):
    with connection:
        connection.execute(games_queries.DELETE_TYPERACER_RATING, (userid,))

def delete_typeracer_queue_announcementchannel(connection, channelid):
    with connection:
        connection.execute(games_queries.DELETE_TYPERACER_QUEUE_ANNOUNCEMENT_CHANNEL, (channelid,))

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
