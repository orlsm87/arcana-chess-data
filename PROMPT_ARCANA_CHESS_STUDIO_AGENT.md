# PROMPT MAESTRO DE ESPECIFICACIÓN TÉCNICA E INTEGRACIÓN
## Para: Agente de Inteligencia Artificial / Desarrollador de Arcana Chess Studio (macOS)
### De: Agente de Arquitectura de Datos de Arcana Chess Data Cloud
### Fecha de emisión: 18 de Septiembre de 2026
### Estado de la Nube: Producción Activa (3,555,967 partidas maestras • TWIC #920 a #1662+)

---

> ### 📋 INSTRUCCIÓN PARA EL USUARIO
> Copia y pega **íntegramente** todo el bloque de texto que está a continuación dentro de la conversación con el agente encargado de desarrollar la aplicación **Arcana Chess Studio (macOS)**. Al leerlo, el agente dispondrá de todo el contexto técnico, endpoints, esquemas de bases de datos, algoritmos de descompresión y protocolos de red para entregarte un **Plan de Implementación** completo y estructurado.

---

```markdown
# BRIEFING TÉCNICO Y PLAN DE INTEGRACIÓN CON ARCANA CHESS DATA CLOUD
## Para el Agente de Desarrollo de Arcana Chess Studio (macOS)

### 1. CONTEXTO Y ROL
Eres el Ingeniero de Software Principal encargado de la arquitectura de la aplicación nativa **Arcana Chess Studio para macOS** (C++20 / Swift / Metal).

La plataforma de datos en la nube **Arcana Chess Data Cloud** ya está 100% construida, probada y desplegada en producción. Es una infraestructura completamente serverless con **costo de mantenimiento de $0/mes**, alojada en GitHub Actions, GitHub Releases y GitHub Pages. Tu objetivo es diseñar e implementar el subsistema de datos y sincronización dentro de **Arcana Chess Studio** para que la app se conecte a esta nube, descargue la base de datos de millones de partidas sin fricción para el usuario y se mantenga sincronizada de forma autónoma semana a semana.

---

### 2. ARQUITECTURA DE LA NUBE (ARCANA CHESS DATA CLOUD)

#### A. Endpoints Públicos de Producción
* **URL de la API / Manifiesto:**
  `https://orlsm87.github.io/arcana-chess-data/manifest.json`
* **Portal Comunitario:**
  `https://orlsm87.github.io/arcana-chess-data/`
* **Repositorio de Distribución:**
  `https://github.com/orlsm87/arcana-chess-data`
* **CDN Global de Binarios:**
  `https://github.com/orlsm87/arcana-chess-data/releases/tag/v{latest_issue}`

#### B. Estructura del `manifest.json`
Cada vez que la nube se actualiza (todos los lunes a las 22:00 UTC vía GitHub Actions), se genera y publica un manifiesto con la siguiente especificación:

```json
{
  "service": "Arcana Chess Data Cloud",
  "version": "1.0",
  "updated_at": "2026-09-18T06:37:13Z",
  "latest_issue": 1662,
  "latest_issue_date": "2026-09-18",
  "total_games": 3555967,
  "master_database": {
    "version_issue": 1662,
    "size_mb": 824.0,
    "format": "sqlite3+zstd",
    "download_url": "https://github.com/orlsm87/arcana-chess-data/releases/download/v1662/arcana_twic_master.db.zst",
    "sha256": "6fb9a82f5503011edf63a1e357603afeedef76a79604cf9a926213cbfe2f93b6"
  },
  "master_pgn": {
    "version_issue": 1662,
    "size_mb": 778.5,
    "format": "pgn+zip",
    "download_url": "https://github.com/orlsm87/arcana-chess-data/releases/download/v1662/arcana_twic_master.pgn.zip",
    "sha256": "17057887ebe326021fb6fa48d37361d3c17b8aad36566aa014009248cc98fef8"
  },
  "weekly_delta": {
    "issue": 1662,
    "games_count": 6615,
    "download_url": "https://github.com/orlsm87/arcana-chess-data/releases/download/v1662/twic_1662.zip",
    "sha256": "c4961e6878b668f44d8b671aaae3be708e9ea9825b7337375bf51509930f7690"
  }
}
```

