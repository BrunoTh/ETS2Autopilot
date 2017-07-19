import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
print("Loading...")
from UI.main import MainUI
from database import Settings


dbs = Settings()

# MIGRATE
if not dbs.get_value("migrated"):
    print("Migrating data. This may take a while...")
    if os.path.exists("captured/data.txt") and os.path.exists("captured/sequence.txt"):
        import migrate
        migrate.migrate()

    if os.path.exists("settings.py"):
        import settings as s
        dbs.set_value(dbs.CONTROLLER, s.JOYSTICK)
        dbs.set_value(dbs.VJOY_DEVICE, s.VJOY_DEVICE)
        dbs.set_value(dbs.AUTOPILOT_SOUND_ACTIVATE, s.AUTOPILOT_SOUND_ACTIVATE)
        dbs.set_value(dbs.ADAPTIVE_STEERING, s.ADAPTIVE_STEERING)
        dbs.set_value(dbs.AUTOPILOT, s.AUTOPILOT_BUTTON)
        dbs.set_value(dbs.STEERING_AXIS, s.STEERING_AXIS)
        dbs.set_value(dbs.THROTTLE_AXIS, s.THROTTLE_AXIS)
        dbs.set_value(dbs.LEFT_INDICATOR, s.INDICATOR_LEFT_BUTTON)
        dbs.set_value(dbs.RIGHT_INDICATOR, s.INDICATOR_RIGHT_BUTTON)
        dbs.set_value(dbs.COUNTRY_DEFAULT, s.COUNTRY_CODE)
        dbs.set_value(dbs.COUNTRIES_MODEL, ",".join(s.COUNTRY))
        dbs.set_value(dbs.IMAGE_FRONT_BORDER_LEFT, s.IMAGE_FRONT_X[0])
        dbs.set_value(dbs.IMAGE_FRONT_BORDER_RIGHT, s.IMAGE_FRONT_X[1])
        dbs.set_value(dbs.IMAGE_FRONT_BORDER_TOP, s.IMAGE_FRONT_Y[0])
        dbs.set_value(dbs.IMAGE_FRONT_BORDER_BOTTOM, s.IMAGE_FRONT_Y[1])

    dbs.set_value("migrated", 1)

# START APPLICATION
app = QApplication(sys.argv)
main = MainUI()
main.show()
sys.exit(app.exec_())
