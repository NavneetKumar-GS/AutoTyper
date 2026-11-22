const API_URL = "http://127.0.0.1:8000";

// Floating HUD inject kar
const hud = document.createElement("div");
hud.id = "autotyper-hud";
hud.innerHTML = `
  <div id="autotyper-status">Ready (Calibrate once)</div>
  <div class="btn-row">
    <button id="btn-calibrate">Calibrate</button>
    <button id="btn-start">Start</button>
    <button id="btn-stop">Stop</button>
  </div>
`;
document.body.appendChild(hud);

const statusEl = document.getElementById("autotyper-status");
let calibStep = 0; // 0 = off, 1 = pick left box, 2 = pick right input box
let hoveredEl = null;

// Visual hover highlight jab calibrate mode on ho
document.addEventListener("mouseover", (e) => {
  if (calibStep === 0 || hud.contains(e.target)) return;
  if (hoveredEl) hoveredEl.classList.remove("autotyper-highlight");
  hoveredEl = e.target;
  hoveredEl.classList.add("autotyper-highlight");
});

// Click karke exact screen coordinates nikalna (DPI scaling ke saath)
document.addEventListener("click", (e) => {
  if (calibStep === 0 || hud.contains(e.target)) return;
  e.preventDefault();
  e.stopPropagation();

  if (hoveredEl) hoveredEl.classList.remove("autotyper-highlight");

  const dpr = window.devicePixelRatio || 1;
  // Viewport se exact OS screen coordinates calculate karna
  const browserBorderX = window.outerWidth - window.innerWidth * dpr;
  const chromeTopHeight = (window.outerHeight - window.innerHeight * dpr) - (browserBorderX / 2);

  const rect = e.target.getBoundingClientRect();
  const screenLeft = Math.round((window.screenX + (browserBorderX / 2) + rect.left * dpr));
  const screenTop = Math.round((window.screenY + chromeTopHeight + rect.top * dpr));
  const screenWidth = Math.round(rect.width * dpr);
  const screenHeight = Math.round(rect.height * dpr);

  if (calibStep === 1) {
    const leftBox = {
      top: screenTop,
      left: screenLeft,
      width: screenWidth,
      height: screenHeight
    };
    chrome.storage.local.set({ left_box: leftBox });
    calibStep = 2;
    statusEl.textContent = "Step 2/2: Click RIGHT typing box";
  } else if (calibStep === 2) {
    const targetClick = [
      Math.round(screenLeft + screenWidth / 2),
      Math.round(screenTop + screenHeight / 2)
    ];
    chrome.storage.local.set({ target_click: targetClick });
    calibStep = 0;
    statusEl.textContent = "Calibrated! Click Start.";
  }
}, true);

document.getElementById("btn-calibrate").addEventListener("click", () => {
  calibStep = 1;
  statusEl.textContent = "Step 1/2: Click LEFT text panel";
});

document.getElementById("btn-start").addEventListener("click", () => {
  chrome.storage.local.get(["left_box", "target_click"], async (data) => {
    if (!data.left_box || !data.target_click) {
      statusEl.textContent = "Error: Click Calibrate first!";
      return;
    }
    statusEl.textContent = "Running... (Click Stop to abort)";
    try {
      await fetch(`${API_URL}/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          left_box: data.left_box,
          target_click: data.target_click
        })
      });
    } catch (err) {
      statusEl.textContent = "Backend offline! Run server.py";
    }
  });
});

document.getElementById("btn-stop").addEventListener("click", async () => {
  statusEl.textContent = "Stopping...";
  await fetch(`${API_URL}/stop`, { method: "POST" });
  statusEl.textContent = "Stopped.";
});