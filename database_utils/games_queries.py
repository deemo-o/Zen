CREATE_BATTLESHIP_TABLE = "CREATE TABLE IF NOT EXISTS battleship (id INTEGER PRIMARY KEY, userid INTEGER UNIQUE, name TEXT, rating INTEGER);"
INSERT_BATTLESHIP_RATING = "INSERT OR REPLACE INTO battleship (userid, name, rating) VALUES (?, ?, ?);"
GET_BATTLE_SHIP_RATING_BY_USERID = "SELECT * FROM battleship where userid = ?;"
GET_ALL_RATINGS = "SELECT * FROM battleship ORDER BY rating DESC;"