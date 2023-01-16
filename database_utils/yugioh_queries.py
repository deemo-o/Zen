TABLE_INIT_ = "CREATE TABLE IF NOT EXISTS yugioh (id INTEGER PRIMARY KEY,cardId INTEGER, name TEXT UNIQUE, type TEXT, attribute TEXT, race TEXT, level INTEGER, linkval TEXT, description TEXT, attack INTEGER, defense INTEGER, image TEXT, scale INTEGER);"

INSERT_YGOCARD = "INSERT INTO yugioh (cardId, name, type, attribute, race, level, linkval, description, attack, defense, image, scale) VALUES(?,?,?,?,?,?,?,?,?,?,?,?);"

UPDATE_YGOCARD = "UPDATE yugioh SET {}=? WHERE name = ?;"

DELETE_YGOCARD = "DELETE FROM yugioh WHERE name = ?;"

GET_YGOCARD_BY_NAME = "SELECT * FROM yugioh WHERE name = ?;"


