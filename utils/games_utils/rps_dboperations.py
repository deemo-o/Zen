import discord
from database_utils import rps_database

def connection():
    try:
      connection = rps_database.connect()
      print("Connected to Database From RPS DBOperations!")
      return connection
    except Exception as exception:
      return exception

def create_table(connection):
    try:
      rps_database.create_rps_table(connection)
      print("Created RPS Table")
    except Exception as exception:
      return exception
      
def insert_rating(connection, userid, name, rating):
    try:
      rps_database.insert_rps_rating(connection, userid, name, rating)
    except Exception as exception:
      return exception

def get_rating(connection, userid):
    try:
      data = rps_database.get_rps_rating(connection, userid)
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
      return rps_database.get_all_ratings(connection)
    except Exception as exception:
      return exception