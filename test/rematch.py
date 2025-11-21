import cv2
import numpy as np
import mss
import pyautogui
import keyboard
import tkinter as tk
import sys
import math

# -----------------------
# Load target images
# -----------------------
target_files = [
"target1.png","target2.png","target3.png","target4.png",
    "target5.png","target6.png","target7.png","target8.png",
    "target9.png","target10.png","target11.png","target12.png",
    "target13.png","target14.png","target15.png","target16.png",
    "target17.png","target18.png","target19.png","target20.png",
    "target21.png","target22.png","target23.png","target24.png",
    "target25.png","target26.png","target27.png","target28.png"
]

targets = []
target_sizes = []

for f in target_files:
    t = cv2.imread(f, 0)
    if t is None:
        print(f"[!] Could not load {f}")
    else:
        targets.append(t)
        target_sizes.append(t.shape[::-1])

if not targets:
    raise ValueError("No target images loaded! Check file paths.")

# -----------------------
# Settings
# -----------------------
sct = mss.mss()
active = False
running = True
distance_threshold = 150  # pixels
detection_threshold = 0.85
scales = [1.0, 0.9, 1.1]

# -----------------------
# Tkinter overlay setup
# -----------------------
screen_width, screen_height = pyautogui.size()
root = tk.Tk()
root.attributes("-topmost", True)
root.geometry(f"{screen_width}x{screen_height}+0+0")
root.overrideredirect(True)

# Canvas with white background (will be transparent)
canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg='white', highlightthickness=0)
canvas.pack()

# Make white transparent
root.attributes("-transparentcolor", "white")

status_label = tk.Label(root, text="Status: Paused | Hotkeys: Q=Toggle, ESC=Quit",
                        font=("Arial", 16), fg="blue", bg="white")
status_label.place(x=10, y=10)

# -----------------------
# Hotkeys
# -----------------------
def toggle_active(event=None):
    global active
    active = not active

def quit_program(event=None):
    global running
    running = False
    root.destroy()
    sys.exit()

keyboard.add_hotkey("q", toggle_active)
keyboard.add_hotkey("esc", quit_program)

# -----------------------
# Drag function
# -----------------------
def drag_to(x, y):
    pyautogui.mouseDown()
    pyautogui.moveTo(x, y, duration=0.2)
    pyautogui.mouseUp()

# -----------------------
# Update overlay
# -----------------------
def update_status():
    if not running:
        return
    status_label.config(text=f"Status: {'Active' if active else 'Paused'} | Hotkeys: Q=Toggle, ESC=Quit")
    root.after(100, update_status)

# -----------------------
# Detection loop
# -----------------------
def detection_loop():
    if not running:
        return

    screen = np.array(sct.grab(sct.monitors[1]))
    gray = cv2.cvtColor(screen, cv2.COLOR_BGRA2GRAY)

    canvas.delete("box")
    detected_any = False

    mouse_x, mouse_y = pyautogui.position()

    for target, (w, h) in zip(targets, target_sizes):
        for scale in scales:
            resized = cv2.resize(target, (int(w*scale), int(h*scale)))
            res_w, res_h = resized.shape[::-1]

            result = cv2.matchTemplate(gray, resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= detection_threshold:
                center_x = max_loc[0] + res_w // 2
                center_y = max_loc[1] + res_h // 4  # head area

                detected_any = True

                # Green box
                canvas.create_rectangle(max_loc[0], max_loc[1],
                                        max_loc[0]+res_w, max_loc[1]+res_h,
                                        outline="green", width=2, tags="box")
                # Detected text
                canvas.create_text(center_x, max_loc[1]-10,
                                   text="Detected!", fill="green", font=("Arial", 14), tags="box")
                # Distance line
                canvas.create_line(mouse_x, mouse_y, center_x, center_y, fill="red", width=2, tags="box")

                # Drag if active and within distance
                distance = math.hypot(center_x - mouse_x, center_y - mouse_y)
                if active and distance <= distance_threshold:
                    drag_to(center_x, center_y)

                break
        if detected_any:
            break

    root.after(10, detection_loop)

# -----------------------
# Start loops
# -----------------------
root.after(0, update_status)
root.after(0, detection_loop)
root.mainloop()
