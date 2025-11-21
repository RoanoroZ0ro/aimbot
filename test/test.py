import cv2
import numpy as np
import mss
import pyautogui
import keyboard
import time

# Load the target image you uploaded
target = cv2.imread("target.png", 0)
w, h = target.shape[::-1]

sct = mss.mss()
active = False
distance_threshold = 250  # pixels, change as needed
move_speed = 1  # fraction of distance to move per frame

print("Press Q to toggle detection ON/OFF. Press ESC to quit.")

# Toggle detection with Q
def toggle_active():
    global active
    active = not active
    print("Detection Active:", active)

keyboard.add_hotkey("q", toggle_active)

while True:
    screen = np.array(sct.grab(sct.monitors[1]))
    gray = cv2.cvtColor(screen, cv2.COLOR_BGRA2GRAY)

    # Template matching
    result = cv2.matchTemplate(gray, target, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(result >= threshold)

    found = False
    for pt in zip(*loc[::-1]):
        found = True
        target_x = pt[0] + w//2
        target_y = pt[1] + h//2
        break  # Only track the first match

    if active and found:
        mouse_x, mouse_y = pyautogui.position()
        dx = target_x - mouse_x
        dy = target_y - mouse_y
        distance = (dx**2 + dy**2)**0.5

        if distance < distance_threshold:
            # Move mouse toward the target smoothly
            pyautogui.moveRel(dx*move_speed, dy*move_speed)


    time.sleep(0.01)
