import threading
import pygame


class DetectorThread(threading.Thread):
    lock = threading.Lock()
    running = True

    def __init__(self, controller, field):
        threading.Thread.__init__(self, daemon=True)
        with DetectorThread.lock:
            DetectorThread.running = True

        self.controller = controller
        self.field = field

    def stop(self):
        with DetectorThread.lock:
            DetectorThread.running = False

    def run(self):
        if pygame.joystick.get_init():
            pygame.joystick.quit()
        pygame.init()
        pygame.joystick.init()
        joystick = pygame.joystick.Joystick(self.controller)
        joystick.init()
        num_buttons = joystick.get_numbuttons()
        num_axes = joystick.get_numaxes()

        while DetectorThread.running:
            pygame.event.pump()

            for i in range(num_buttons):
                if joystick.get_button(i) == 1:
                    self.field.setText(str(i))
                    self.stop()

            for i in range(num_axes):
                if abs(joystick.get_axis(i)) > 0.3:
                    self.field.setText(str(i))
                    self.stop()
