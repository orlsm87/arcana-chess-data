/**
 * Arcana Chess Data Cloud - Web Portal Application
 * Loads dynamic manifest.json, animates counters, binds release download links,
 * and powers the interactive SQLite terminal demo.
 */

// Fallback data when manifest.json cannot be reached (e.g. local file:// preview)
const DEFAULT_MANIFEST = {
  service: "Arcana Chess Data Cloud",
  version: "1.0",
  updated_at: "2026-09-14T22:30:00Z",
  latest_issue: 1662,
  latest_issue_date: "2026-09-14",
  total_games: 4918250,
  master_database: {
    version_issue: 1662,
    size_mb: 422.4,
    format: "sqlite3+zstd",
    download_url: "https://github.com/orlsm87/arcana-chess-data/releases/download/v1662/arcana_twic_master.db.zst",
    sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  master_pgn: {
    version_issue: 1662,
    size_mb: 512.8,
    format: "pgn+zip",
    download_url: "https://github.com/orlsm87/arcana-chess-data/releases/download/v1662/arcana_twic_master.pgn.zip",
    sha256: "f42a1240c5717a6a4220b2241cfb5f8f9185a6cfc4f22c1b48325a7707e7b899"
  },
  weekly_delta: {
    issue: 1662,
    games_count: 3680,
    download_url: "https://github.com/orlsm87/arcana-chess-data/releases/download/v1662/twic_1662.zip"
  }
};

// Simulated SQLite Queries for Terminal Demo
const TERMINAL_PRESETS = {
  carlsen: {
    sql: "SELECT twic_issue, white, black, result, date, eco FROM games WHERE black = 'Carlsen, Magnus' AND eco = 'C88' LIMIT 3;",
    executionMs: "0.38 ms",
    headers: ["twic_issue", "white", "black", "result", "date", "eco"],
    rows: [
      ["1561", "Ding, Liren", "Carlsen, Magnus", "0-1", "2024.11.28", "C88"],
      ["1520", "Nepomniachtchi, Ian", "Carlsen, Magnus", "1/2-1/2", "2024.02.14", "C88"],
      ["1498", "Caruana, Fabiano", "Carlsen, Magnus", "0-1", "2023.09.05", "C88"]
    ]
  },
  kasparov: {
    sql: "SELECT twic_issue, white, black, result, date, event FROM games WHERE (white = 'Kasparov, Garry' OR black = 'Kasparov, Garry') AND white_elo > 2800 LIMIT 3;",
    executionMs: "0.52 ms",
    headers: ["twic_issue", "white", "black", "result", "date", "event"],
    rows: [
      ["261", "Kasparov, Garry", "Anand, Viswanathan", "1-0", "1999.11.12", "Wijk aan Zee SuperGM"],
      ["275", "Kramnik, Vladimir", "Kasparov, Garry", "1/2-1/2", "2000.02.18", "Linares Super Tournament"],
      ["320", "Kasparov, Garry", "Topalov, Veselin", "1-0", "2001.01.20", "Corus Chess Tournament"]
    ]
  },
  openings: {
    sql: "SELECT eco, count(*) as count FROM games GROUP BY eco ORDER BY count DESC LIMIT 5;",
    executionMs: "1.14 ms",
    headers: ["eco", "count"],
    rows: [
      ["B90", "134,812"],
      ["C88", "98,420"],
      ["E60", "84,310"],
      ["B33", "79,640"],
      ["D37", "72,190"]
    ]
  }
};

function formatNumber(num) {
  return new Intl.NumberFormat('en-US').format(num);
}

function animateValue(element, start, end, duration) {
  if (!element) return;
  const range = end - start;
  let current = start;
  const increment = end > start ? 1 : -1;
  const stepTime = Math.abs(Math.floor(duration / 50));
  const startTime = performance.now();

  function update() {
    const elapsed = performance.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const value = Math.floor(start + range * progress);
    element.textContent = formatNumber(value) + (progress === 1 ? "+" : "");
    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }
  requestAnimationFrame(update);
}

async function loadManifest() {
  let manifest = DEFAULT_MANIFEST;

  try {
    const response = await fetch('./manifest.json?t=' + Date.now());
    if (response.ok) {
      manifest = await response.json();
    }
  } catch (err) {
    console.warn("Using fallback manifest data (preview mode):", err);
  }

  // Update Hero & Metrics
  const gamesEl = document.getElementById("stat-total-games");
  if (gamesEl) {
    animateValue(gamesEl, 4500000, manifest.total_games || 4900000, 1200);
  }

  const issueEl = document.getElementById("stat-latest-issue");
  if (issueEl) issueEl.textContent = `#${manifest.latest_issue}`;

  const dateEl = document.getElementById("stat-issue-date");
  if (dateEl && manifest.latest_issue_date) {
    dateEl.textContent = `Publicado: ${manifest.latest_issue_date}`;
  }

  const dbSizeEl = document.getElementById("stat-db-size");
  if (dbSizeEl && manifest.master_database?.size_mb) {
    dbSizeEl.textContent = `${manifest.master_database.size_mb} MB`;
  }

  // Update Download Buttons & Links
  const btnDb = document.getElementById("btn-download-db");
  if (btnDb && manifest.master_database?.download_url) {
    btnDb.href = manifest.master_database.download_url;
  }
  const sizeDb = document.getElementById("dl-db-size");
  if (sizeDb && manifest.master_database?.size_mb) {
    sizeDb.textContent = `Peso: ${manifest.master_database.size_mb} MB`;
  }
  const shaDb = document.getElementById("sha-db");
  if (shaDb && manifest.master_database?.sha256) {
    shaDb.textContent = manifest.master_database.sha256;
    shaDb.title = manifest.master_database.sha256;
  }

  const btnPgn = document.getElementById("btn-download-pgn");
  if (btnPgn && manifest.master_pgn?.download_url) {
    btnPgn.href = manifest.master_pgn.download_url;
  }
  const sizePgn = document.getElementById("dl-pgn-size");
  if (sizePgn && manifest.master_pgn?.size_mb) {
    sizePgn.textContent = `Peso: ${manifest.master_pgn.size_mb} MB`;
  }
  const shaPgn = document.getElementById("sha-pgn");
  if (shaPgn && manifest.master_pgn?.sha256) {
    shaPgn.textContent = manifest.master_pgn.sha256;
    shaPgn.title = manifest.master_pgn.sha256;
  }

  const btnDelta = document.getElementById("btn-download-delta");
  if (btnDelta && manifest.weekly_delta?.download_url) {
    btnDelta.href = manifest.weekly_delta.download_url;
  }
  const nameDelta = document.getElementById("dl-delta-name");
  if (nameDelta && manifest.weekly_delta?.issue) {
    nameDelta.textContent = `Edición: TWIC #${manifest.weekly_delta.issue}`;
  }
  const gamesDelta = document.getElementById("dl-delta-games");
  if (gamesDelta && manifest.weekly_delta?.games_count) {
    gamesDelta.textContent = `Partidas: ${formatNumber(manifest.weekly_delta.games_count)}`;
  }

  // Render Manifest in Code Block
  const manifestBlock = document.getElementById("manifest-display");
  if (manifestBlock) {
    manifestBlock.textContent = JSON.stringify(manifest, null, 2);
  }
}

function renderTerminalPreset(presetKey) {
  const preset = TERMINAL_PRESETS[presetKey];
  if (!preset) return;

  const queryEl = document.getElementById("terminal-query-text");
  const outputEl = document.getElementById("terminal-output");
  if (!queryEl || !outputEl) return;

  queryEl.textContent = preset.sql;

  let tableHtml = `<div style="color: #64748b; margin-bottom: 6px;">-- Execution time: ${preset.executionMs} (Indexed B-Tree scan)</div>`;
  tableHtml += '<table class="sql-table"><thead><tr>';
  preset.headers.forEach(h => {
    tableHtml += `<th>${h}</th>`;
  });
  tableHtml += '</tr></thead><tbody>';

  preset.rows.forEach(r => {
    tableHtml += '<tr>';
    r.forEach(val => {
      tableHtml += `<td>${val}</td>`;
    });
    tableHtml += '</tr>';
  });
  tableHtml += '</tbody></table>';

  outputEl.innerHTML = tableHtml;
}

function setupTerminal() {
  const buttons = document.querySelectorAll(".preset-btn");
  buttons.forEach(btn => {
    btn.addEventListener("click", () => {
      buttons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const key = btn.getAttribute("data-query");
      renderTerminalPreset(key);
    });
  });

  // Initial render with default preset
  renderTerminalPreset("carlsen");
}

document.addEventListener("DOMContentLoaded", () => {
  loadManifest();
  setupTerminal();
});
