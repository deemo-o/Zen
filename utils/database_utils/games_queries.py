CREATE_BATTLESHIP_TABLE = "CREATE TABLE IF NOT EXISTS battleship (id INTEGER PRIMARY KEY, userid INTEGER UNIQUE, name TEXT, rating INTEGER);"
INSERT_BATTLESHIP_RATING = "INSERT OR REPLACE INTO battleship (userid, name, rating) VALUES (?, ?, ?);"
GET_BATTLE_SHIP_RATING_BY_USERID = "SELECT * FROM battleship where userid = ?;"
GET_ALL_BATTLESHIP_RATINGS = "SELECT * FROM battleship ORDER BY rating DESC;"

CREATE_TYPERACER_TABLE = "CREATE TABLE IF NOT EXISTS typeracer_ratings (id INTEGER PRIMARY KEY, userid INTEGER UNIQUE, name TEXT, rating INTEGER, ratingdeviation REAL, volatility REAL, matchcount INTEGER, lastmatch TEXT);"
INSERT_TYPERACER_RATING = "INSERT INTO typeracer_ratings (userid, name, rating, ratingdeviation, volatility, matchcount, lastmatch) VALUES (?, ?, ?, ?, ?, ?, ?);"
UPDATE_TYPERACER_RATING = "UPDATE typeracer_ratings SET rating = ?, ratingdeviation = ?, volatility = ?, matchcount = ?, lastmatch = ? WHERE userid = ?"
GET_TYPERACER_RATING_BY_USERID = "SELECT * FROM typeracer_ratings where userid = ?;"
GET_ALL_TYPERACER_RATINGS = "SELECT * FROM typeracer_ratings ORDER BY rating DESC;"

CREATE_RPS_TABLE = "CREATE TABLE IF NOT EXISTS rps (id INTEGER PRIMARY KEY, userid INTEGER UNIQUE, name TEXT, rating INTEGER);"
INSERT_RPS_RATING = "INSERT OR REPLACE INTO rps (userid, name, rating) VALUES (?, ?, ?);"
GET_RPS_RATING_BY_USERID ="SELECT * FROM rps WHERE USERID = ?;"
GET_ALL_RPS_RATINGS = "SELECT * FROM rps ORDER BY rating DESC;"
