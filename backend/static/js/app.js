const API = {
  separate: "/api/separate",
  job: (id) => `/api/jobs/${id}`,
  download: (id) => `/api/download/${id}`,
};

const els = {
  fileInput: document.getElementById("fileInput"),
  dropzone: document.getElementById("dropzone"),
  browseBtn: document.getElementById("browseBtn"),
  uploadBtn: document.getElementById("uploadBtn"),
  clearBtn: document.getElementById("clearBtn"),
  langBtn: document.getElementById("langBtn"),
  selectedBox: document.getElementById("selectedBox"),
  fileName: document.getElementById("fileName"),
  fileInfo: document.getElementById("fileInfo"),
  formatValue: document.getElementById("formatValue"),
  statusValue: document.getElementById("statusValue"),
  processingBox: document.getElementById("processingBox"),
  processingHint: document.getElementById("processingHint"),
  errorBox: document.getElementById("errorBox"),
  resultBox: document.getElementById("resultBox"),
  trackList: document.getElementById("trackList"),
  downloadLink: document.getElementById("downloadLink"),
};

let currentLang = "en";
let selectedFile = null;
let currentJobId = null;
let pollTimer = null;
let statusKey = "statusIdle";

function t(key) {
  return window.I18N[currentLang][key] ?? window.I18N.en[key] ?? key;
}

function applyLanguage(lang) {
  currentLang = window.I18N[lang] ? lang : "en";
  document.body.dataset.lang = currentLang;

  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.getAttribute("data-i18n");
    const text = t(key);
    if (text) node.textContent = text;
  });

  els.langBtn.textContent = currentLang === "en" ? "EN / RU" : "RU / EN";

  if (selectedFile) {
    els.fileName.textContent = selectedFile.name;
    els.fileInfo.textContent = `${humanSize(selectedFile.size)} · ${selectedFile.type || "unknown type"}`;
    els.formatValue.textContent = (selectedFile.name.split(".").pop() || "—").toUpperCase();
  } else {
    els.fileName.textContent = t("selectedNone");
    els.fileInfo.textContent = t("selectedHint");
    els.formatValue.textContent = "—";
  }

  els.statusValue.textContent = t(statusKey);
  els.downloadLink.textContent = t("download");
  els.processingHint.textContent = t("processingHintUpload");
}

function humanSize(bytes) {
  const units = ["B", "KB", "MB", "GB"];
  let size = bytes;
  let i = 0;
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024;
    i++;
  }
  return `${size.toFixed(size >= 10 || i === 0 ? 0 : 1)} ${units[i]}`;
}

function setStatus(key) {
  statusKey = key;
  els.statusValue.textContent = t(key);
}

function setProcessing(active, hintKey = "processingHintUpload") {
  els.processingBox.classList.toggle("show", active);
  els.processingHint.textContent = t(hintKey);
  els.dropzone.classList.toggle("disabled", active);
  els.uploadBtn.disabled = active || !selectedFile;
  els.browseBtn.disabled = active;
  els.clearBtn.disabled = active;
}

function updateFileUI() {
  if (!selectedFile) {
    els.selectedBox.classList.remove("show");
    els.fileName.textContent = t("selectedNone");
    els.fileInfo.textContent = t("selectedHint");
    els.formatValue.textContent = "—";
    els.uploadBtn.disabled = true;
    return;
  }

  els.selectedBox.classList.add("show");
  els.fileName.textContent = selectedFile.name;
  els.fileInfo.textContent = `${humanSize(selectedFile.size)} · ${selectedFile.type || "unknown type"}`;
  els.formatValue.textContent = (selectedFile.name.split(".").pop() || "—").toUpperCase();
  els.uploadBtn.disabled = false;
}

function resetResult() {
  els.resultBox.classList.remove("show");
  els.trackList.innerHTML = "";
  els.downloadLink.href = "#";
}

function handleFiles(files) {
  const file = files && files[0];
  if (!file) return;

  const ext = (file.name.split(".").pop() || "").toLowerCase();
  if (!["mp3", "wav", "flac"].includes(ext)) {
    showError(t("errFormat"));
    return;
  }

  clearError();
  resetResult();
  selectedFile = file;
  updateFileUI();
  setStatus("statusSelected");
}

function showError(message) {
  els.errorBox.textContent = message;
  els.errorBox.classList.add("show");
}

function clearError() {
  els.errorBox.textContent = "";
  els.errorBox.classList.remove("show");
}

// 1. Initialization when loading the page
// (setting the default language and UI)
document.addEventListener("DOMContentLoaded", () => {
  applyLanguage(currentLang);
});

// 2. Language switching (EN / RU)
els.langBtn.addEventListener("click", () => {
  const nextLang = currentLang === "en" ? "ru" : "en";
  applyLanguage(nextLang);
});

// 3. Opening of the file selection dialog box
// when clicking on "Browse files"
els.browseBtn.addEventListener("click", (e) => {
  // We prevent surfacing so that a click on the drop zone does not work
  e.stopPropagation(); 
  els.fileInput.click();
});

