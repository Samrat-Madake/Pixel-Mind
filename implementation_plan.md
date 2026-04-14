# PixelMind — Offline AI Photo Intelligence System
## End-to-End Implementation Plan

> **100% Local · Zero Internet · PC/Laptop Edition**

---

## 📐 Architecture Analysis

### 1. High-Level Design (HLD)

![HLD Diagram](C:\Users\DELL\.gemini\antigravity\brain\4316703d-da61-4854-a88c-e97abe38711d\HLD.png)

The system is organized into 4 horizontal layers:

| Layer | Components |
|-------|-----------|
| **Ingest** | Photo Folder Watcher → File Scanner → Index Queue (Priority) |
| **AI Pipeline** | CLIP Pipeline · Face Pipeline · EXIF Pipeline · Dedup Engine |
| **Local AI Models** | CLIP ViT-B/32 · MTCNN · FaceNet · DBSCAN |
| **Storage** | FAISS Vector Index · SQLite DB · NetworkX Graph · File System |
| **Desktop UI** | Electron + React → Search · People · Graph · Duplicates · Settings |

---

### 2. Ingestion Pipeline (Detailed Flow)

![Ingestion Pipeline](C:\Users\DELL\.gemini\antigravity\brain\4316703d-da61-4854-a88c-e97abe38711d\Ingestion_Pipeline.png)

```
New Image
  └── Ingest Module (SHA-256 hash for duplicate check)
        ├── Already indexed? → Skip (Yes branch)
        └── No → Preprocess (Resize 224×224, Normalize pixels)
              ├── CLIP Image Encoder ViT-B/32 → 512-D vector → FAISS IVFFlat insert
              ├── EXIF Parser (Pillow/ExifTags) → shot_date, lat, lon, camera_model → SQLite
              ├── pHash Generator (DCT 8×8 → 64-bit hash) → SQLite duplicates table
              └── Face Branch:
                    MTCNN (Multi-scale CNN → bounding boxes)
                    → FaceNet (InceptionResNet → 128-D embedding)
                    → DBSCAN (eps=0.6, min=2 → cluster groups)
                    → SQLite faces table (bbox + cluster_id + confidence)
                    → NetworkX Graph (CO_APPEARS edges)
              └── ✅ Done
```

**Key design decisions:**
- SHA-256 hash pre-check prevents re-indexing unchanged files
- All AI runs locally — no outbound calls
- DBSCAN clustering done incrementally per batch

---

### 3. Retrieval Pipeline (Query Engine)

![Retrieval Pipeline](C:\Users\DELL\.gemini\antigravity\brain\4316703d-da61-4854-a88c-e97abe38711d\Retrival_Pipeline.png)

Three query paths merge into a unified results engine:

| Query Type | Path |
|---|---|
| **Text Query** | CLIP Text Encoder → 512-D vector → FAISS ANN Search (Cosine, Top-K) |
| **Filter Applied** | Parse filters (date range, GPS, camera) → SQLite WHERE + BETWEEN |
| **Person Search** | Name lookup in SQLite clusters → cluster_ids → NetworkX edge intersection → SQLite face→image join |

**Post-merge steps:**
1. Merge Engine (AND/OR set logic + deduplication)
2. Re-rank by combined similarity score
3. Lazy-load thumbnails from file system
4. Return Results Grid

---

### 4. Storage Layer Architecture

![Storage Layer](C:\Users\DELL\.gemini\antigravity\brain\4316703d-da61-4854-a88c-e97abe38711d\Storage_Layer.png)

