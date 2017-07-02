import pygame

pygame.init()
pygame.joystick.init()

joystick_count = pygame.joystick.get_count()
if joystick_count == 0:
    print("No joysticks found.")
    exit(0)

for i in range(joystick_count):
    print("%d - %s" % (i, pygame.joystick.Joystick(i).get_name()))

try:
    joystick_id = int(input("Choose a joystick: "))
except ValueError:
    print("Incorrect input. Only numbers are allowed.")
    exit(1)

if joystick_id > joystick_count:
    print("Joystick ID is invalid.")
    exit(0)

joystick = pygame.joystick.Joystick(joystick_id)
joystick.init()
num_buttons = joystick.get_numbuttons()
num_axes = joystick.get_numaxes()

while(True):
    pygame.event.pump()

    for i in range(num_buttons):
        if joystick.get_button(i) == 1:
            print("Button %d is pressed." % i)

    for i in range(num_axes):
        if abs(joystick.get_axis(i)) > 0.3:
            print("Axis %d is in use." % i)
