# 🌌 PixelMind

**PixelMind** is a high-performance, **100% offline** AI Photo Intelligence System. Use the power of local AI to search, cluster, and organize your photo library without ever uploading a single byte to the cloud.

---

## ✨ Key Features

*   🔍 **Semantic Search**: Search your photos using natural language (e.g., *"sunset at the beach"* or *"person wearing a blue shirt"*) powered by **OpenAI's CLIP**.
*   👤 **Face Intelligence**: Automatic face detection and clustering using **MTCNN** and **FaceNet**. Group photos by person automatically.
*   📈 **Social Graph**: Discover relationships! See who appears with whom in your photos via a built-in relationship engine.
*   📷 **Metadata Extraction**: Offline EXIF parsing for camera details, dates, and locations.
*   🛡️ **Privacy First**: Everything runs locally on your CPU/GPU. No internet connection required after setup.

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+**
- **Git**
- **Windows / macOS / Linux** (Tested primarily on Windows)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/PixelMind.git
cd PixelMind

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Mac/Linux

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Setup AI Models
Download the required AI model weights (around 1.5GB total) to run the system offline:
```bash
python -m backend.utils.model_downloader
```

### 4. Index Your Photos
Update the path in your script or use the test script to ingest a folder:
```bash
python .\scripts\test_phase2.py "C:\Path\To\Your\Pictures"
```

---

## 💻 Running the Application

### Start the Backend API
The system provides a FastAPI backend that powers the search and gallery:
```bash
# Run from the project root
python -m backend.api.main
```
Once running, you can visit:
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🛠️ Project Structure

```text
pixelmind/
├── backend/            # FastAPI, AI Pipelines, DB Logic
│   ├── api/            # REST API Endpoints
│   ├── pipelines/      # CLIP, Face, EXIF, Dedup logic
│   ├── db/             # SQLite schema and connectivity
│   └── search/         # FAISS Vector Store & Search Engine
├── scripts/            # Utility and testing scripts
├── data/               # Local database and vector indices (Ignored by Git)
├── models/             # AI model weights (Ignored by Git)
└── frontend/           # (In Progress) Electron + React UI
```

---

## 📅 Roadmap
- [x] Phase 1: Foundation & DB Schema
- [x] Phase 2: AI Pipelines (CLIP & Face)
- [x] Phase 3: Graph Engine & FastAPI Backend
- [ ] Phase 4: Desktop UI (Electron + React)
- [ ] Phase 5: Installer & Packaging

---

## ⚖️ License
MIT License - See [LICENSE](LICENSE) for details.
