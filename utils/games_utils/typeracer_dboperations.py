import discord
from utils.database_utils import games_database

def connection():
    try:
        connection = games_database.connect()
        return connection
    except Exception as exception:
        return exception

def create_table(connection):
    try:
        games_database.create_typeracer_table(connection)
    except Exception as exception:
        return exception

def create_queue_announcementchannels_table(connection):
    try:
        games_database.create_typeracer_queue_announcementchannels(connection)
    except Exception as exception:
        return exception

def insert_rating(connection, userid, name, rating, ratingdeviation, volatility, matchcount, wins, losses, draws, lastmatch):
    try:
        games_database.insert_typeracer_rating(connection, userid, name, rating, ratingdeviation, volatility, matchcount, wins, losses, draws, lastmatch)
    except Exception as exception:
        return exception

def insert_queue_announcement_channel(connection, channelid):
    try:
        games_database.insert_typeracer_queue_announcementchannel(connection, channelid)
    except Exception as exception:
        return exception

def update_rating(connection, rating, ratingdeviation, volatility, matchcount, lastmatch, wins, losses, draws, userid):
    try:
        games_database.update_typeracer_rating(connection, rating, ratingdeviation, volatility, matchcount, lastmatch, wins, losses, draws, userid)
    except Exception as exception:
        return exception

def get_rating(connection, userid):
    try:
        data = games_database.get_typeracer_rating(connection, userid)
        if not data:
            return "Nope"
        return data
    except Exception as exception:
        return exception

def get_leaderboard(connection):
    try:
        return games_database.get_all_typeracer_ratings(connection)
    except Exception as exception:
        return exception

def get_queue_announcementchannel(connection, channelid):
    try:
        return games_database.get_typeracer_queue_announcementchannel(connection, channelid)
    except Exception as exception:
        return exception

def get_all_queue_announcementchannels(connection):
    try:
        return games_database.get_all_typeracer_queue_announcementchannels(connection)
    except Exception as exception:
        return exception

def delete_rating(connection, userid):
    try:
        games_database.delete_typeracer_rating(connection, userid)
    except Exception as exception:
        return exception

def delete_queue_announcementchannel(connection, channelid):
    try:
        games_database.delete_typeracer_queue_announcementchannel(connection, channelid)
    except Exception as exception:
        return exception