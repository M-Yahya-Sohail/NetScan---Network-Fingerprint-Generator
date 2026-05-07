let charts = {};

// --- HELPER: VALIDATE URL ---
function validateURL(url) {
  return /^https?:\/\/.+\..+/.test(url);
}

// --- HELPER: FORMAT BYTES ---
function formatBytes(b) {
  if (b === 0) return "0 B";
  return b < 1048576
    ? (b / 1024).toFixed(1) + " KB"
    : (b / 1048576).toFixed(1) + " MB";
}

// --- UI CONTROL ---
function showLoading(show, duration = 10) {
  const loader = document.getElementById("loadingSection");
  const progressFill = document.getElementById("progressFill");
  const progressPct = document.getElementById("progressPct");
  const caption = document.getElementById("loadingCaption");

  if (show) {
    loader.classList.add("visible");
    document.getElementById("resultsSection").classList.remove("visible");
    document.getElementById("homeView").style.display = "none";
    document.getElementById("inputSection").style.display = "none";

    // Progress bar aur text reset karein
    caption.innerText = `Capturing Live Packets (${duration}s window)`;
    animateProgressBar(duration * 1000); // ms mein convert kiya
  } else {
    loader.classList.remove("visible");
  }
}

function animateProgressBar(ms) {
  const fill = document.getElementById("progressFill");
  const pctText = document.getElementById("progressPct");
  const start = performance.now();

  function update(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / ms, 1); // 0 se 1 tak

    fill.style.width = progress * 100 + "%";
    pctText.innerText = Math.round(progress * 100) + "%";

    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }
  requestAnimationFrame(update);
}

function showError(msg) {
  // Loading animation rok do
  showLoading(false);

  // Custom modal mein error text dalo aur usay show karo
  document.getElementById("errorMessage").innerText = msg;
  document.getElementById("errorModal").classList.add("visible");
}

function closeError() {
  // Modal ko hide karo aur page refresh kar do taake UI reset ho jaye
  document.getElementById("errorModal").classList.remove("visible");
  resetApp();
}

// --- ANALYZE SINGLE SITE ---
async function analyzeSingle() {
  const urlInput = document.getElementById("url1");
  const url = urlInput.value.trim();

  if (!validateURL("https://" + url)) {
    alert("Please enter a valid domain (e.g., google.com)");
    return;
  }

  showLoading(true);
  // 2nd doughnut hide kar rahe hain single mode mein
  document.getElementById("protocolChart2").style.display = "none";

  try {
    const response = await fetch("http://localhost:5000/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: "https://" + url }),
    });
    const data = await response.json();

    if (!response.ok) {
      showError("⚠️ " + (data.error || "Domain does not exist!"));
      showLoading(false);
      return;
    }

    displayFingerprint(data);
    renderSingleCharts(data);
    document.getElementById("resultsSection").classList.add("visible");
  } catch (e) {
    showError("Backend Error");
  }
  showLoading(false);
}

// --- COMPARE WEBSITES ---
// --- COMPARE WEBSITES ---
async function compareURLs() {
  const v1 = document.getElementById("comp1").value.trim();
  const v2 = document.getElementById("comp2").value.trim();

  // Basic Validation
  if (!v1 || !v2) {
    alert("Please enter both URLs to compare!");
    return;
  }

  const url1 = "https://" + v1;
  const url2 = "https://" + v2;

  // 20 second window for comparison
  showLoading(true, 20);
  document.getElementById("protocolChart2").style.display = "block";

  try {
    const response = await fetch("http://localhost:5000/api/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url1, url2 }),
    });

    const data = await response.json();

    // --- CASE 1: Domain Error (400) ---
    if (!response.ok) {
      // Direct Alert, No showError fuzool calls
      showError("⚠️ " + (data.error || "One of the domains does not exist!"));
      showLoading(false);
      return; 
    }

    // --- CASE 2: Success ---
    displayComparison(data);
    renderComparisonCharts(data);
    document.getElementById("resultsSection").classList.add("visible");

  } catch (e) {
    // --- CASE 3: Backend connection error ---
    console.error("Compare Error:", e);
    showError("❌ Error: Cannot connect to backend server!");
  } finally {
    // End mein loading band
    showLoading(false);
  }
}

