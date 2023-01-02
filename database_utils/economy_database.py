import sqlite3 

CREATE_MEMBERS_TABLE = "CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY, userid INTEGER UNIQUE, name TEXT, money INTEGER);"
INSERT_MEMBER = "INSERT INTO members (userid, name, money) VALUES (?, ?, ?);"
UPDATE_MEMBER_MONEY = "UPDATE members SET money = ? WHERE userid = ?;"
GET_ALL_MEMBERS = "SELECT * FROM members;"
GET_MEMBER_BY_USERID = "SELECT * FROM members WHERE userid = ?;"

def connect():
    return sqlite3.connect("database_utils/economy.db")

def create_table(connection):
    with connection:
        connection.execute(CREATE_MEMBERS_TABLE)

def add_member(connection, userid, name, money):
    with connection:
        connection.execute(INSERT_MEMBER, (userid, name, money))

def update_member(connection, userid, money):
    money += get_member(connection, userid)[0][3]
    with connection:
        connection.execute(UPDATE_MEMBER_MONEY, (money, userid))

def get_all_members(connection):
    with connection:
        return connection.execute(GET_ALL_MEMBERS).fetchall()

def get_member(connection, userid):
    with connection:
        return connection.execute(GET_MEMBER_BY_USERID, (userid,)).fetchall()
