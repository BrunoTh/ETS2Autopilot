import threading
import pygame
import pyvjoy
from database import Settings


class ControllerThread(threading.Thread):
    print_lock = threading.Lock()
    running = True
    angle = 0

    def __init__(self):
        threading.Thread.__init__(self)
        ControllerThread.running = True
        self.controller = Settings().get_value(Settings.CONTROLLER)
        self.vjoy = Settings().get_value(Settings.VJOY_DEVICE)
        self.axis = Settings().get_value(Settings.STEERING_AXIS)
        self.running = True
        self.autopilot = False
        self.angle = 0

    def stop(self):
        with ControllerThread.print_lock:
            ControllerThread.running = False

    def run(self):
        if pygame.joystick.get_init():
            pygame.joystick.quit()
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
                angle = ControllerThread.angle

            vjoy.set_axis(pyvjoy.HID_USAGE_Y, angle)

    def is_running(self):
        return self.running

    def set_autopilot(self, value):
        self.autopilot = value

    def set_angle(self, value):
        with ControllerThread.print_lock:
            ControllerThread.angle = value