// --- DISPLAY LOGIC ---
function displayFingerprint(fp) {
  const statRow = document.getElementById("statRow");
  statRow.innerHTML = `
        <div class="stat-card stat-card--cyan">
            <div class="stat-label">Behavior</div>
            <div class="stat-value">${fp.behavior_label}</div>
        </div>
        <div class="stat-card stat-card--cyan">
            <div class="stat-label">Total Packets</div>
            <div class="stat-value">${fp.total_packets}</div>
        </div>
        <div class="stat-card stat-card--cyan">
            <div class="stat-label">Data Transferred</div>
            <div class="stat-value">${formatBytes(fp.total_bytes)}</div>
        </div>
        <div class="stat-card stat-card--cyan">
            <div class="stat-label">Avg Packet Size</div>
            <div class="stat-value stat-value--small">${fp.mean_packet_size} B</div>
        </div>
    `;
}

function displayComparison(data) {
  const s1 = data.site1;
  const s2 = data.site2;
  const statRow = document.getElementById("statRow");

  // Yahan hum grid ko 2 rows mein divide kar rahe hain taake dono ki details aayein
  statRow.innerHTML = `
        <!-- Site A Details -->
        <div class="stat-card stat-card--cyan">
            <div class="stat-label">Site A: Packets / Data</div>
            <div class="stat-value stat-value--small">${s1.total_packets} / ${formatBytes(s1.total_bytes)}</div>
            <div class="stat-label" style="margin-top:5px">Avg: ${s1.mean_packet_size} B</div>
        </div>
        
        <!-- Site B Details -->
        <div class="stat-card stat-card--purple">
            <div class="stat-label">Site B: Packets / Data</div>
            <div class="stat-value stat-value--small">${s2.total_packets} / ${formatBytes(s2.total_bytes)}</div>
            <div class="stat-label" style="margin-top:5px">Avg: ${s2.mean_packet_size} B</div>
        </div>

        <!-- Site A Behavior -->
        <div class="stat-card stat-card--cyan">
            <div class="stat-label">Site A Behavior</div>
            <div class="stat-value stat-value--small">${s1.behavior_label}</div>
        </div>

        <!-- Site B Behavior -->
        <div class="stat-card stat-card--purple">
            <div class="stat-label">Site B Behavior</div>
            <div class="stat-value stat-value--small">${s2.behavior_label}</div>
        </div>
    `;
}

// --- CHARTING LOGIC ---
function destroyCharts() {
  Object.values(charts).forEach((c) => {
    if (c) c.destroy();
  });
  charts = {};
}

function renderSingleCharts(fp) {
  destroyCharts();
  const ctx1 = document.getElementById("protocolChart1").getContext("2d");
  const ctxHist = document.getElementById("histogramChart").getContext("2d");
  const ctxLine = document.getElementById("timelineChart").getContext("2d");

  // 1. Protocol Distribution (Doughnut Chart)
  charts.p1 = new Chart(ctx1, {
    type: "doughnut",
    data: {
      labels: Object.keys(fp.protocol_distribution),
      datasets: [
        {
          data: Object.values(fp.protocol_distribution),
          backgroundColor: ["#00f5ff", "#bf5fff", "#34d399", "#fbbf24"],
        },
      ],
    },
    options: { responsive: true, maintainAspectRatio: false },
  });

  // 2. Packet Size Histogram (Bar Chart)
  charts.hist = new Chart(ctxHist, {
    type: "bar",
    data: {
      labels: Object.keys(fp.size_histogram),
      datasets: [
        {
          label: "Packet Count",
          data: Object.values(fp.size_histogram),
          backgroundColor: "#00f5ff",
        },
      ],
    },
  });

  // 3. Traffic Timeline (Line Chart)
  charts.line = new Chart(ctxLine, {
    type: "line",
    data: {
      // 0 se 9 seconds tak ke labels fix kar diye hain stretch ke liye[cite: 1]
      labels: ["0s", "1s", "2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s"],
      datasets: [
        {
          label: "Bytes/sec",
          // Har second ke liye data check karein, agar missing ho toh 0 dikhayein[cite: 1]
          data: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map((s) => {
            const point = fp.timeline.find((t) => t.second === s);
            return point ? point.bytes : 0;
          }),
          borderColor: "#00f5ff",
          backgroundColor: "rgba(0, 245, 255, 0.1)",
          fill: true,
          tension: 0.4,
          borderWidth: 3,
          pointRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { display: false }, ticks: { color: "#8b9ab8" } },
        y: {
          beginAtZero: true,
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: { color: "#8b9ab8" },
        },
      },
      plugins: {
        legend: { display: true, labels: { color: "#fff" } },
      },
    },
  });
}