```
┌─────────────────────────────────────────────────────────┐
│                  pixelmind.db (SQLite)                   │
│  images: id · file_path · phash · indexed_at            │
│  metadata: image_id · shot_date · lat · lon · camera    │
│  faces: image_id · cluster_id · bbox · confidence       │
│  clusters: label · face_count · thumbnail_face_id       │
│  embeddings_map: image_id · faiss_index_id              │
│  duplicates: image_id_a · image_id_b · phash_distance   │
└──────────────┬──────────────────────────────────────────┘
               │
    ┌──────────┴──────────┐──────────────────┐
    ▼                     ▼                  ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│ FAISS Index  │  │ NetworkX Graph   │  │ File System           │
│ (faiss.index)│  │ (graph.pkl)      │  │ /models/ weights      │
│ IVFFlat 256  │  │ Person Nodes     │  │ /thumbnails/ 256×256  │
│ 512-D CLIP   │  │ CO_APPEARS edges │  │ /originals/ .jpg/.png │
│ 128-D Face   │  │ APPEARS_IN edges │  │                       │
└──────────────┘  └──────────────────┘  └──────────────────────┘
```

---

### 5. Component Interaction (Sequence Diagram)

![Component Interaction](C:\Users\DELL\.gemini\antigravity\brain\4316703d-da61-4854-a88c-e97abe38711d\Component_Interaction.png)

Three end-to-end flows shown:

**Indexing Flow:**
```
User → drops folder → Electron UI → POST /index → FastAPI Backend
  → Enqueue all images → [For each image loop]:
      → CLIP: encode_image() → store vector in FAISS
      → Face Pipeline: detect_and_embed() → store faces + embeddings in SQLite
      → write EXIF metadata to SQLite
      → rebuild_graph(new_faces) in NetworkX
  → SSE progress events → Electron → "Indexing complete ✓"
```

**Search Flow:**
```
User types "birthday party 2024" → Electron → GET /search?q=...&year=2024
  → FastAPI → CLIP: encode_text() → 512-D vector
  → FAISS.search(vector, top_k=50) → candidate image_ids + scores
  → SQLite filter WHERE year=2024 → filtered image_ids
  → fetch thumbnails + metadata → JSON results list
  → Electron renders photo grid
```

**Face Label Flow:**
```
User labels cluster as "Rahul" → Electron → POST /label-cluster {cluster_id, label}
  → FastAPI → UPDATE clusters SET label='Rahul' in SQLite
  → NetworkX: update_node_label(cluster_id, 'Rahul')
  → 200 OK → "All photos update to show Rahul"
```

---

## 🛠️ Full Technology Stack

### Backend (Python Core)
| Component | Technology | Version |
|---|---|---|
| API Server | FastAPI + Uvicorn | 0.110+ |
| AI — CLIP | `open-clip-torch` (ViT-B/32) | Latest |
| AI — Face Detection | `facenet-pytorch` MTCNN | Latest |
| AI — Face Recognition | `facenet-pytorch` InceptionResNet | Latest |
| Vector Search | `faiss-cpu` / `faiss-gpu` | Latest |
| Metadata DB | SQLite3 (stdlib) | 3.x |
| Relationship Graph | NetworkX | 3.x |
| File Watcher | Watchdog | 4.x |
| Image Processing | Pillow, ImageHash | Latest |
| Geocoding (offline) | `reverse_geocoder` | Latest |
| EXIF Parsing | Pillow ExifTags | Built-in |

### Frontend (Desktop)
| Component | Technology |
|---|---|
| Desktop Shell | Electron 30+ |
| UI Framework | React 18+ |
| Build Tool | Vite |
| Styling | Tailwind CSS |
| Graph Visualization | D3.js |
| Data Fetching | TanStack Query |
| Communication | Electron IPC + FastAPI REST |

### Hardware Requirements
| Tier | Spec |
|---|---|
| Minimum | i5 8th gen, 8GB RAM, 10GB free disk |
| Recommended | i7 12th gen, 16GB RAM, NVIDIA GTX 1660+ (CUDA 11.8) |
| Speed (CPU) | ~1.2 images/sec |
| Speed (GPU) | ~35 images/sec (RTX 3070) |

---

## 📁 Project Directory Structure

