const statusEl = document.getElementById("status");
const captionsEl = document.getElementById("captions");

function addCaption(item) {
  const row = document.createElement("div");
  row.className = "caption-row";

  const label = document.createElement("span");
  label.className = "source-label source-" + item.source;
  label.textContent = item.source;

  const text = document.createElement("span");
  text.className = "caption-text";
  text.textContent = item.text;

  row.appendChild(label);
  row.appendChild(text);

  captionsEl.insertBefore(row, captionsEl.firstChild);
}

const socket = new WebSocket("ws://127.0.0.1:8000/captions");

socket.onopen = function () {
  statusEl.textContent = "Connected, listening";
};

socket.onmessage = function (event) {
  const item = JSON.parse(event.data);
  addCaption(item);
};

socket.onclose = function () {
  statusEl.textContent = "Disconnected, start the backend and reopen this popup";
};

socket.onerror = function () {
  statusEl.textContent = "Could not connect, check the backend is running";
};


