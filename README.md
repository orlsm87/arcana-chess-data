# ♟️ Arcana Chess Data Cloud

Plataforma serverless y pipeline automatizado con **coste de infraestructura de $0/mes** para recopilar, sanitizar, indexar y distribuir las partidas históricas y semanales de **The Week in Chess (TWIC)**.

Diseñado para alimentar a la estación de trabajo de ajedrez nativa para macOS **Arcana Chess Studio** y brindar a la comunidad ajedrecística internacional una base de datos maestra en **SQLite + Zstandard** de calidad profesional sin barreras de pago.

---

## 🏛️ Arquitectura del Pipeline ($0/mes)

El ecosistema aprovecha al 100% las capas gratuitas de GitHub (Actions, Releases y Pages):

```
                       [ theweekinchess.com/zips/twic{N}g.zip ]
                                          │
                                          ▼ (Cron: Lunes 22:00 UTC - 1 petición respetuosa)
                       [ GitHub Actions: twic_weekly_sync.yml ]
                                          │
                 ┌────────────────────────┴────────────────────────┐
                 ▼                                                 ▼
     [ twic_downloader.py ]                              [ fide_normalizer.py ]
     - Descarga respetuosa (rate limit)                  - Normalización FIDE (Carlsen, M. -> Magnus)
     - Cacheo local de zips                              - Limpieza y estandarización ELO
                 │                                                 │
                 └────────────────────────┬────────────────────────┘
                                          ▼
                                 [ pgn_cleaner.py ]
                                 - Validación de sintaxis PGN y tags estándar
                                 - Filtro de partidas truncadas y sin jugadas
                                 - Huella de deduplicación SHA-256
                                          │
                                          ▼
                               [ master_builder.py ]
                                 - SQLite 3 con WAL & inserción masiva
                                 - Índices: Blancas, Negras, ECO, Fecha, TWIC
                                 - Exportación Master PGN
                                 - Compresión Zstandard (.zst)
                                          │
                 ┌────────────────────────┴────────────────────────┐
                 ▼                                                 ▼
      [ GitHub Releases (CDN) ]                         [ generate_manifest.py ]
     - arcana_twic_master.db.zst                        - manifest.json con checksums SHA-256
     - arcana_twic_master.pgn.zip                       - Métricas en vivo y URLs CDN
     - twic_{issue}.zip (delta semanal)                            │
                                                                   ▼
                                                       [ GitHub Pages / Web ]
                                                       - Landing Cyberpunk (#0b0e14 / #00e5ff)
                                                       - Métricas en vivo desde manifest.json
                                                       - Atribución legal a Mark Crowther (TWIC)
                                                       - Banner Arcana Chess Studio
```

---

## 🗄️ Esquema SQLite Optimizado

```sql
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    twic_issue INTEGER NOT NULL,
    event TEXT,
    site TEXT,
    date TEXT,
    round TEXT,
    white TEXT NOT NULL,
    black TEXT NOT NULL,
    result TEXT NOT NULL,
    white_elo INTEGER,
    black_elo INTEGER,
    eco TEXT,
    pgn TEXT NOT NULL
);

-- Índices B-Tree para búsquedas en submilisegundos
CREATE INDEX IF NOT EXISTS idx_white ON games(white);
CREATE INDEX IF NOT EXISTS idx_black ON games(black);
CREATE INDEX IF NOT EXISTS idx_eco ON games(eco);
CREATE INDEX IF NOT EXISTS idx_date ON games(date);
CREATE INDEX IF NOT EXISTS idx_twic ON games(twic_issue);
```

---

## 🚀 Guía de Puesta en Marcha (Administrador)

### 1. Clonar y subir a GitHub
Crea un nuevo repositorio público en tu cuenta de GitHub (ejemplo: `arcana-chess-data`):

```bash
cd arcana-chess-data
git init
git add .
git commit -m "feat: initial Arcana Chess Data Cloud infrastructure"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/arcana-chess-data.git
git push -u origin main
```

### 2. Habilitar GitHub Pages
1. En GitHub, ve a tu repositorio $\to$ **Settings** $\to$ **Pages**.
2. En **Build and deployment**, selecciona **Source: GitHub Actions**.
3. ¡Listo! Cada vez que el pipeline se ejecute los lunes, actualizará la web pública automáticamente.

### 3. Ejecución y Sincronización Automática
* **Automática:** Todos los lunes a las 22:00 UTC (cron de GitHub Actions).
* **Manual:** Puedes ir a **Actions** $\to$ **Arcana TWIC Weekly Sync & Release** $\to$ **Run workflow** para forzar la actualización en cualquier momento.

---

## 💻 Uso Local y Herramientas

### Requisitos
* Python 3.9 o superior (cero dependencias obligatorias; utiliza la biblioteca estándar).
* Opcional: `pip install -r requirements.txt` para aceleración con librería nativa `zstandard`.

### Bootstrap Histórico (Compilar base inicial)
```bash
# Ingesta desde una carpeta local con zips descargados:
python3 scripts/bootstrap_historical.py --local-dir /ruta/a/mis_zips/ --compress

# O descarga respetuosa desde la web (ejemplo: ediciones 1650 a 1662):
python3 scripts/bootstrap_historical.py --start 1650 --end 1662 --delay 1.5 --compress
```

### Verificación de Calidad e Integridad
```bash
python3 scripts/verify_integrity.py --db data/arcana_twic_master.db --manifest manifest.json
```

---

## 📡 Especificación de la API (`manifest.json`)

Los clientes de escritorio como **Arcana Chess Studio** consultan este endpoint estático con latencia ultra-baja:

```json
{
  "service": "Arcana Chess Data Cloud",
  "version": "1.0",
  "updated_at": "2026-09-14T22:30:00Z",
  "latest_issue": 1662,
  "latest_issue_date": "2026-09-14",
  "total_games": 4918250,
  "master_database": {
    "version_issue": 1662,
    "size_mb": 422.4,
    "format": "sqlite3+zstd",
    "download_url": "https://github.com/<owner>/arcana-chess-data/releases/download/v1662/arcana_twic_master.db.zst",
    "sha256": "abcdef123456..."
  },
  "master_pgn": {
    "version_issue": 1662,
    "size_mb": 512.8,
    "format": "pgn+zip",
    "download_url": "https://github.com/<owner>/arcana-chess-data/releases/download/v1662/arcana_twic_master.pgn.zip",
    "sha256": "fedcba654321..."
  },
  "weekly_delta": {
    "issue": 1662,
    "games_count": 3680,
    "download_url": "https://github.com/<owner>/arcana-chess-data/releases/download/v1662/twic_1662.zip"
  }
}
```

---

## 🤝 Reconocimiento y Atribución a TWIC

Este proyecto es una iniciativa comunitaria de código abierto. Reconocemos explícitamente y agradecemos de corazón a **Mark Crowther**, creador y editor de [The Week in Chess (TWIC)](https://theweekinchess.com), por haber dedicado más de 30 años ininterrumpidos a recopilar las partidas magistrales de todo el mundo.

Por favor, considera apoyar a Mark Crowther suscribiéndote o donando en [theweekinchess.com/twic](https://theweekinchess.com/twic).

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
