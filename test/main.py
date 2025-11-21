import cv2
import numpy as np
import mss
import keyboard
import time

# Load the target image
target = cv2.imread("target.png", 0)
w, h = target.shape[::-1]

sct = mss.mss()
previous_pos = None
active = False

print("Press Q to toggle detection ON/OFF. Press ESC to quit.")

# Define hotkey to toggle detection
def toggle_active():
    global active, previous_pos
    active = not active
    previous_pos = None
    print("ACTIVE:", active)

keyboard.add_hotkey("q", toggle_active)

while True:
    # Capture full screen
    screen = np.array(sct.grab(sct.monitors[1]))
    gray = cv2.cvtColor(screen, cv2.COLOR_BGRA2GRAY)

    if active:
        # Template matching
        result = cv2.matchTemplate(gray, target, cv2.TM_CCOEFF_NORMED)
        threshold = 0.75
        loc = np.where(result >= threshold)

        moved = False
        found = False

        for pt in zip(*loc[::-1]):
            found = True

            if previous_pos is not None:
                dx = abs(pt[0] - previous_pos[0])
                dy = abs(pt[1] - previous_pos[1])
                if dx > 5 or dy > 5:
                    moved = True

            previous_pos = pt
            break  # Only track the first match

        if found and moved:
            print("Target moved! Position:", previous_pos)

    # Exit if ESC is pressed
    if keyboard.is_pressed("esc"):
        print("Exiting...")
        break

    time.sleep(0.01)  # Slight delay to reduce CPU usage
