import sqlite3

"""
Image:
INSERT INTO image VALUES (?,...);
DELETE FROM image WHERE filename=?;
UPDATE image SET maneuver=? WHERE filename=?;

Sequence:
INSERT INTO sequence (country) VALUES (?);
DELETE FROM sequence WHERE id=?;
UPDATE sequence SET country=?/type=? WHERE id=?;

Country:
INSERT INTO country VALUES (?);
SELECT id FROM country WHERE code=?;


get_country_id(code) - Creates or selects country and returns cid
get_country_list() - Returns list with all country codes and ids

add_image(filename, ...)
set_image_maneuver(filename or filename-range)
delete_image(filename)
get_image_list(sequence) - Returns list with all images in a sequence

add_sequence(country, type=-1)
update_sequence(country, type)
delete_sequence(id)
get_sequence_list() - Returns list with all sequences
"""


class Database(object):
    def __init__(self):
        sql_create_tables = """CREATE TABLE IF NOT EXISTS settings (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    key VARCHAR(45) PRIMARY KEY,
                                    value TEXT NOT NULL
                                );
                                
                                CREATE TABLE IF NOT EXISTS country (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    code VARCHAR(3) UNIQUE
                                );
                                
                                CREATE TABLE IF NOT EXISTS sequence (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    country INT,
                                    type INT DEFAULT -1,
                                    FOREIGN KEY(country) REFERENCES country(id)
                                );
                                
                                CREATE TABLE IF NOT EXISTS image (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    filename VARCHAR UNIQUE,
                                    steering DOUBLE NOT NULL,
                                    speed INTEGER,
                                    throttle DOUBLE,
                                    maneuver INTEGER NOT NULL,
                                    sequence INTEGER NOT NULL,
                                    FOREIGN KEY(sequence) REFERENCES sequence(id) ON DELETE CASCADE 
                                );
                            """

        self.conn = sqlite3.connect('data.sqlite')

        try:
            c = self.conn.cursor()
            c.execute(sql_create_tables)
        except Exception as e:
            print(e)

    def execute(self, command, params=()):
        try:
            c = self.conn.cursor()
            c.execute(command, params)

            if command.startswith("INSERT"):
                return c.lastrowid
            else:
                return c.fetchall()
        except Exception as e:
            print(e)
            return "ERROR"


class Settings(object):
    def __init__(self):
        self.db = Database()

    def get_value(self, key):
        """
        :param key:
        :return: Returns settings value or None if the key does not exist
        """
        result = self.db.execute("SELECT value FROM settings WHERE key=?", (key,))
        if len(result) > 0 and result != "ERROR":
            return result[0][0]
        else:
            return None

    def set_value(self, key, value):
        self.db.execute("UPDATE settings SET value=? WHERE key=?", (value, key,))

    def delete_entry(self, key):
        self.db.execute("DELETE FROM settings WHERE key=?", (key,))


class Sequence(object):
    def __init__(self):
        self.db = Database()

    def get_country_id(self, code):
        cid = self.db.execute("SELECT id FROM country WHERE code=?", (code,))
        if len(cid) > 0:
            return cid[0][0]
        else:
            return self.db.execute("INSERT INTO country (code) VALUES (?)", (code,))

    def add_sequence(self, type):
        """
        Creates a new sequence in db
        :return: ID of new sequence
        """
        settings = Settings()
        country = settings.get_value("country")
        cid = self.get_country_id(country)
        id = self.db.execute("INSERT INTO sequence (country) VALUES (?)", (cid,))
        return id


class Image(object):
    def __init__(self):
        self.db = Database()

    def add_image(self, filename, steering, speed, throttle, maneuver, sequence):
        self.db.execute("INSERT INTO image VALUES (?,?,?,?,?,?)", (filename, steering, speed, throttle, maneuver, sequence,))

    def delete_image(self, filename):
        self.db.execute("DELETE FROM image WHERE filename=?", (filename,))