```
pixelmind/
├── backend/
│   ├── api/
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── routes/
│   │   │   ├── index.py             # POST /index
│   │   │   ├── search.py            # GET /search
│   │   │   ├── people.py            # GET/POST /people, /label-cluster
│   │   │   ├── graph.py             # GET /graph
│   │   │   └── duplicates.py        # GET /duplicates
│   │   └── sse.py                   # Server-Sent Events for progress
│   ├── pipelines/
│   │   ├── ingest.py                # File scanner + queue manager
│   │   ├── clip_pipeline.py         # CLIP image + text encoding
│   │   ├── face_pipeline.py         # MTCNN + FaceNet + DBSCAN
│   │   ├── exif_pipeline.py         # EXIF metadata extraction
│   │   └── dedup_pipeline.py        # pHash duplicate detection
│   ├── db/
│   │   ├── schema.sql               # SQLite table definitions
│   │   ├── db.py                    # Connection & query helpers
│   │   └── migrations/              # Schema version migrations
│   ├── graph/
│   │   ├── graph_manager.py         # NetworkX build/update/query
│   │   └── graph_queries.py         # Common graph traversal queries
│   ├── search/
│   │   ├── search_engine.py         # Merge engine + re-ranking
│   │   ├── faiss_store.py           # FAISS CRUD operations
│   │   └── filters.py               # SQLite filter helpers
│   └── utils/
│       ├── thumbnail.py             # Thumbnail generation (256×256)
│       ├── geocoder.py              # Offline reverse geocoding
│       └── config.py                # App-level config (paths, params)
├── frontend/
│   ├── electron/
│   │   ├── main.js                  # Electron main process
│   │   ├── preload.js               # Context bridge (IPC)
│   │   └── updater.js               # Auto-update logic
│   └── src/
│       ├── App.jsx
│       ├── pages/
│       │   ├── Search.jsx           # Semantic search UI
│       │   ├── People.jsx           # Face clusters + labeling
│       │   ├── Graph.jsx            # D3.js relationship explorer
│       │   ├── Duplicates.jsx       # Duplicate management
│       │   └── Settings.jsx         # Path config, model settings
│       ├── components/
│       │   ├── PhotoGrid.jsx
│       │   ├── FaceCard.jsx
│       │   ├── SearchBar.jsx
│       │   ├── FilterPanel.jsx
│       │   └── ProgressBar.jsx
│       └── api/
│           └── client.js            # TanStack Query + fetch wrappers
├── models/
│   ├── clip/                        # CLIP ViT-B/32 weights
│   ├── facenet/                     # FaceNet InceptionResNet weights
│   └── mtcnn/                       # MTCNN weights
├── data/
│   ├── pixelmind.db                 # SQLite database
│   ├── faiss.index                  # CLIP vector index
│   ├── face.index                   # FaceNet vector index
│   ├── graph.pkl                    # NetworkX serialized graph
│   └── thumbnails/                  # 256×256 JPEG cache
└── scripts/
    ├── setup.py                     # Download models + init DB
    └── build.py                     # PyInstaller + Electron packaging
```

---

## 🗓️ Phase-Wise Implementation Plan

---

### Phase 1 — Foundation & Environment Setup (Weeks 1–2)

**Goal:** Working skeleton with DB schema, model download, and basic project structure.

#### Deliverables
- [x] Python virtual environment configured
- [x] All AI model weights downloaded and cached locally
- [x] SQLite schema created and validated
- [x] FAISS index initialized (empty)
- [x] FastAPI server boots successfully
- [x] Electron + React + Vite scaffold created

#### Detailed Steps

**1.1 Environment Setup**
```bash
# Python environment
python -m venv .venv
pip install fastapi uvicorn[standard] faiss-cpu open-clip-torch \
            facenet-pytorch pillow imagehash networkx watchdog \
            reverse_geocoder scipy numpy

# Frontend scaffold
cd frontend
npm create vite@latest . -- --template react
npm install electron tailwindcss d3 @tanstack/react-query
```

**1.2 Model Download Script** (`scripts/setup.py`)
- Download `CLIP ViT-B/32` via `open_clip.create_model_and_transforms()`
- Download `MTCNN` + `InceptionResnetV1` via `facenet_pytorch`
- Save all weights to `models/` for offline use

