CREATE_MEMBERS_TABLE = "CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY, userid INTEGER UNIQUE, name TEXT, money INTEGER, rank TEXT);"
CREATE_RANKS_TABLE = "CREATE TABLE IF NOT EXISTS ranks (id INTEGER PRIMARY KEY, name TEXT UNIQUE, minsalary INTEGER, maxsalary INTEGER, required INTEGER, position INTEGER UNIQUE);"
CREATE_GIFTCHANNELS_TABLE = "CREATE TABLE IF NOT EXISTS giftchannels_{} (id INTEGER PRIMARY KEY, channelid INTEGER unique);"
CREATE_GUILDS_TABLE = "CREATE TABLE IF NOT EXISTS guilds (id INTEGER PRIMARY KEY, guildid INTEGER UNIQUE, guildname TEXT);"
INSERT_GUILD = "INSERT OR REPLACE INTO guilds (guildid, guildname) VALUES (?, ?);"
INSERT_MEMBER = "INSERT INTO members (userid, name, money, rank) VALUES (?, ?, ?, ?);"
INSERT_RANK = "INSERT INTO ranks (name, minsalary, maxsalary, required, position) VALUES (?, ?, ?, ?, ?);"
INSERT_GIFTCHANNEL = "INSERT INTO giftchannels_{} (channelid) VALUES (?);"
UPDATE_MEMBER_MONEY = "UPDATE members SET money = ? WHERE userid = ?;"
UPDATE_MEMBER_RANK = "UPDATE members SET rank = ? WHERE userid = ?;"
UPDATE_RANK = "UPDATE ranks SET name = ?, minsalary = ?, maxsalary = ?, required = ? WHERE position = ?;"
GET_ALL_GUILDS = "SELECT * FROM guilds;"
GET_ALL_MEMBERS = "SELECT * FROM members;"
GET_ALL_MEMBERS_BY_NETWORTH = "SELECT * FROM members ORDER BY money DESC;"
GET_ALL_RANKS = "SELECT * FROM ranks;"
GET_ALL_RANKS_BY_POSITION = "SELECT * FROM ranks ORDER BY position DESC;"
GET_ALL_GIFTCHANNELS = "SELECT * FROM giftchannels_{};"
GET_MEMBER_BY_USERID = "SELECT * FROM members WHERE userid = ?;"
GET_RANK_BY_NAME = "SELECT * FROM ranks WHERE name = ?;"
GET_RANK_BY_POSITION = "SELECT * FROM ranks WHERE position = ?;"
DELETE_MEMBER = "DELETE FROM members WHERE userid = ?;"
DELETE_RANK = "DELETE FROM ranks WHERE position = ?;"
DELETE_GIFTCHANNEL = "DELETE FROM giftchannels_{} WHERE channelid = ?"