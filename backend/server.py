import os
import time
import random
import threading
import mss
import pyautogui
import pygetwindow as gw
from PIL import Image
from pynput.keyboard import Controller, Key
from dotenv import load_dotenv
from google import genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = genai.Client()
keyboard = Controller()
stop_flag = False
is_running = False

class JobRequest(BaseModel):
    left_box: dict      # {"top": int, "left": int, "width": int, "height": int}
    target_click: list  # [x, y]
    h_scroll: int = -1200
    v_scroll: int = -800

def capture_left_panel(left_box, h_scroll, v_scroll):
    cx = left_box["left"] + left_box["width"] // 2
    cy = left_box["top"] + left_box["height"] // 2
    pyautogui.moveTo(cx, cy)

    with mss.mss() as sct:
        # 1. Top-Left
        raw1 = sct.grab(left_box)
        img_tl = Image.frombytes("RGB", raw1.size, raw1.bgra, "raw", "BGRX")

        # 2. Top-Right
        pyautogui.keyDown("shift")
        pyautogui.scroll(h_scroll)
        pyautogui.keyUp("shift")
        time.sleep(0.4)
        raw2 = sct.grab(left_box)
        img_tr = Image.frombytes("RGB", raw2.size, raw2.bgra, "raw", "BGRX")

        # 3. Reset horizontal + Scroll down to Bottom-Left
        pyautogui.keyDown("shift")
        pyautogui.scroll(-h_scroll)
        pyautogui.keyUp("shift")
        time.sleep(0.3)

        pyautogui.scroll(v_scroll)
        time.sleep(0.4)
        raw3 = sct.grab(left_box)
        img_bl = Image.frombytes("RGB", raw3.size, raw3.bgra, "raw", "BGRX")

        # 4. Bottom-Right
        pyautogui.keyDown("shift")
        pyautogui.scroll(h_scroll)
        pyautogui.keyUp("shift")
        time.sleep(0.4)
        raw4 = sct.grab(left_box)
        img_br = Image.frombytes("RGB", raw4.size, raw4.bgra, "raw", "BGRX")

        # 5. Reset scrolls
        pyautogui.keyDown("shift")
        pyautogui.scroll(-h_scroll)
        pyautogui.keyUp("shift")
        pyautogui.scroll(-v_scroll)

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

def run_pipeline(job: JobRequest):
    global stop_flag, is_running
    is_running = True
    stop_flag = False

    try:
        print("[1/3] Capturing 2x2 grid...")
        images = capture_left_panel(job.left_box, job.h_scroll, job.v_scroll)
        if stop_flag:
            return

        print("[2/3] Extracting text via Gemini...")
        clean_text = extract_and_merge_text(images)
        if stop_flag:
            return

        print(f"[3/3] Typing {len(clean_text)} chars...")
        pyautogui.click(job.target_click[0], job.target_click[1])
        time.sleep(0.3)

        locked_win = gw.getActiveWindow()
        locked_title = locked_win.title if locked_win else ""

        for char in clean_text:
            if stop_flag:
                print("[STOPPED] Aborted via Extension button.")
                return

            current_win = gw.getActiveWindow()
            if current_win is None or current_win.title != locked_title:
                print("[STOPPED] Window lost focus.")
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

        print("[DONE] Page finished.")
    finally:
        is_running = False

@app.post("/start")
def start_typing(job: JobRequest):
    if is_running:
        return {"status": "already_running"}
    threading.Thread(target=run_pipeline, args=(job,), daemon=True).start()
    return {"status": "started"}

@app.post("/stop")
def stop_typing():
    global stop_flag
    stop_flag = True
    return {"status": "stopping"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)