**1.3 SQLite Schema** (`backend/db/schema.sql`)
```sql
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    phash TEXT,
    width INTEGER, height INTEGER,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE metadata (
    image_id INTEGER REFERENCES images(id),
    shot_date TEXT, lat REAL, lon REAL,
    camera_make TEXT, camera_model TEXT
);
CREATE TABLE faces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id INTEGER REFERENCES images(id),
    bbox_x REAL, bbox_y REAL, bbox_w REAL, bbox_h REAL,
    cluster_id INTEGER, confidence REAL
);
CREATE TABLE clusters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT, thumbnail_face_id INTEGER, face_count INTEGER DEFAULT 0
);
CREATE TABLE embeddings_map (
    image_id INTEGER REFERENCES images(id),
    faiss_index_id INTEGER
);
CREATE TABLE duplicates (
    image_id_a INTEGER, image_id_b INTEGER,
    phash_distance INTEGER
);
```

**1.4 Config System** (`backend/utils/config.py`)
```python
DATA_DIR = Path("data/")
MODELS_DIR = Path("models/")
FAISS_INDEX_PATH = DATA_DIR / "faiss.index"
DB_PATH = DATA_DIR / "pixelmind.db"
GRAPH_PATH = DATA_DIR / "graph.pkl"
THUMBNAIL_DIR = DATA_DIR / "thumbnails/"
CLIP_DIM = 512
FACE_DIM = 128
DBSCAN_EPS = 0.6
DBSCAN_MIN_SAMPLES = 2
```

#### Verification
- Run `python -c "import faiss, clip, facenet_pytorch; print('OK')"` — should pass
- Run `python backend/api/main.py` → `GET /health` returns `{"status": "ok"}`
- Open `pixelmind.db` in DB Browser and confirm all 6 tables exist

---

### Phase 2 — AI Pipelines (Weeks 3–4)

**Goal:** All four AI sub-pipelines working independently with unit tests.

#### Deliverables
- [ ] `IngestModule` with SHA-256 dedup check
- [ ] `CLIPPipeline` — image + text encoding, FAISS CRUD
- [ ] `FacePipeline` — MTCNN detect → FaceNet embed → DBSCAN cluster
- [ ] `EXIFPipeline` — full metadata extraction
- [ ] `DedupPipeline` — pHash generation + Hamming distance check
- [ ] All pipelines integrated into a single `IndexQueue` worker

#### 2.1 Ingest Module (`backend/pipelines/ingest.py`)
```python
class IngestModule:
    def scan_folder(self, folder_path: str) -> list[Path]
    def compute_sha256(self, path: Path) -> str
    def is_indexed(self, sha256: str) -> bool      # Check images table
    def enqueue(self, paths: list[Path]) -> None    # Priority queue
    def process_queue(self) -> Generator           # Yields progress events
```

#### 2.2 CLIP Pipeline (`backend/pipelines/clip_pipeline.py`)
```python
class CLIPPipeline:
    model: open_clip.CLIP          # ViT-B/32
    preprocess: Callable
    tokenizer: Callable
    faiss_index: faiss.IndexIVFFlat  # nlist=256, dim=512

    def encode_image(self, path: Path) -> np.ndarray  # 512-D L2-norm
    def encode_text(self, query: str) -> np.ndarray   # 512-D L2-norm
    def add_to_index(self, vector: np.ndarray, image_id: int)
    def search(self, vector: np.ndarray, k: int) -> tuple[list[int], list[float]]
    def save_index(self)
    def load_index(self)
```

#### 2.3 Face Pipeline (`backend/pipelines/face_pipeline.py`)
```python
class FacePipeline:
    mtcnn: MTCNN
    facenet: InceptionResnetV1

    def detect_faces(self, img: PIL.Image) -> list[dict]   # bbox + crop
    def embed_face(self, face_crop: Tensor) -> np.ndarray  # 128-D
    def cluster_faces(self, all_embeddings: np.ndarray) -> np.ndarray  # DBSCAN labels
    def assign_cluster(self, embedding: np.ndarray) -> int  # Nearest cluster
    def save_faces_to_db(self, image_id, faces, clusters)
```

