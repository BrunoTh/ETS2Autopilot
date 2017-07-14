import sqlite3


class Database(object):
    def __init__(self):
        sql_create_tables = list()
        sql_create_tables.append("""CREATE TABLE IF NOT EXISTS settings (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    key VARCHAR(45) UNIQUE,
                                    value TEXT NOT NULL
                                );""")
                                
        sql_create_tables.append("""CREATE TABLE IF NOT EXISTS country (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    code VARCHAR(3) UNIQUE
                                );""")
                                
        sql_create_tables.append("""CREATE TABLE IF NOT EXISTS sequence (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    country INT,
                                    type INT DEFAULT -1,
                                    FOREIGN KEY(country) REFERENCES country(id)
                                );""")
                                
        sql_create_tables.append("""CREATE TABLE IF NOT EXISTS image (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    filename VARCHAR UNIQUE,
                                    steering DOUBLE NOT NULL,
                                    speed INTEGER,
                                    throttle DOUBLE,
                                    maneuver INTEGER NOT NULL,
                                    sequence INTEGER NOT NULL,
                                    FOREIGN KEY(sequence) REFERENCES sequence(id) ON DELETE CASCADE 
                                );""")

        self.conn = sqlite3.connect('data.sqlite')

        try:
            c = self.conn.cursor()
            for sql_statement in sql_create_tables:
                c.execute(sql_statement)
        except Exception as e:
            print(e)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def execute(self, command, params=()):
        try:
            c = self.conn.cursor()
            c.execute(command, params)
            self.conn.commit()
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


class Data(object):
    def __init__(self):
        self.db = Database()
        self.settings = Settings()

    def get_country_id(self, code):
        """
        Looks up the id of the given country code and creates a new entry if the code isn't in the table.
        :param code: Country code
        :return: country id
        """
        cid = self.db.execute("SELECT id FROM country WHERE code=?", (code,))
        if len(cid) > 0:
            return cid[0][0]
        else:
            return self.db.execute("INSERT INTO country (code) VALUES (?)", (code,))

    def get_country_list(self):
        """
        :return: List with all country codes and ids
        """
        result = self.db.execute("SELECT id, code FROM country")
        if type(result) == str and result.startswith("ERROR"):
            return []
        else:
            return result

    def add_image(self, filename, steering, speed, throttle, maneuver, sequence):
        self.db.execute("INSERT INTO image VALUES (?,?,?,?,?,?)", (filename, steering, speed, throttle, maneuver, sequence,))

    def set_image_maneuver(self, filename, maneuver):
        self.db.execute("UPDATE image SET maneuver=? WHERE filename=?", (maneuver, filename,))

    def delete_image(self, filename):
        self.db.execute("DELETE FROM image WHERE filename=?", (filename,))

    def get_image_list(self, sequence):
        """
        :param sequence: id of sequence
        :return: List with all images of a sequence
        """
        result = self.db.execute("SELECT filename, steering, speed, throttle, maneuver FROM image WHERE sequence=?", (sequence,))
        if type(result) == str and result.startswith("ERROR"):
            return []
        else:
            return result

    def add_sequence(self, country=None, road_type=-1):
        """
        Creates a new sequence in db
        :return: ID of new sequence
        """
        if not country:
            if not self.settings.get_value("country"):
                country = "NULL"
            else:
                country = self.settings.get_value("country")
        cid = self.get_country_id(country)
        return self.db.execute("INSERT INTO sequence (country, type) VALUES (?, ?)", (cid, road_type,))

    def update_sequence(self, sid, country=None, road_type=None):
        """
        :param sid: id of sequence you want to update
        :param country: country code
        :param road_type: road type
        :return:
        """
        if country is not None:
            cid = self.get_country_id(country)
            self.db.execute("UPDATE sequence SET country=? WHERE id=?", (cid, sid,))
        if road_type is not None:
            self.db.execute("UPDATE sequence SET type=? WHERE id=?", (road_type, sid,))

    def delete_sequence(self, sid):
        self.db.execute("DELETE FROM sequence WHERE id=?", (sid,))

    def get_sequence_list(self):
        """
        :return: List with all sequences
        """
        result = self.db.execute("SELECT id, country, type FROM sequence")
        if type(result) == str and result.startswith("ERROR"):
            return []
        else:
            return result