function renderComparisonCharts(data) {
  destroyCharts();
  const s1 = data.site1;
  const s2 = data.site2;
  const opt = { responsive: true, maintainAspectRatio: false };

  // 1. Protocol Pie Site A
  charts.p1 = new Chart(document.getElementById("protocolChart1"), {
    type: "doughnut",
    data: {
      labels: Object.keys(s1.protocol_distribution),
      datasets: [
        {
          data: Object.values(s1.protocol_distribution),
          backgroundColor: ["#00f5ff", "#bf5fff", "#34d399"],
        },
      ],
    },
    options: {
      ...opt,
      plugins: { title: { display: true, text: "Site A", color: "#fff" } },
    },
  });

  // 2. Protocol Pie Site B
  charts.p2 = new Chart(document.getElementById("protocolChart2"), {
    type: "doughnut",
    data: {
      labels: Object.keys(s2.protocol_distribution),
      datasets: [
        {
          data: Object.values(s2.protocol_distribution),
          backgroundColor: ["#bf5fff", "#00f5ff", "#34d399"],
        },
      ],
    },
    options: {
      ...opt,
      plugins: { title: { display: true, text: "Site B", color: "#fff" } },
    },
  });

  // 3. Histogram (Missing in your code)
  charts.hist = new Chart(document.getElementById("histogramChart"), {
    type: "bar",
    data: {
      labels: Object.keys(s1.size_histogram),
      datasets: [
        {
          label: "Site A",
          data: Object.values(s1.size_histogram),
          backgroundColor: "#00f5ff",
        },
        {
          label: "Site B",
          data: Object.values(s2.size_histogram),
          backgroundColor: "#bf5fff",
        },
      ],
    },
    options: opt,
  });

  // 4. Timeline (Missing in your code)
  const labels = Array.from(
    { length: Math.max(s1.timeline.length, s2.timeline.length) },
    (_, i) => `${i}s`,
  );
  charts.line = new Chart(document.getElementById("timelineChart"), {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Site A",
          data: labels.map((_, i) => s1.timeline[i]?.bytes || 0),
          borderColor: "#00f5ff",
          tension: 0.3,
        },
        {
          label: "Site B",
          data: labels.map((_, i) => s2.timeline[i]?.bytes || 0),
          borderColor: "#bf5fff",
          tension: 0.3,
        },
      ],
    },
    options: opt,
  });
}

// --- NAVIGATION ---
function selectMode(mode) {
  document.getElementById("homeView").style.display = "none";
  const inputSec = document.getElementById("inputSection");
  inputSec.classList.add("visible");

  if (mode === "single") {
    document.getElementById("singleInputGroup").style.display = "flex";
    document.getElementById("compareInputGroup").style.display = "none";
    document.getElementById("inputModeLabel").innerText =
      "Single Site Analysis";
  } else {
    document.getElementById("singleInputGroup").style.display = "none";
    document.getElementById("compareInputGroup").style.display = "flex";
    document.getElementById("inputModeLabel").innerText = "Compare Websites";
  }
}

function goHome() {
  location.reload();
}

function resetApp() {
  location.reload();
}

// Input validation to enable buttons
document.addEventListener("input", (e) => {
  const sBtn = document.getElementById("singleRunBtn");
  const cBtn = document.getElementById("compareRunBtn");
  sBtn.disabled = !document.getElementById("url1").value.trim();
  cBtn.disabled = !(
    document.getElementById("comp1").value.trim() &&
    document.getElementById("comp2").value.trim()
  );
});
