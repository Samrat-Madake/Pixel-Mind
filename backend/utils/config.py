import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = BASE_DIR / "backend"
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
THUMBNAILS_DIR = DATA_DIR / "thumbnails"

# Ensure directories exist
for directory in [DATA_DIR, MODELS_DIR, THUMBNAILS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Database & Index Paths
DB_PATH = DATA_DIR / "pixelmind.db"
FAISS_CLIP_PATH = DATA_DIR / "faiss_clip.index"
FAISS_FACE_PATH = DATA_DIR / "faiss_face.index"
GRAPH_PATH = DATA_DIR / "graph.pkl"

# AI Model Settings
CLIP_MODEL_NAME = "ViT-B-32"
CLIP_PRETRAINED = "openai"
CLIP_DIM = 512
FACE_DIM = 512
PHASH_THRESHOLD = 8
DBSCAN_EPS = 0.6
DBSCAN_MIN_SAMPLES = 2

# App Settings
CLIP_BATCH_SIZE = 4  # Reduced for more stability on 8GB RAM
THUMBNAIL_SIZE = (256, 256)
FAISS_NLIST = 256

# Hardware settings
CPU_ONLY = True  # As per user request
