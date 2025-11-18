import pygame

# Initialize Pygame and Joystick
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    raise Exception("No joystick detected!")

joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Joystick name: {joystick.get_name()}")
print(f"Number of axes: {joystick.get_numaxes()}")
print(f"Number of buttons: {joystick.get_numbuttons()}")

try:
    print("Press Ctrl+C to exit.")
    while True:
        pygame.event.pump()

        # Read axes
        axis_values = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
        # Read buttons
        button_values = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]

        # Display values
        print("\rAxes:", ["{:.2f}".format(a) for a in axis_values], end=" | ")
        print("Buttons:", button_values, end="")

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    pygame.quit()
