import pyautogui
import time

print("5 second mein Edge browser khol aur LEFT text box ke TOP-LEFT kone par mouse rakh...")
time.sleep(5)
tl = pyautogui.position()
print("TOP-LEFT:", tl)

print("\n5 second mein LEFT text box ke BOTTOM-RIGHT kone par mouse rakh...")
time.sleep(5)
br = pyautogui.position()
print("BOTTOM-RIGHT:", br)

print("\n5 second mein RIGHT typing box ('Start typing here...') ke andar mouse rakh...")
time.sleep(5)
target = pyautogui.position()
print("TARGET BOX:", target)

print("\n================ YE DO LINES COPY KAR LE ================")
print(f'LEFT_BOX = {{"top": {tl.y}, "left": {tl.x}, "width": {br.x - tl.x}, "height": {br.y - tl.y}}}')
print(f'TARGET_CLICK = ({target.x}, {target.y})')
print("==========================================================")