import sqlite3


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
                                    type INT,
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
                                    FOREIGN KEY(sequence) REFERENCES sequence(id)
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
            return c.fetchall()
        except Exception as e:
            print(e)
            return "ERROR"


class Settings(object):
    def __init__(self):
        self.db = Database()

    def get_value(self, key):
        pass

    def set_value(self, key, value):
        pass
