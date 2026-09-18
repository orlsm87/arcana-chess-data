/**
 * Arcana Chess Data Cloud - Web Portal Application
 * Multilingual Engine (ES/EN), dynamic manifest ingestion, live metric animations,
 * release asset link binding, and interactive SQLite terminal emulator.
 */

// Fallback data reflecting the 3.55M games master database
const DEFAULT_MANIFEST = {
  service: "Arcana Chess Data Cloud",
  version: "1.0",
  updated_at: "2026-09-18T06:37:13Z",
  latest_issue: 1662,
  latest_issue_date: "2026-09-18",
  total_games: 3555967,
  master_database: {
    version_issue: 1662,
    size_mb: 824.0,
    format: "sqlite3+zstd",
    download_url: "https://github.com/orlsm87/arcana-chess-data/releases/download/v1662/arcana_twic_master.db.zst",
    sha256: "6fb9a82f5503011edf63a1e357603afeedef76a79604cf9a926213cbfe2f93b6"
  },
  master_pgn: {
    version_issue: 1662,
    size_mb: 778.5,
    format: "pgn+zip",
    download_url: "https://github.com/orlsm87/arcana-chess-data/releases/download/v1662/arcana_twic_master.pgn.zip",
    sha256: "17057887ebe326021fb6fa48d37361d3c17b8aad36566aa014009248cc98fef8"
  },
  weekly_delta: {
    issue: 1662,
    games_count: 6615,
    download_url: "https://github.com/orlsm87/arcana-chess-data/releases/download/v1662/twic_1662.zip"
  }
};

