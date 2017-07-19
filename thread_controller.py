import threading
import pygame
import pyvjoy
from database import Settings


class ControllerThread(threading.Thread):
    print_lock = threading.Lock()
    running = True

    def __init__(self):
        threading.Thread.__init__(self)
        ControllerThread.running = True
        self.controller = int(Settings().get_value(Settings.CONTROLLER))
        self.vjoy = int(Settings().get_value(Settings.VJOY_DEVICE))
        self.axis = int(Settings().get_value(Settings.STEERING_AXIS))
        self.running = True
        self.autopilot = False
        self.angle = 0

    def stop(self):
        with ControllerThread.print_lock:
            ControllerThread.running = False

    def run(self):
        pygame.init()
        pygame.joystick.init()
        joystick = pygame.joystick.Joystick(self.controller)
        joystick.init()
        vjoy = pyvjoy.VJoyDevice(self.vjoy)
        vjoy.reset()

        while ControllerThread.running:
            pygame.event.pump()
            if not self.autopilot:
                angle = round((joystick.get_axis(self.axis) + 1) * 32768 / 2)
            else:
                angle = self.angle

            vjoy.set_axis(pyvjoy.HID_USAGE_Y, angle)

    def is_running(self):
        return self.running

    def set_autopilot(self, value):
        self.autopilot = value

    def set_angle(self, value):
        self.angle = value
