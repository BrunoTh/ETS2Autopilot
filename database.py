import sqlite3
import os


class Database(object):
    def __init__(self, batch=False):
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
                                    note VARCHAR(45),
                                    controller_type INT,
                                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
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
        self.batch = batch

        try:
            c = self.conn.cursor()
            for sql_statement in sql_create_tables:
                c.execute(sql_statement)
        except Exception as e:
            print(e)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def execute(self, command, params=()):
        try:
            c = self.conn.cursor()
            c.execute(command, params)
            if not self.batch:
                self.conn.commit()
            if command.startswith("INSERT"):
                return c.lastrowid
            else:
                return c.fetchall()
        except Exception as e:
            print(e)
            return "ERROR"


class Settings(object):
    CONTROLLER = "controller_id"
    VJOY_DEVICE = "vjoy_id"

    AUTOPILOT_SOUND_ACTIVATE = "autopilot_sound.activate"
    AUTOPILOT_SOUND_DEACTIVATE = "autopilot_sound.deactivate"
    ADAPTIVE_STEERING = "adaptive_steering"

    COUNTRY_DEFAULT = "country_default"
    COUNTRIES_MODEL = "countries_model"

    AUTOPILOT = "button_autopilot"
    LEFT_INDICATOR = "button_left_indicator"
    RIGHT_INDICATOR = "button_right_indicator"
    STEERING_AXIS = "axis_steering"
    THROTTLE_AXIS = "axis_throttle"

    SCREEN = "screen"
    IMAGE_FRONT_BORDER_LEFT = "image_front.border_left"
    IMAGE_FRONT_BORDER_RIGHT = "image_front.border_right"
    IMAGE_FRONT_BORDER_TOP = "image_front.border_top"
    IMAGE_FRONT_BORDER_BOTTOM = "image_front.border_bottom"

    def __init__(self):
        self.db = Database()

    def get_value(self, key):
        """
        :param key:
        :return: Returns settings value or None if the key does not exist
        """
        result = self.db.execute("SELECT value FROM settings WHERE key=?", (key,))
        if len(result) > 0 and result != "ERROR":
            try:
                return int(result[0][0])
            except Exception:
                return result[0][0]
        else:
            return None

    def set_value(self, key, value):
        if self.get_value(key) is None:
            self.db.execute("INSERT INTO settings (key, value) VALUES (?,?)", (key, value,))
        else:
            self.db.execute("UPDATE settings SET value=? WHERE key=?", (value, key,))

    def delete_entry(self, key):
        self.db.execute("DELETE FROM settings WHERE key=?", (key,))


class Data(object):
    def __init__(self, batch=False):
        self.db = Database(batch)
        self.settings = Settings()

    def append(self):
        self.db.commit()

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

    def get_country_code(self, cid):
        """
        :param cid: country id
        :return: country code
        """
        code = self.db.execute("SELECT code FROM country WHERE id=?", (cid,))
        if len(code) > 0:
            return code[0][0]
        else:
            return None

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
        self.db.execute("INSERT INTO image (filename, steering, speed, throttle, maneuver, sequence) "
                        "VALUES (?,?,?,?,?,?)", (filename, steering, speed, throttle, maneuver, sequence,))

    def set_image_maneuver(self, filename, maneuver):
        self.db.execute("UPDATE image SET maneuver=? WHERE filename=?", (maneuver, filename,))

    def delete_image(self, filename):
        self.db.execute("DELETE FROM image WHERE filename=?", (filename,))

        if os.path.exists(os.path.join("captured", filename)):
            os.remove(os.path.join("captured", filename))

    def get_image_list(self, sequence):
        """
        :param sequence: id of sequence
        :return: List with all images of a sequence
        """
        result = self.db.execute("SELECT id, filename, steering, speed, throttle, maneuver FROM image WHERE sequence=?", (sequence,))
        if type(result) == str and result.startswith("ERROR"):
            return []
        else:
            return result

    def get_image_data(self, imgid):
        result = self.db.execute("SELECT id, filename, steering, speed, throttle, maneuver FROM image WHERE id=?",
                                 (imgid,))
        if type(result) == str and result.startswith("ERROR"):
            return []
        else:
            if len(result) > 0:
                return result[0]
            else:
                return []

    def get_next_fileid(self):
        result = self.db.execute("SELECT filename FROM image ORDER BY id DESC LIMIT 1")
        if result is None or len(result) == 0:
            return 0
        else:
            filename = result[0][0]
            return int(filename.split(".png")[0])+1

    def get_image_list_filter(self, country=None, maneuver=None):
        sql_where = ""
        sql_conditions = []
        sql_condition_values = []
        if country is not None:
            sql_where = " WHERE "
            sql_conditions.append("cty.code=?")
            sql_condition_values.append(country)

        if maneuver is not None:
            sql_where = " WHERE "
            sql_conditions.append("img.maneuver=?")
            sql_condition_values.append(maneuver)

        result = self.db.execute("SELECT img.id, img.filename, img.steering, img.speed, img.throttle, img.maneuver, "
                                 "cty.code FROM image img "
                                 "LEFT JOIN sequence seq ON img.sequence = seq.id "
                                 "LEFT JOIN country cty ON cty.id = seq.country "
                                 "%s%s" % (sql_where, " AND ".join(sql_conditions)), tuple(sql_condition_values))
        if type(result) == str and result.startswith("ERROR"):
            return []
        else:
            return result

    def add_sequence(self, country=None, road_type=-1, controller_type=0, note=None, timestamp=None):
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

        if timestamp:
            result = self.db.execute("INSERT INTO sequence (country, type, controller_type, note, timestamp) VALUES (?, ?, ?, ?, ?)", (cid, road_type, controller_type, note, str(timestamp),))
        else:
            result = self.db.execute("INSERT INTO sequence (country, type, controller_type, note) VALUES (?, ?, ?, ?)", (cid, road_type, controller_type, note,))
        return result

    def update_sequence(self, sid, country=None, road_type=None, note=None):
        """
        :param sid: id of sequence you want to update
        :param country: country code
        :param road_type: road type
        :param note: note (up to 45 characters)
        :return:
        """
        if country is not None:
            cid = self.get_country_id(country)
            self.db.execute("UPDATE sequence SET country=? WHERE id=?", (cid, sid,))
        if road_type is not None:
            self.db.execute("UPDATE sequence SET type=? WHERE id=?", (road_type, sid,))
        if note is not None:
            self.db.execute("UPDATE sequence SET note=? WHERE id=?", (note, sid,))

    def delete_sequence(self, sid):
        images = self.get_image_list(sid)
        self.db.execute("DELETE FROM sequence WHERE id=?", (sid,))

        # Remove all files
        for image in images:
            if os.path.exists(os.path.join("captured", image[1])):
                os.remove(os.path.join("captured", image[1]))

    def get_sequence_list(self):
        """
        :return: List with all sequences (id,timestamp,country,type)
        """
        result = self.db.execute("SELECT id, timestamp, country, type, note FROM sequence")
        if type(result) == str and result.startswith("ERROR"):
            return []
        else:
            return result

    def get_sequence_data(self, sid):
        """
        :param sid:
        :return:
        """
        sequence_data = self.db.execute("SELECT id, country, type FROM sequence WHERE id=?", (sid,))
        if len(sequence_data) > 0:
            return sequence_data[0]
        else:
            return None
