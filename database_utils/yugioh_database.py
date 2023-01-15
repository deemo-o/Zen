import sqlite3
from database_utils import yugioh_queries


def connect():
    try:
        print("Connection just Opened!")
        return sqlite3.connect('database_utils/database.db')
    except Exception as error:
        print(error)


def insertCard(conn, cardId, name, type, attribute, race, level, linkval, description, attack, defense, image, scale):

    with conn:
        c = conn.cursor()
        c.execute(yugioh_queries.TABLE_INIT_)
        c.execute(yugioh_queries.INSERT_YGOCARD, (cardId, name, type, attribute, race, level, linkval, description, attack, defense, image, scale))


def getCardByName(conn, name):
    with conn:
        c = conn.cursor()
        c.execute(yugioh_queries.TABLE_INIT_)
        try:
            # c.execute("SELECT * FROM yugioh;")
            c.execute(yugioh_queries.GET_YGOCARD_BY_NAME, (name,))
            return c.fetchall()

        except Exception as error:
            print(error)
        
            