import sqlite3 
from database_utils import rps_queries

def connect():
    return sqlite3.connect("database_utils/database.db")

def create_rps_table(connection):
    with connection:
        connection.execute(rps_queries.CREATE_RPS_TABLE)
        
def insert_rps_rating(connection, userid, name, rating):
     with connection:
        connection.execute(rps_queries.INSERT_RPS_RATING, (userid, name, rating))

def get_rps_rating(connection, userid):
    with connection:
        return connection.execute(rps_queries.GET_RPS_RATING_BY_USERID, (userid,)).fetchall()

def get_all_ratings(connection):
    with connection:
        return connection.execute(rps_queries.GET_ALL_RATINGS).fetchall()