#### 2.4 EXIF Pipeline (`backend/pipelines/exif_pipeline.py`)
```python
class EXIFPipeline:
    def extract(self, path: Path) -> dict:
        # Returns: shot_date, lat, lon, camera_make, camera_model
    def _parse_gps(self, gps_info: dict) -> tuple[float, float]
    def _reverse_geocode(self, lat: float, lon: float) -> str  # offline
```

#### 2.5 Dedup Pipeline (`backend/pipelines/dedup_pipeline.py`)
```python
class DedupPipeline:
    def compute_phash(self, path: Path) -> str        # DCT 8×8 → 64-bit hex
    def find_duplicates(self, phash: str, threshold: int = 8) -> list[int]
    def register_duplicate(self, id_a: int, id_b: int, distance: int)
```

#### 2.6 Index Queue Worker (`backend/pipelines/ingest.py`)
```python
async def process_image(path: Path):
    # 1. SHA-256 check → skip if already indexed
    # 2. Preprocess → resize 224×224, normalize
    # 3. CLIPPipeline.encode_image() → FAISS insert
    # 4. EXIFPipeline.extract() → SQLite metadata
    # 5. DedupPipeline.compute_phash() → SQLite duplicates
    # 6. FacePipeline.detect_faces() → embed → cluster → SQLite faces
    # 7. GraphManager.update(image_id, cluster_ids)
    # 8. Yield SSE progress event
```

#### Verification
- Unit test each pipeline with 10 sample images
- Validate FAISS index search returns correct image_ids
- Validate DBSCAN clusters same person across 5+ photos

---

### Phase 3 — Graph Engine + FastAPI (Week 5)

**Goal:** Full REST API with all endpoints, graph logic, and file watcher.

#### Deliverables
- [ ] `GraphManager` for NetworkX build/update/query
- [ ] All 5 FastAPI route groups wired up
- [ ] SSE progress streaming for indexing
- [ ] Watchdog file watcher for auto-ingestion
- [ ] API tested with Postman/httpx

#### 3.1 Graph Manager (`backend/graph/graph_manager.py`)
```python
class GraphManager:
    G: nx.Graph   # Loaded from graph.pkl

    def rebuild(self, batch_faces: list[dict])
    def update(self, image_id: int, cluster_ids: list[int])
        # For every pair of cluster_ids: increment CO_APPEARS edge weight
    def get_connections(self, cluster_id: int) -> list[dict]
    def get_full_graph(self) -> dict                  # Nodes + edges for D3
    def update_node_label(self, cluster_id: int, label: str)
    def save(self)
    def load(self)
```

#### 3.2 FastAPI Endpoints (`backend/api/routes/`)

| Route | Method | Description |
|---|---|---|
| `/health` | GET | Server health check |
| `/index` | POST | Start indexing a folder path |
| `/index/progress` | GET | SSE stream for progress events |
| `/search` | GET | `?q=text&year=2024&person=Rahul` |
| `/people` | GET | All face clusters with labels |
| `/label-cluster` | POST | `{cluster_id, label}` |
| `/merge-clusters` | POST | `{cluster_ids: [1,2,3]}` |
| `/graph` | GET | Full NetworkX graph as JSON |
| `/graph/{cluster_id}` | GET | Connections for one person |
| `/duplicates` | GET | List near-duplicate image pairs |
| `/duplicates/delete` | POST | Bulk delete confirmed duplicates |
| `/thumbnail/{image_id}` | GET | Serve 256×256 JPEG |

