const statusEl = document.getElementById("status");
const statusDot = document.getElementById("status-dot");

const slots = {};

function setStatus(state, text) {
  statusDot.className = state;
  statusEl.textContent = text;
}

function getContainer(source) {
  if (source === "microphone") return document.getElementById("mic-captions");
  return document.getElementById("sys-captions");
}

function makeRow(source) {
  const row = document.createElement("div");
  row.className = "caption-row caption-partial";

  const label = document.createElement("span");
  label.className = "source-label source-" + source;
  label.textContent = source === "microphone" ? "mic" : "sys";

  const text = document.createElement("span");
  text.className = "caption-text";

  row.appendChild(label);
  row.appendChild(text);
  return row;
}

function handleMessage(item) {
  const uid = item.utterance_id;
  const container = getContainer(item.source);
  if (!container) return;

  if (!slots[uid]) {
    const row = makeRow(item.source);
    container.insertBefore(row, container.firstChild);
    const rows = container.querySelectorAll(".caption-row");
    if (rows.length > 30) rows[rows.length - 1].remove();
    slots[uid] = { row: row, whisper_done: false };
  }

  const slot = slots[uid];
  const textEl = slot.row.querySelector(".caption-text");

  if (item.engine === "vosk" && !slot.whisper_done) {
    textEl.textContent = item.text;
    slot.row.className = item.is_final
      ? "caption-row caption-vosk-done"
      : "caption-row caption-partial";
  }

  if (item.engine === "whisper") {
    textEl.textContent = item.text;
    slot.row.className = "caption-row caption-whisper-done";
    slot.whisper_done = true;
    delete slots[uid];
  }
}

const socket = new WebSocket("ws://127.0.0.1:8000/captions");

socket.onopen = function () {
  setStatus("connected", "Connected, listening");
};

socket.onmessage = function (event) {
  handleMessage(JSON.parse(event.data));
};

socket.onclose = function () {
  setStatus("disconnected", "Disconnected, restart the backend");
};

socket.onerror = function () {
  setStatus("disconnected", "Could not connect, check the backend is running");
};

