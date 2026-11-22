import os
import time
import random
import mss
import pyautogui
import pygetwindow as gw
import keyboard as hotkey_listener
from PIL import Image
from pynput.keyboard import Controller, Key
from dotenv import load_dotenv
from google import genai

load_dotenv()

LEFT_BOX = {"top": 217, "left": 7, "width": 1397, "height": 1572}
TARGET_CLICK = (2379, 640)
SCROLL_AMOUNT = -1200    # Horizontal scroll (right)
V_SCROLL_AMOUNT = -800

client = genai.Client()
keyboard = Controller()

def capture_left_panel():
    cx = LEFT_BOX["left"] + LEFT_BOX["width"] // 2
    cy = LEFT_BOX["top"] + LEFT_BOX["height"] // 2
    pyautogui.moveTo(cx, cy)

    with mss.mss() as sct:
        # 1. Top-Left
        raw1 = sct.grab(LEFT_BOX)
        img_tl = Image.frombytes("RGB", raw1.size, raw1.bgra, "raw", "BGRX")

        # 2. Top-Right (Horizontal scroll right)
        pyautogui.keyDown("shift")
        pyautogui.scroll(SCROLL_AMOUNT)
        pyautogui.keyUp("shift")
        time.sleep(0.4)
        raw2 = sct.grab(LEFT_BOX)
        img_tr = Image.frombytes("RGB", raw2.size, raw2.bgra, "raw", "BGRX")

        # 3. Reset horizontal scroll + Scroll Down to Bottom-Left
        pyautogui.keyDown("shift")
        pyautogui.scroll(-SCROLL_AMOUNT)
        pyautogui.keyUp("shift")
        time.sleep(0.3)

        pyautogui.scroll(V_SCROLL_AMOUNT)
        time.sleep(0.4)
        raw3 = sct.grab(LEFT_BOX)
        img_bl = Image.frombytes("RGB", raw3.size, raw3.bgra, "raw", "BGRX")

        # 4. Bottom-Right (Horizontal scroll right)
        pyautogui.keyDown("shift")
        pyautogui.scroll(SCROLL_AMOUNT)
        pyautogui.keyUp("shift")
        time.sleep(0.4)
        raw4 = sct.grab(LEFT_BOX)
        img_br = Image.frombytes("RGB", raw4.size, raw4.bgra, "raw", "BGRX")

        # 5. Reset both scrolls back to Top-Left
        pyautogui.keyDown("shift")
        pyautogui.scroll(-SCROLL_AMOUNT)
        pyautogui.keyUp("shift")
        pyautogui.scroll(-V_SCROLL_AMOUNT)

    return [img_tl, img_tr, img_bl, img_br]

def extract_and_merge_text(images):
    prompt = (
        "These 4 screenshots show a 2x2 grid (Top-Left, Top-Right, Bottom-Left, Bottom-Right) "
        "of the same scrollable text box with overlapping text horizontally and vertically. "
        "Transcribe the ENTIRE text verbatim from the very first line to the very last line. "
        "Merge lines horizontally and stitch paragraphs vertically without duplicating any overlapping words or lines. "
        "Preserve exact punctuation, capitalization, and line breaks. Output ONLY the final merged text."
    )
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=[*images, prompt]
    )
    return response.text.strip()

# def is_edge_active():
#     win = gw.getActiveWindow()
#     return win is not None and "Edge" in win.title

def human_type(text):
    pyautogui.click(TARGET_CLICK[0], TARGET_CLICK[1])
    time.sleep(0.3)

    for char in text:
        if hotkey_listener.is_pressed("esc"):
            print("\n[STOPPED] ESC pressed.")
            return

        if char == "\n":
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
            time.sleep(random.uniform(0.08, 0.15))
        else:
            keyboard.type(char)
            delay = random.uniform(0.025, 0.06)
            if char in " .,;":
                delay += random.uniform(0.02, 0.04)
            time.sleep(delay)

if __name__ == "__main__":
    print("[READY] F8 = Start | ESC = Stop | Auto-stops if you leave target window.")

    while True:
        hotkey_listener.wait("f8")
        print("\n[F8] Capturing 2x2 grid screenshots...")
        images = capture_left_panel()

        print("[AI] Extracting and merging text...")
        clean_text = extract_and_merge_text(images)
        print(f"[TYPING] {len(clean_text)} chars... (Press ESC to stop)")

        human_type(clean_text)
        print("[DONE] Review and submit. Press F8 on the next page.")
        time.sleep(1)