#### C. Esquema Relacional de la Base de Datos SQLite (`schema.sql`)
La base de datos maestra utiliza SQLite 3 optimizado para lectura masiva:

```sql
-- Tabla principal de partidas
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    twic_issue INTEGER NOT NULL,
    white TEXT NOT NULL,
    black TEXT NOT NULL,
    white_elo INTEGER,
    black_elo INTEGER,
    result TEXT NOT NULL,
    date TEXT,
    event TEXT,
    site TEXT,
    eco TEXT,
    moves TEXT NOT NULL,
    sha256_hash TEXT NOT NULL UNIQUE
);

-- Índices B-Tree de alta velocidad
CREATE INDEX IF NOT EXISTS idx_white ON games (white);
CREATE INDEX IF NOT EXISTS idx_black ON games (black);
CREATE INDEX IF NOT EXISTS idx_eco ON games (eco);
CREATE INDEX IF NOT EXISTS idx_date ON games (date);
CREATE INDEX IF NOT EXISTS idx_twic ON games (twic_issue);

-- Registro de ediciones semanales procesadas
CREATE TABLE IF NOT EXISTS processed_issues (
    issue_number INTEGER PRIMARY KEY,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    games_count INTEGER NOT NULL
);

-- Metadatos de estado del sistema
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

#### D. Sanitización y Calidad de Datos
Todas las partidas de la base maestra ya pasaron por:
1. **Normalización canónica FIDE:** Nombres unificados (ej. `"Carlsen, M."` $\to$ `"Carlsen, Magnus"`), eliminación de títulos duplicados y saneamiento de Elo.
2. **Deduplicación SHA-256:** Huella criptográfica única generada sobre `white`, `black`, `date`, `result` y la secuencia normalizada de jugadas.
3. **Optimización de Compresión:** Comprimida con **Zstandard (Zstandard v1.5+, nivel 19)** pasando de 3.54 GB crudos a **824 MB**.

---

### 3. PROTOCOLO DE FUNCIONAMIENTO EN ARCANA CHESS STUDIO (macOS)

La app para macOS debe implementar un gestor de base de datos (`DatabaseSyncManager`) con los siguientes dos flujos principales:

#### Flujo 1: Primer Lanzamiento de la App (Cold Bootstrap / Instalación Limpia)
1. **Detección de estado:**
   La app verifica si existe la base de datos local en:
   `~/Library/Application Support/ArcanaChessStudio/database/arcana_master.db`.
2. **Si no existe:**
   - La app muestra una pantalla de bienvenida amigable: *"Descargando Base de Datos Maestra de Partidas (3.55M partidas)..."*
   - Realiza un `HTTP GET` a `https://orlsm87.github.io/arcana-chess-data/manifest.json?t={timestamp}`.
   - Obtiene el campo `master_database.download_url` y `master_database.sha256`.
   - Descarga con barra de progreso el archivo `arcana_twic_master.db.zst` (824 MB) soportando pausa/reanudación (`Range: bytes`).
   - Verifica el hash SHA-256 descargado contra el manifiesto.
   - Descomprime el archivo en streaming usando la biblioteca nativa `libzstd` (en Apple Silicon M1/M2/M3/M4 toma **menos de 1.5 segundos**).
   - Coloca la base descomprimida en su ruta final y ejecuta:
     ```sql
     PRAGMA journal_mode = WAL;
     PRAGMA synchronous = NORMAL;
     PRAGMA cache_size = -64000; -- 64MB de caché en RAM
     PRAGMA temp_store = MEMORY;
     PRAGMA busy_timeout = 60000;
     ```
   - ¡Listo! La app tiene acceso instantáneo a todas las partidas sin bloquear la interfaz.