// Full Bilingual Dictionary
const TRANSLATIONS = {
  es: {
    page_title: "Arcana Chess Data Cloud | Plataforma Global de Datos de TWIC",
    page_meta: "Base de datos maestra de ajedrez mundial The Week in Chess (TWIC) pre-indexada en SQLite + Zstandard. Actualizaciones automáticas semanales con coste $0/mes para Arcana Chess Studio.",
    nav_manifesto: "Manifiesto",
    nav_scope: "Alcance #920",
    nav_downloads: "Descargas",
    nav_terminal: "Terminal SQL",
    nav_attribution: "Atribución TWIC",

    hero_status: "SINCRONIZACIÓN ACTIVA • COSTO $0/MES",
    hero_title: "La Base Maestra de <span class=\"gradient-text\">The Week in Chess</span> en SQLite",
    hero_desc: "Pipeline serverless y autónomo que consolida, sanitiza y comprime más de 12 años de torneos mundiales de TWIC con compresión <strong>Zstandard</strong> e indexación B-Tree ultrarrápida.",

    stat_total_label: "TOTAL PARTIDAS INDEXADAS",
    stat_total_sub: "Deduplicadas y sanitizadas",
    stat_issue_label: "EDICIÓN ACTUAL TWIC",
    stat_issue_sub: "Publicado: ",
    stat_size_label: "TAMAÑO COMPRIMIDO (ZST)",
    stat_size_sub: "Descompresión < 2 seg en Mac",
    stat_cycle_label: "CICLO DE ACTUALIZACIÓN",
    stat_cycle_val: "Lunes 22:00 UTC",
    stat_cycle_sub: "Cron Serverless en GitHub",

    manifesto_author: "Orlando (Arcana Chess Studio)",
    manifesto_badge: "LA PESADILLA DEL AJEDRECISTA",
    manifesto_heading: "Por qué construimos esta herramienta: <span>Basta del infierno de las bases de datos</span>",
    manifesto_p1: "Cualquiera que haya competido en ajedrez de alto rendimiento o haya tenido alumnos a su cargo conoce esta verdad: <strong>la gestión de bases de datos de partidas es una auténtica pesadilla técnica</strong>.",
    manifesto_p2: "Se te daña un disco duro, cambias de computadora o sufres una corrupción de archivos y pierdes años de preparación. O peor aún: un estudiante talentoso o un jugador que recién empieza quiere armar su biblioteca y se encuentra con un muro infranqueable. O pagas cientos de euros a monopolios comerciales por bases de datos cerradas y propietarias, o intentas la tortura de ir a TWIC a descargar <strong>más de 700 archivos ZIP uno por uno</strong>, lidiar con errores de red, nombres mal escritos (<em>\"Carlsen, M.\"</em> vs <em>\"Carlsen, Magnus\"</em>), duplicados infinitos y el riesgo constante de que el servidor te bloquee la IP por exceso de peticiones.",
    manifesto_quote: "\"El análisis de partidas de Grandes Maestros debe ser un derecho formativo universal, no un privilegio reservado a quienes pueden pagar suscripciones abusivas o pasar semanas limpiando archivos de texto corruptos.\"",
    pill1_title: "Descarga en 1 Clic",
    pill1_desc: "Un único archivo maestro SQLite optimizado en lugar de 700+ descargas individuales propensas a fallos.",
    pill2_title: "Sanitización & Normalización",
    pill2_desc: "Nombres FIDE canónicos unificados, jugadas verificadas, tags estandarizados y deduplicación con hash SHA-256.",
    pill3_title: "Costo $0 para Siempre",
    pill3_desc: "Construido 100% en infraestructura serverless abierta para garantizar acceso gratuito y perpetuo a la comunidad.",

    scope_tag: "TRANSPARENCIA TÉCNICA",
    scope_title: "Alcance del Archivo: ¿Por qué iniciamos en TWIC #920?",
    scope_desc: "Explicación transparente de la cobertura histórica actual y los motivos técnicos de preservación del servidor de TWIC.",
    scope_era1_badge: "ERA MODERNA CONSOLIDADA (100% ACTIVA)",
    scope_era1_title: "Ediciones TWIC #920 a #1662+ (Junio 2012 – Presente)",
    scope_era1_p1: "En junio de 2012 (edición #920), Mark Crowther migró la arquitectura de distribución web de <em>The Week in Chess</em> a su formato público actual (<code>twic{N}g.zip</code>).",
    scope_era1_p2: "Nuestra nube cubre <strong>el 100% ininterrumpido de estas 743 semanas consecutivas</strong> (más de 3.55 millones de partidas), garantizando que ningún torneo de la era moderna falte en tu base.",
    scope_era1_li1: "743 ediciones semanales consecutivas procesadas sin huecos.",
    scope_era1_li2: "3,555,967 partidas maestras indexadas y deduplicadas.",
    scope_era1_li3: "Sincronización semanal automática todos los lunes a las 22:00 UTC.",
    scope_era2_badge: "ERA LEGACY (EN CONSOLIDACIÓN)",
    scope_era2_title: "Ediciones TWIC #1 a #919 (1994 – Junio 2012)",
    scope_era2_p1: "Las primeras 919 ediciones corresponden a la primera época de TWIC (archivos de texto antiguos, boletines por correo electrónico y discos CD/DVD históricos comercializados por Mark Crowther para sustentar el proyecto).",
    scope_era2_p2: "<strong>Decisión ética y técnica:</strong> Para no sobrecargar los servidores de TWIC con peticiones forzadas ni scraping no autorizado, no atacamos endpoints legacy.",
    scope_era2_p3: "🤝 <em>Llamado a la comunidad:</em> Estamos preparando una importación consolidada desde respaldos públicos autorizados para unir este bloque y alcanzar las 4.9M partidas completas.",

    promo_badge: "ESTACIÓN DE TRABAJO RECOMENDADA",
    promo_title: "Diseñado para alimentar a <span>Arcana Chess Studio</span>",
    promo_desc: "Navega por millones de partidas a velocidad nativa en macOS. Con motor <strong>Stockfish 19 C++20 in-process</strong>, visor de árboles de aperturas, y sincronización delta automática con esta nube.",
    promo_btn: "Explorar Arcana Studio",

    dl_tag: "DISTRIBUCIÓN COMUNITARIA",
    dl_title: "Descargas Directas sin Registro",
    dl_sub: "Alojadas en la CDN global de GitHub Releases con ancho de banda y velocidad ilimitada.",
    card1_tag: "RECOMENDADO PARA APPS",
    card1_title: "Base de Datos Maestra SQLite",
    card1_desc: "3.55M de partidas desde TWIC 920 a la actualidad, estructurada en SQLite 3 con índices en Blancas, Negras, ECO y Fecha. Comprimida con Zstandard.",
    card1_btn: "⬇️ Descargar Master SQLite (.zst)",
    card2_tag: "COMPATIBILIDAD UNIVERSAL",
    card2_title: "Archivo PGN Consolidado",
    card2_desc: "Todas las partidas históricas en formato estándar PGN compatible con cualquier software de ajedrez (ChessBase, SCID, Fritz, Lichess, Chess.com).",
    card2_btn: "⬇️ Descargar Master PGN (.zip)",
    card3_tag: "ACTUALIZACIÓN SEMANAL",
    card3_title: "Parche Semanal (Delta)",
    card3_desc: "Únicamente las partidas de la última edición de TWIC. Ideal para mantener tu base de datos al día sin descargar todo el archivo acumulado.",
    card3_btn: "⬇️ Descargar Última Edición (.zip)",
    card3_usage_lbl: "Uso:",
    card3_usage_val: "Importación incremental en Arcana",

    term_tag: "CONSULTAS A MÁXIMA VELOCIDAD",
    term_title: "Prueba la Arquitectura SQLite",
    term_sub: "Ejecuta consultas de ejemplo para ver la estructura de campos y el poder de los índices B-Tree.",
    term_presets_lbl: "Consultas Rápidas:",
    preset_carlsen: "Magnus Carlsen con Negras (C88)",
    preset_kasparov: "Garry Kasparov en TWIC",
    preset_openings: "Top 5 Aperturas Más Populares",

    api_tag: "ESPECIFICACIÓN CDN",
    api_title: "API REST Estática (manifest.json)",
    api_sub: "Servida con latencia mínima a través de GitHub Pages / CDN para sincronización de clientes desktop y bots.",

    attr_title: "Reconocimiento Formal y Ética: The Week in Chess (TWIC)",
    attr_p1: "<strong>Arcana Chess Data Cloud</strong> es un proyecto independiente y complementario que no busca reemplazar a <em>The Week in Chess</em>, sino facilitar su indexación para clientes de escritorio modernos.",
    attr_p2: "Todas las partidas son recopiladas originalmente por el periodista ajedrecístico <strong>Mark Crowther</strong>, quien ha mantenido TWIC de forma ininterrumpida desde 1994. Reconocemos profundamente su labor histórica para la cultura ajedrecística mundial.",
    attr_btn_visit: "Visitar theweekinchess.com",
    attr_btn_donate: "Apoyar / Donar a TWIC",

    footer_sub: "Infraestructura serverless de costo $0/mes para la comunidad global de ajedrez.",
    footer_license: "Licencia de código abierto MIT",
    footer_for: "Diseñado para"
  },

  en: {
    page_title: "Arcana Chess Data Cloud | Global TWIC Chess Data Platform",
    page_meta: "Master global chess database from The Week in Chess (TWIC) pre-indexed in SQLite + Zstandard. Automated weekly sync at $0/month cost for Arcana Chess Studio.",
    nav_manifesto: "Manifesto",
    nav_scope: "Scope #920",
    nav_downloads: "Downloads",
    nav_terminal: "SQL Terminal",
    nav_attribution: "TWIC Attribution",

    hero_status: "ACTIVE PIPELINE • $0/MONTH INFRASTRUCTURE",
    hero_title: "The Master <span class=\"gradient-text\">The Week in Chess</span> SQLite Database",
    hero_desc: "Autonomous, serverless pipeline consolidating, sanitizing, and compressing over 12 years of global master games with <strong>Zstandard</strong> compression and ultra-fast B-Tree indexing.",

    stat_total_label: "TOTAL MASTER GAMES INDEXED",
    stat_total_sub: "Deduplicated & sanitized",
    stat_issue_label: "CURRENT TWIC ISSUE",
    stat_issue_sub: "Published: ",
    stat_size_label: "COMPRESSED SIZE (ZST)",
    stat_size_sub: "Decompresses in < 2 sec on Mac",
    stat_cycle_label: "UPDATE CYCLE",
    stat_cycle_val: "Mondays 22:00 UTC",
    stat_cycle_sub: "GitHub Serverless Cron",

    manifesto_author: "Orlando (Arcana Chess Studio)",
    manifesto_badge: "THE CHESS PLAYER'S NIGHTMARE",
    manifesto_heading: "Why We Built This Tool: <span>Ending the Chess Database Nightmare</span>",
    manifesto_p1: "Anyone who has competed in tournament chess or trained students knows this harsh truth: <strong>managing game databases is a constant, exhausting technical nightmare</strong>.",
    manifesto_p2: "A hard drive dies, you upgrade your laptop, or a database gets corrupted, and you instantly lose years of accumulated work. Worse still: a talented young student or an aspiring master trying to build their library from scratch hits an absurd wall. You either pay hundreds of dollars to commercial monopolies for locked, proprietary databases, or you endure the torture of downloading <strong>over 700 individual ZIP files one by one</strong> from TWIC, dealing with socket errors, misspelled names (<em>\"Carlsen, M.\"</em> vs <em>\"Carlsen, Magnus\"</em>), infinite duplicates, and the constant fear of your IP being banned by TWIC's firewall for too many requests.",
    manifesto_quote: "\"Master game analysis must be a universal educational right, not a luxury reserved for those who can afford exorbitant subscriptions or spend weeks cleaning corrupted text archives.\"",
    pill1_title: "1-Click Download",
    pill1_desc: "A single optimized master SQLite database instead of 700+ error-prone individual downloads.",
    pill2_title: "Sanitization & Normalization",
    pill2_desc: "Canonical FIDE player identities, verified moves, standard roster tags, and SHA-256 game fingerprint deduplication.",
    pill3_title: "$0 Cost Forever",
    pill3_desc: "Built entirely on enterprise-grade serverless open infrastructure to guarantee perpetual, free community access.",

    scope_tag: "TECHNICAL TRANSPARENCY",
    scope_title: "Archive Scope: Why Do We Start at TWIC #920?",
    scope_desc: "Transparent overview of our current historical coverage and the technical reasons for preserving TWIC's server.",
    scope_era1_badge: "CONSOLIDATED MODERN ERA (100% ACTIVE)",
    scope_era1_title: "TWIC Issues #920 to #1662+ (June 2012 – Present)",
    scope_era1_p1: "In June 2012 (issue #920), Mark Crowther migrated <em>The Week in Chess</em> web distribution architecture to its current public format (<code>twic{N}g.zip</code>).",
    scope_era1_p2: "Our cloud covers <strong>100% uninterrupted across these 743 consecutive weeks</strong> (over 3.55 million games), guaranteeing that no modern master tournament is missing from your collection.",
    scope_era1_li1: "743 consecutive weekly issues processed without gaps.",
    scope_era1_li2: "3,555,967 master games indexed and deduplicated.",
    scope_era1_li3: "Automated weekly synchronization every Monday at 22:00 UTC.",
    scope_era2_badge: "LEGACY ERA (CONSOLIDATION IN PROGRESS)",
    scope_era2_title: "TWIC Issues #1 to #919 (1994 – June 2012)",
    scope_era2_p1: "The earliest 919 issues belong to TWIC's original era (early text digests, email dispatches, and historical CD/DVD archives distributed by Mark Crowther to fund the project).",
    scope_era2_p2: "<strong>Ethical and technical policy:</strong> To avoid hammering TWIC's servers with brute-force scraping on non-existent endpoints, we never attack legacy URLs.",
    scope_era2_p3: "🤝 <em>Community Call:</em> We are preparing a verified public import to bridge these early years and reach the full 4.9M historical games.",

    promo_badge: "RECOMMENDED WORKSTATION",
    promo_title: "Engineered to Power <span>Arcana Chess Studio</span>",
    promo_desc: "Navigate millions of master games at native macOS speed. Powered by an embedded <strong>Stockfish 19 C++20 in-process engine</strong>, opening tree explorer, and automatic delta synchronization.",
    promo_btn: "Explore Arcana Studio",

    dl_tag: "COMMUNITY DISTRIBUTION",
    dl_title: "Direct Downloads Without Registration",
    dl_sub: "Hosted on GitHub Releases global CDN with unlimited bandwidth and high-speed delivery.",
    card1_tag: "RECOMMENDED FOR APPS",
    card1_title: "Master SQLite Database",
    card1_desc: "3.55M games from TWIC 920 to present, structured in SQLite 3 with indexes on White, Black, ECO, and Date. Compressed with Zstandard.",
    card1_btn: "⬇️ Download Master SQLite (.zst)",
    card2_tag: "UNIVERSAL COMPATIBILITY",
    card2_title: "Consolidated Master PGN",
    card2_desc: "Complete historical collection in standard PGN format compatible with all chess software (ChessBase, SCID, Fritz, Lichess, Chess.com).",
    card2_btn: "⬇️ Download Master PGN (.zip)",
    card3_tag: "WEEKLY UPDATE",
    card3_title: "Weekly Patch (Delta)",
    card3_desc: "Exclusively the games from the latest TWIC issue. Perfect for keeping your database up-to-date without downloading the full archive.",
    card3_btn: "⬇️ Download Latest Issue (.zip)",
    card3_usage_lbl: "Usage:",
    card3_usage_val: "Incremental import in Arcana Studio",

    term_tag: "LIGHTNING FAST QUERIES",
    term_title: "Experience the SQLite Architecture",
    term_sub: "Execute sample queries to see the field structure and the speed of optimized B-Tree indexes.",
    term_presets_lbl: "Quick Queries:",
    preset_carlsen: "Magnus Carlsen with Black (C88)",
    preset_kasparov: "Garry Kasparov in TWIC",
    preset_openings: "Top 5 Most Popular Openings",

    api_tag: "CDN SPECIFICATION",
    api_title: "Static REST API (manifest.json)",
    api_sub: "Served with minimal latency via GitHub Pages / CDN for desktop client and bot synchronizations.",

    attr_title: "Formal Attribution & Ethics: The Week in Chess (TWIC)",
    attr_p1: "<strong>Arcana Chess Data Cloud</strong> is an independent, non-commercial community project designed to facilitate indexing for modern desktop chess clients.",
    attr_p2: "All games are originally collected by chess journalist <strong>Mark Crowther</strong>, who has published TWIC without interruption since 1994. We deeply honor and thank him for his monumental contribution to global chess culture.",
    attr_btn_visit: "Visit theweekinchess.com",
    attr_btn_donate: "Support / Donate to TWIC",

    footer_sub: "Serverless $0/month infrastructure for the global chess community.",
    footer_license: "MIT Open Source License",
    footer_for: "Engineered for"
  }
};