#### 3.3 Search Engine (`backend/search/search_engine.py`)
```python
class SearchEngine:
    def search(self, query: str, filters: dict, person: str = None, k: int = 50):
        results = []
        if query:
            vec = CLIPPipeline.encode_text(query)
            clip_ids, scores = FAISSStore.search(vec, k)
            results.append(("clip", clip_ids, scores))
        if filters:
            filter_ids = SQLiteFilters.apply(filters)
            results.append(("filter", filter_ids, None))
        if person:
            cluster_ids = db.lookup_cluster(person)
            graph_ids = GraphManager.get_images_for_clusters(cluster_ids)
            results.append(("person", graph_ids, None))

        merged = MergeEngine.merge(results, logic="AND")
        ranked = Ranker.rank(merged)
        return ThumbnailFetcher.fetch(ranked)
```

#### 3.4 File Watcher (`backend/pipelines/watcher.py`)
```python
class PhotoWatcher:
    def start(self, folders: list[str])  # Watchdog observer
    def on_created(self, event)          # Trigger ingest for new files
    def on_modified(self, event)         # Re-index on file change
```

#### Verification
- `POST /index` with a folder of 50 images → complete without errors
- `GET /search?q=beach+sunset` → top-5 results visually correct
- `GET /graph` → valid JSON with nodes and edges
- SSE stream → Electron receives progress events correctly

---

### Phase 4 — Desktop UI (Weeks 6–7)

**Goal:** Full Electron + React desktop app with all 5 pages.

#### Deliverables
- [ ] Electron shell with IPC bridge
- [ ] Search page with semantic query + filters
- [ ] People page with face clusters and labeling
- [ ] D3.js relationship graph explorer
- [ ] Duplicates management page
- [ ] Settings page (folder config, model info)

#### 4.1 Electron Main Process (`frontend/electron/main.js`)
```javascript
// Spawn Python FastAPI backend as child process
// Open BrowserWindow pointing to localhost:8000
// Set up IPC handlers for native file dialogs
// Handle app quit → kill Python process
```

#### 4.2 Search Page (`frontend/src/pages/Search.jsx`)
- Search bar with debounced input (300ms)
- Filter panel: date range, camera model, GPS location
- Photo grid with lazy-loading thumbnails
- Click to open full-resolution viewer
- "Find similar" button → image-to-image search

#### 4.3 People Page (`frontend/src/pages/People.jsx`)
- Grid of face cluster thumbnails
- Click cluster → see all photos with that person
- Rename cluster via inline edit
- Merge clusters via drag-and-drop select
- Face count and first/last seen date per person

#### 4.4 Graph Explorer (`frontend/src/pages/Graph.jsx`)
```javascript
// D3.js force-directed graph
// Person nodes sized by face_count
// Edge thickness = CO_APPEARS weight
// Click node → highlight all shared photos
// Zoom/pan interaction
// Filter: show only people with >5 shared photos
```

#### 4.5 Duplicates Page (`frontend/src/pages/Duplicates.jsx`)
- Side-by-side duplicate pairs display
- pHash distance badge (lower = more similar)
- Single-click delete or Keep Both
- Bulk select and delete confirmed duplicates

#### 4.6 Settings Page (`frontend/src/pages/Settings.jsx`)
- Add/remove watched folders
- Performance: CPU vs GPU toggle
- Storage info: index size, DB size, photo count
- Re-index all / Reset database buttons

#### UI Design System
```css
/* Dark mode, glassmorphism theme */
--bg-primary: #0f0f13;
--bg-secondary: #1a1a24;
--accent: #7c6af5;        /* Purple */
--accent-secondary: #4ade80; /* Green for success */
--text-primary: #f0f0f8;
--glass: rgba(255,255,255,0.05);
--border-glass: rgba(255,255,255,0.1);
```

#### Verification
- Electron app launches and shows Search page
- Drag-and-drop folder → triggers indexing with progress bar
- Text search returns visible, correct photo grid
- People page shows clustered faces correctly
- Graph renders with correct connections

---

### Phase 5 — Packaging & Polish (Week 8)

**Goal:** Single-click installer for Windows (and Mac/Linux optionally).

