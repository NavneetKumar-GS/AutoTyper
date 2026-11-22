# AutoTyper Setup & Daily Workflow Guide

## 1. Initial Setup (On a New Laptop)

1. **Copy Project Folders:** Copy both `backend/` (including your `.env` file) and `extension/` folders to the target machine.
2. **Install Python Dependencies:**
   Open a terminal inside the `backend/` folder and run:
   ```bash
   pip install -r requirements.txt
   ```
   *(If using `uv`: `uv pip install -r requirements.txt`)*
3. **Verify `.env` File:** Ensure `backend/.env` contains your valid API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```
4. **Load Chrome Extension:**
   - Open Chrome and go to `chrome://extensions`
   - Enable **Developer mode** (top-right toggle).
   - Click **Load unpacked** and select the `extension/` folder.

---

## 2. Daily Operation Workflow

### Step 1: Start the Local Backend
Open a terminal in the `backend/` directory and start the FastAPI server:
```bash
uvicorn server:app --host 127.0.0.1 --port 8000
```
*(Or with `uv`: `uv run uvicorn server:app`)*
Minimize the terminal window once it shows `Uvicorn running on http://127.0.0.1:8000`.

### Step 2: Open Portal & Calibrate (Once per Session)
1. Open the target web portal in Chrome and maximize/position the browser window where you plan to keep it.
2. Look at the bottom-right corner of the webpage for the **AutoTyper HUD** (`Calibrate | Start | Stop`).
3. Click **Calibrate**:
   - **Step 1/2:** Hover over the **left scrollable text container** (wait for the blue dashed outline) and click it.
   - **Step 2/2:** Hover over the **right typing/input box** and click it.
   - *Note: Coordinates are saved automatically in Chrome storage. You only need to recalibrate if you resize or move the Chrome window.*

### Step 3: Process Pages (Target: 20+ Pages/Session)
1. Click **Start** on the HUD.
2. **Hands off mouse/keyboard** for ~3–5 seconds while the script captures the 2x2 grid screenshots and merges text via Gemini.
3. Once typing begins, let it complete (~1.5 mins per page).
4. **Quick Verification:** Glance at the final few lines to ensure no text was cut off at the bottom/right scroll limits, then manually click **Submit**.
5. On the next page, click **Start** again.

---

## 3. Troubleshooting & Tuning

- **Emergency Stop:** Click the red **Stop** button on the HUD, or simply click outside the Chrome window (the focus-guard will immediately halt typing).
- **Text Cut Off at Right/Bottom Edges:** Open `backend/server.py` and increase the scroll distances in `JobRequest`:
  - `h_scroll: int = -1600` (default `-1200`)
  - `v_scroll: int = -1200` (default `-800`)
- **HUD Not Visible:** Refresh the webpage (`F5`). Extensions do not inject into `chrome://` pages.