// Clicking on the drop zone area itself also opens the file selection
els.dropzone.addEventListener("click", (e) => {
  // We check that the "Start separation" button was not clicked
  if (els.dropzone.classList.contains("disabled") || e.target === els.uploadBtn) return;
  els.fileInput.click();
});

// 4. Processing file selection via standard file Explorer
els.fileInput.addEventListener("change", () => {
  handleFiles(els.fileInput.files);
});

// 5. The button for cleaning the selected file (Remove)
els.clearBtn.addEventListener("click", () => {
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = null;
  currentJobId = null;
  selectedFile = null;
  els.fileInput.value = "";
  clearError();
  setProcessing(false);
  resetResult();
  updateFileUI();
  setStatus("statusIdle");
});

// 6. Drag & Drop logic for the drop zone
// Preventing default browser behavior (opening a file in a new tab)
["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
  els.dropzone.addEventListener(eventName, (e) => {
    e.preventDefault();
    e.stopPropagation();
  }, false);
});

// Highlighting a zone when dragging a file over it
["dragenter", "dragover"].forEach((eventName) => {
  els.dropzone.addEventListener(eventName, () => {
    if (!els.dropzone.classList.contains("disabled")) {
      els.dropzone.classList.add("dragover");
    }
  }, false);
});

// We turn off the backlight when the file flies out of the zone or is reset
["dragleave", "drop"].forEach((eventName) => {
  els.dropzone.addEventListener(eventName, () => {
    els.dropzone.classList.remove("dragover");
  }, false);
});

// Catching the dropped file
els.dropzone.addEventListener("drop", (e) => {
  if (els.dropzone.classList.contains("disabled")) return;
  
  const dt = e.dataTransfer;
  const files = dt.files;
  handleFiles(files);
});

// 7. Processing of sending a file to the backend ("Start separation" button)
els.uploadBtn.addEventListener("click", async () => {
  if (!selectedFile || els.dropzone.classList.contains("disabled")) return;

  try {
    clearError();
    setProcessing(true, "processingHintUpload");
    setStatus("statusUploading");

    // Creating a multipart/form-data for sending the file
    const formData = new FormData();
    formData.append("file", selectedFile);

    const response = await fetch(API.separate, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    // We assume that the backend returns the task ID in data.job_id or data.id
    currentJobId = data.job_id || data.id;
    
    setProcessing(true, "processingHintWork");
    setStatus("statusUploading");

    // Celery task status polling method should be called here
    startPolling(currentJobId);

  } catch (err) {
    console.error(err);
    showError(err.message || t("errUpload"));
    setStatus("statusError");
    setProcessing(false);
  }
});

function startPolling(jobId) {
  // Just in case, we clear the old timer
  if (pollTimer) clearInterval(pollTimer);

  async function tick() {
    try {
      const response = await fetch(API.job(jobId));

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();

      // We check the status of the task (adapt it to the scheme of your
      // backend, for example, "SUCCESS"/"FAILURE" or "completed"/"failed")
      if (data.status === "completed" || data.status === "SUCCESS") {
        clearInterval(pollTimer);

        setProcessing(false);
        setStatus("statusCompleted");
        // Passing an object with links to tracks
        // (for example, data.stems or data.tracks)
        displayResults(data.stems || {}, jobId);

      } else if (data.status === "failed" || data.status === "FAILURE") {
        clearInterval(pollTimer);
        setProcessing(false);
        setStatus("statusFailed");
        showError(data.error || t("errFailed"));
      } else {
        // The task is still running in Celery
        setStatus("statusUploading");
        setProcessing(true, "processingHintWork");
      }
    } catch (err) {
      clearInterval(pollTimer);
      setProcessing(false);
      setStatus("statusError");
      showError(err.message || t("errConnection"));
    }
  }

  tick();
  pollTimer = setInterval(tick, 3000);
}

/**
 * Generates audio players for the received tracks and shows a block of results
 */
function displayResults(stems, jobId) {
  els.trackList.innerHTML = ""; // Clearing old results

  const stemKeys = Object.keys(stems);

  if (stemKeys.length === 0) {
    // If backend has not returned the tracks, we output a warning from i18n
    const emptyMsg = document.createElement("div");
    emptyMsg.className = "muted";
    emptyMsg.style.padding = "10px 0";
    emptyMsg.textContent = t("noTracksYet");
    els.trackList.appendChild(emptyMsg);
  } else {
    // Dynamically create markup for each audio track (Vocals, Drums, etc.)
    stemKeys.forEach((key) => {
      const trackUrl = stems[key]; // The URL to the audio file on the backend
      
      const trackEl = document.createElement("div");
      trackEl.className = "track";
      trackEl.innerHTML = `
        <div class="track-head">
          <span class="track-name">${key.toUpperCase()}</span>
        </div>
        <audio controls src="${trackUrl}"></audio>
      `;
      els.trackList.appendChild(trackEl);
    });
  }

  // Updating the download link for the entire ZIP archive
  els.downloadLink.href = API.download(jobId);

  els.resultBox.classList.add("show");
}

// Keyboard accessibility for dropzone
els.dropzone.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    if (!els.dropzone.classList.contains("disabled")) {
      els.fileInput.click();
    }
  }
});
