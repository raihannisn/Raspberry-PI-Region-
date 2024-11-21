import cv2
import RPi.GPIO as GPIO
import time

# Initialize GPIO for stepper motor control
# Modify these pins based on your stepper motor driver and connections
DIR_PIN = 17
STEP_PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(STEP_PIN, GPIO.OUT)

# Initialize OpenCV
cap = cv2.VideoCapture(0)  # Change to the appropriate video source index

# Initialize variables
prev_focus_value = 0

def calculate_focus(frame):
    # Use Laplacian variance as a focus metric
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def move_stepper(direction):
    GPIO.output(DIR_PIN, direction)
    GPIO.output(STEP_PIN, GPIO.HIGH)
    time.sleep(0.005)  # Adjust sleep time based on your motor and speed
    GPIO.output(STEP_PIN, GPIO.LOW)
    time.sleep(0.005)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        focus_value = calculate_focus(frame)

        if focus_value < prev_focus_value:
            move_stepper(GPIO.HIGH)  # Move in one direction
        else:
            move_stepper(GPIO.LOW)   # Move in the opposite direction

        prev_focus_value = focus_value

except KeyboardInterrupt:
    pass

finally:
    cap.release()
    GPIO.cleanup()