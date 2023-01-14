TABLE_INIT_ = "CREATE TABLE IF NOT EXISTS yugioh (id INTEGER PRIMARY KEY,cardId INTEGER, name TEXT UNIQUE, type TEXT, attribute TEXT, race TEXT, level INTEGER, linkval TEXT, description TEXT, attack INTEGER, defense INTEGER, image TEXT);"

INSERT_YGOCARD = "INSERT INTO yugioh (cardId, name, type, attribute, race, level, linkval, description, attack, defense, image) VALUES(?,?,?,?,?,?,?,?,?,?,?);"

GET_YGOCARD_BY_NAME = "SELECT * FROM yugioh WHERE name = ?;"


