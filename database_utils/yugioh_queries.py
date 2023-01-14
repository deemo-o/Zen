TABLE_INIT_ = """CREATE TABLE IF NOT EXISTS yugioh (id INTEGER PRIMARY KEY,cardId INTEGER UNIQUE, name TEXT, type TEXT, attribute TEXT, race TEXT, description TEXT, attack INTEGER, defense INTEGER, image TEXT)"""

INSERT_YGOCARD = """INSERT INTO yugioh (cardId, name, type, attribute, race, description, attack, defense, image) VALUES(?,?,?,?,?,?,?,?,?)"""

GET_YGOCARD_BY_NAME = """SELECT * FROM yugioh WHERE name = ?"""