#### Deliverables
- [ ] Python backend bundled with PyInstaller
- [ ] Electron app packaged with `electron-builder`
- [ ] NSIS Windows installer (.exe)
- [ ] Onboarding wizard (first-run: pick folder, download models)
- [ ] Performance profiling complete
- [ ] QA test suite passes

#### 5.1 PyInstaller Bundle
```bash
pyinstaller --onefile --name pixelmind-backend \
  --add-data "models:models" \
  --add-data "data:data" \
  backend/api/main.py
```

#### 5.2 Electron Builder (`electron-builder.yml`)
```yaml
appId: com.pixelmind.app
productName: PixelMind
files:
  - dist/**
  - electron/**
  - backend/dist/**
win:
  target: nsis
  icon: assets/icon.ico
nsis:
  oneClick: false
  allowToChangeInstallationDirectory: true
```

#### 5.3 Onboarding Wizard (First Run)
1. Welcome screen + privacy explanation
2. Pick photo folder(s)
3. GPU/CPU detection + performance estimate
4. Optional: model download progress (if not bundled)
5. Start first index → progress view
6. Done → land on Search page

#### 5.4 Performance Optimizations
- FAISS index: train IVFFlat with `nlist=256` after 10K+ images
- Thumbnail generation: background thread, never blocks UI
- CLIP inference: batch size 32 for GPU, 8 for CPU
- Face clustering: run DBSCAN full re-cluster after every 500 new faces
- SQLite: WAL mode + indexed columns (`shot_date`, `cluster_id`, `phash`)

#### Verification
- Clean Windows install → app opens, indexes 1000 photos in <30 min (CPU)
- All 5 pages functional after install
- No network requests observed (Wireshark check)
- Memory < 2GB during indexing of 10K photos

---

## 🔄 Phase Summary Table

| Phase | Duration | Key Milestone | Acceptance Criteria |
|-------|----------|---------------|---------------------|
| **1 — Foundation** | Weeks 1–2 | FastAPI boots, DB created, models downloaded | `/health` returns OK, all 6 tables exist |
| **2 — AI Pipelines** | Weeks 3–4 | All 4 pipelines process images end-to-end | 50 images indexed, faces clustered correctly |
| **3 — Graph + API** | Week 5 | All REST endpoints working, search returns results | Postman tests pass for all 12 endpoints |
| **4 — Desktop UI** | Weeks 6–7 | Electron app with 5 pages fully functional | Drag-drop folder → search results visible |
| **5 — Packaging** | Week 8 | Windows installer, onboarding wizard | Clean install + index 1000 photos in <30 min |

---

## ⚠️ Risks & Mitigations

| Risk | Mitigation |
|---|---|
| DBSCAN produces too many clusters | Tune `eps` from 0.6 → 0.5 based on dataset |
| FAISS IVFFlat accuracy drops at large scale | Switch to HNSW index after 500K+ images |
| PyInstaller + AI model size too large (>2GB) | Bundle ONNX-quantized models instead |
| Watchdog misses rapid file changes | Add SHA-256 diff check on re-scan |
| EXIF GPS missing for many phones | Fall back to camera model + timestamp clustering |

---

## 📌 Open Questions for User Review

> [!IMPORTANT]
> **Q1: GPU Support Priority**
> Should Phase 2 include CUDA/GPU path from the start, or CPU-only first and add GPU in Phase 5?

> [!IMPORTANT]
> **Q2: Model Bundling Strategy**
> Should model weights (~600MB) be bundled inside the installer, or downloaded on first run?

> [!IMPORTANT]
> **Q3: Face Clustering Approach**
> Should DBSCAN run on all faces globally (re-cluster all faces together), or incrementally (assign new faces to nearest centroid)?

> [!NOTE]
> **Q4: Image-to-Image Search**
> Should "Find Similar" work by passing the original image through CLIP again, or storing and re-using its pre-computed vector from the FAISS index?

> [!NOTE]
> **Q5: Platforms**
> Is Windows the only target for Phase 5, or should we include macOS and Linux in scope?
