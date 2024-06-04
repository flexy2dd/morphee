
import RPi.GPIO as GPIO
import board
import time

SW_PIN = 20

#prev_button_state = GPIO.HIGH

## Configure GPIO pins
print("setup SW_PIN")
GPIO.setup(SW_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Read the initial state of the rotary encoder's CLK pin")

# Read the initial state of the rotary encoder's CLK pin
prev_button_state = GPIO.input(SW_PIN)

try:
    while True:
        # State change detection for the button
        button_state = GPIO.input(SW_PIN)
        if button_state != prev_button_state:
            time.sleep(0.01)  # Add a small delay to debounce
            if button_state == GPIO.LOW:
                print("The button is pressed")
                button_pressed = True
            else:
                button_pressed = False
                print("The button is NOT pressed")

        prev_button_state = button_state
except KeyboardInterrupt:
    GPIO.cleanup()  # Clean up GPIO on program exit