let currentLang = localStorage.getItem("arcana_lang") || (navigator.language?.startsWith("es") ? "es" : "en");

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

function setLanguage(lang) {
  currentLang = lang;
  localStorage.setItem("arcana_lang", lang);
  document.documentElement.lang = lang;

  const dict = TRANSLATIONS[lang] || TRANSLATIONS.es;

  // Update Page Title and Meta
  if (dict.page_title) document.title = dict.page_title;
  const metaEl = document.querySelector('meta[name="description"]');
  if (metaEl && dict.page_meta) metaEl.setAttribute("content", dict.page_meta);

  // Update all elements with data-i18n
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) {
      el.innerHTML = dict[key];
    }
  });

  // Update Language Switcher Buttons
  const btnEs = document.getElementById("btn-lang-es");
  const btnEn = document.getElementById("btn-lang-en");
  if (btnEs && btnEn) {
    if (lang === "es") {
      btnEs.classList.add("active");
      btnEn.classList.remove("active");
    } else {
      btnEn.classList.add("active");
      btnEs.classList.remove("active");
    }
  }
}

function animateValue(element, start, end, duration) {
  if (!element) return;
  const range = end - start;
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
    animateValue(gamesEl, 3000000, manifest.total_games || 3555967, 1200);
  }

  const issueEl = document.getElementById("stat-latest-issue");
  if (issueEl) issueEl.textContent = `#${manifest.latest_issue}`;

  const dateEl = document.getElementById("stat-issue-date");
  if (dateEl && manifest.latest_issue_date) {
    const prefix = currentLang === "es" ? "Publicado: " : "Published: ";
    dateEl.textContent = `${prefix}${manifest.latest_issue_date}`;
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
    sizeDb.textContent = `Peso / Size: ${manifest.master_database.size_mb} MB`;
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
    sizePgn.textContent = `Peso / Size: ${manifest.master_pgn.size_mb} MB`;
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
    nameDelta.textContent = `TWIC #${manifest.weekly_delta.issue}`;
  }
  const gamesDelta = document.getElementById("dl-delta-games");
  if (gamesDelta && manifest.weekly_delta?.games_count) {
    const lbl = currentLang === "es" ? "Partidas" : "Games";
    gamesDelta.textContent = `${lbl}: ${formatNumber(manifest.weekly_delta.games_count)}`;
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

  const execLbl = currentLang === "es" ? "-- Tiempo de ejecución" : "-- Execution time";
  const scanLbl = currentLang === "es" ? "(Escaneo con índice B-Tree)" : "(Indexed B-Tree scan)";
  let tableHtml = `<div style="color: #64748b; margin-bottom: 6px;">${execLbl}: ${preset.executionMs} ${scanLbl}</div>`;
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

  renderTerminalPreset("carlsen");
}

function setupLanguageSwitcher() {
  const btnEs = document.getElementById("btn-lang-es");
  const btnEn = document.getElementById("btn-lang-en");

  if (btnEs) {
    btnEs.addEventListener("click", () => {
      setLanguage("es");
      loadManifest();
    });
  }

  if (btnEn) {
    btnEn.addEventListener("click", () => {
      setLanguage("en");
      loadManifest();
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  setLanguage(currentLang);
  setupLanguageSwitcher();
  loadManifest();
  setupTerminal();
});
