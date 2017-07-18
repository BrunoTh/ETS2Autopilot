import threading
import pygame
import pyvjoy
from database import Settings


class ControllerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.controller = Settings().get_value(Settings.CONTROLLER)
        self.vjoy = Settings().get_value(Settings.VJOY_DEVICE)
        self.axis = Settings().get_value(Settings.STEERING_AXIS)
        self.running = True
        self.autopilot = False
        self.angle = 0

        pygame.init()
        pygame.joystick.init()

    def run(self):
        joystick = pygame.joystick.Joystick(self.controller)
        joystick.init()
        vjoy = pyvjoy.VJoyDevice(self.vjoy)
        vjoy.reset()

        while(self.running):
            pygame.event.pump()
            if not self.autopilot:
                angle = round((joystick.get_axis(self.axis) + 1) * 32768 / 2)
            else:
                angle = self.angle

            vjoy.set_axis(pyvjoy.HID_USAGE_Y, angle)

    def stop(self):
        self.running = False

    def is_running(self):
        return self.running

    def set_autopilot(self, value):
        self.autopilot = value

    def set_angle(self, value):
        self.angle = value