#### Flujo 2: Sincronización Semanal Incremental (Delta Sync)
1. **Comprobación periódica:**
   Al abrir la app (o cuando el usuario presiona el botón *"Sincronizar"* en el menú):
   - Consulta `SELECT MAX(issue_number) FROM processed_issues;` en el SQLite local. Supongamos que la base local tiene hasta el issue `#1661`.
   - Consulta el manifiesto remoto: `manifest.latest_issue` (supongamos `#1662`).
2. **Si `latest_issue > local_issue`:**
   - Si la diferencia es de 1 edición ($N+1$):
     - Descarga únicamente el parche semanal delta: `twic_1662.zip` (**1.8 MB**, toma menos de 1 segundo).
     - Extrae el archivo PGN del zip en memoria.
     - Ejecuta un `BEGIN TRANSACTION;`
     - Inserta las nuevas partidas en la tabla `games` usando `INSERT OR IGNORE INTO games ...` (evitando duplicados gracias a la restricción `UNIQUE` en `sha256_hash`).
     - Registra la edición: `INSERT INTO processed_issues (issue_number, games_count) VALUES (1662, ...);`
     - Actualiza el metadato: `UPDATE metadata SET value = '1662' WHERE key = 'last_issue';`
     - Ejecuta `COMMIT;`
   - Si la diferencia es de varias semanas ($> 1$ y $\le 8$ semanas):
     - La app puede descargar los zips semanales faltantes de forma secuencial (`twic_1662.zip`, `twic_1663.zip`, etc.).
   - Si la diferencia es muy grande ($> 12$ semanas):
     - Ofrecer al usuario actualizar mediante la descarga del master consolidado `.zst` para mayor velocidad.
3. **Modo Offline:**
   Si la app no tiene conexión a internet, simplemente usa la base de datos local SQLite existente sin emitir errores invasivos ni interrumpir el trabajo de estudio o análisis.

---

### 4. REQUERIMIENTOS ESPECÍFICOS PARA TU PLAN DE IMPLEMENTACIÓN

Por favor, con base en toda la información anterior, genera un **Plan de Implementación Exhaustivo** para la versión macOS de Arcana Chess Studio que incluya:

1. **Módulos de Código Propuestos (Arquitectura C++20 / Swift):**
   - Módulo de Red (`NetworkClient` con soporte para reanudación y descarga asíncrona de `manifest.json` y binarios).
   - Módulo de Descompresión Zstandard (`ZstdStreamDecompressor` integrando `libzstd` nativo vía CMake o Swift Package Manager).
   - Módulo de Base de Datos SQLite (`ChessDatabaseService` con transacciones seguras, consultas preparadas B-Tree y pool de conexiones en modo WAL).
   - Módulo de Árbol de Aperturas (`OpeningTreeService` optimizado para calcular frecuencias de movimientos, porcentajes de victoria de blancas/negras y transposiciones en $< 15$ ms).

2. **Diseño de Interfaz de Usuario (UI/UX en macOS):**
   - Indicador de estado de sincronización (insignia discreta en la barra de herramientas: *● Sincronizado*, *⬇️ Sincronizando...*, o *Offline*).
   - Ventana modal / diálogo de primera descarga (Cold Start) con barra de progreso, estimación de tiempo y opción de pausar.
   - Notificación sutil no intrusiva al finalizar una sincronización semanal ("*Se han añadido 6,615 partidas maestras del TWIC #1662*").

3. **Estrategia de Pruebas y Robustez:**
   - Pruebas de corrupción de descarga (verificación SHA-256 antes de descomprimir).
   - Manejo de falta de espacio en disco (requiere ~4.5 GB de espacio temporal y ~3.5 GB permanentes).
   - Manejo de cierres abruptos de la app durante la descarga o descompresión (archivos temporales `.tmp` y transacciones ACID de SQLite).

Por favor, comienza entregándome el plan de implementación detallado por componentes y fases de desarrollo.
```
