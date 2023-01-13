import discord
from database_utils import economy_database

def connection():
    try:
        connection = economy_database.connect()
        print("Connected to the Economy database!")
        return connection
    except Exception as exception:
        return exception

def create_tables(connection):
    try:
        economy_database.create_members_table(connection)
        print("Members Table is ready!")
        economy_database.create_ranks_table(connection)
        print("Ranks Table is ready!")
    except Exception as exception:
        return exception

def create_giftchannels_table(connection, guildid):
    try:
        economy_database.create_giftchannels_table(connection, guildid)
        print(f"GiftChannel - {guildid} Table is ready!")
    except Exception as exception:
        return exception

def create_guilds_table(connection):
    try:
        economy_database.create_guilds_table(connection)
        print("Guilds Table is ready!")
    except Exception as exception:
        return exception

def add_guild(connection, guildid, guildname):
    try:
        economy_database.add_guild(connection, guildid, guildname)
    except Exception as exception:
        return exception

def add_giftchannel(connection, guildid, channelid):
    try:
        economy_database.add_giftchannel(connection, guildid, channelid)
    except Exception as exception:
        return exception

def add_member_money(connection, member: discord.Member, money: int):
    try:
        temp_member = economy_database.get_member_by_userid(connection, member.id)[0]
        money += temp_member[3]
        economy_database.add_member_money(connection, member.id, money)
        temp_member_rank = temp_member[4]
        current_rank = economy_database.get_rank_by_name(connection, temp_member_rank)[0]
        current_rank_position = current_rank[5]
        ranks = economy_database.get_all_ranks(connection)
        for rank in ranks:
            if money >= rank[4]:
                temp_member_rank = rank
        economy_database.update_member(connection, member.id, temp_member_rank[1])
        old_member_rank = economy_database.get_rank_by_name(connection, temp_member[4])[0]
        new_member_rank = temp_member_rank
        if old_member_rank[4] < new_member_rank[4]:
            return f"Congratulations! <@{temp_member[1]}> promoted to **{new_member_rank[1].capitalize()}**!"
        elif old_member_rank[4] == new_member_rank[4]:
            return ""
        else:
            return f"Unlucky, <@{temp_member[1]}> demoted to **{new_member_rank[1].capitalize()}**."
    except Exception as exception:
        return exception

def update_rank(connection, name, minsalary, maxsalary, required, position):
    try:
        economy_database.update_rank(connection, name, minsalary, maxsalary, required, position)
    except Exception as exception:
        return exception

def check_member_exists(connection, member: discord.Member):
    try:
        if not economy_database.get_member_by_userid(connection, member.id):
            return False
        else:
            return True
    except Exception as exception:
        return exception

def get_all_guilds(connection):
    try:
        return economy_database.get_all_guilds(connection)
    except Exception as exception:
        return exception

def get_rank_minmax_salary(connection, rank: str):
    try:
        rank_data = economy_database.get_rank_by_name(connection, rank)
        minsalary: int = rank_data[0][2]
        maxsalary: int = rank_data[0][3]
        return minsalary, maxsalary
    except Exception as exception:
        return exception

def get_leaderboard(connection):
    try:
        return economy_database.get_all_members_by_networth(connection)
    except Exception as exception:
        return exception

def get_all_giftchannels(connection, guildid):
    try:
        return economy_database.get_all_giftchannels(connection, guildid)
    except Exception as exception:
        return exception

def get_ranks_by_position(connection):
    try:
        return economy_database.get_all_ranks_by_position(connection)
    except Exception as exception:
        return exception

def get_member(connection, member: discord.Member):
    try:
        return economy_database.get_member_by_userid(connection, member.id)
    except Exception as exception:
        return exception

def get_member_money(connection, member: discord.Member):
    try:
        return economy_database.get_member_by_userid(connection, member.id)[0][3]
    except Exception as exception:
        return exception

def get_member_rank(connection, member: discord.Member):
    try:
        return economy_database.get_member_by_userid(connection, member.id)[0][4]
    except Exception as exception:
        return exception

def get_default_rank(connection):
    try:
        return economy_database.get_rank_by_position(connection, 1)
    except Exception as exception:
        return exception

def get_rank_with_position(connection, position: int):
    try:
        return economy_database.get_rank_by_position(connection, position)
    except Exception as exception:
        return exception

def get_all_ranks(connection):
    try:
        return economy_database.get_all_ranks(connection)
    except Exception as exception:
        return exception

def create_member(connection, userid, name, money, rank):
    try:
        economy_database.add_member(connection, userid, name, money, rank)
    except Exception as exception:
        return exception

def create_rank(connection, rank, minsalary, maxsalary, required, position):
    try:
        economy_database.add_rank(connection, rank, minsalary, maxsalary, required, position)
    except Exception as exception:
        return exception

def delete_member(connection, userid):
    try:
        economy_database.delete_member_by_userid(connection, userid)
    except Exception as exception:
        return exception

def delete_rank(connection, position):
    try:
        economy_database.delete_rank_by_name(connection, position)
    except Exception as exception:
        return exception
        
def delete_giftchannel(connection, guildid, channelid):
    try:
        economy_database.delete_giftchannel(connection, guildid, channelid)
    except Exception as exception:
        return exception