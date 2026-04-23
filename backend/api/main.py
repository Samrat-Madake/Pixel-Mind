from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Fix for OpenMP duplicate library error on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from backend.db.db import init_db, get_db_connection
from backend.search.faiss_store import faiss_clip, faiss_face
from backend.utils.config import DB_PATH

from backend.api.routes import search, images, people, index_routes, graph_routes, duplicate_routes, things

app = FastAPI(title="PixelMind API")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(search.router)
app.include_router(images.router)
app.include_router(people.router)
app.include_router(index_routes.router)
app.include_router(graph_routes.router)
app.include_router(duplicate_routes.router)
app.include_router(things.router)

@app.on_event("startup")
async def startup_event():
    # Initialize DB on startup
    init_db()

@app.get("/health")
async def health_check():
    db_ok = os.path.exists(DB_PATH)
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        db_connected = True
    except Exception:
        db_connected = False

    return {
        "status": "ok",
        "db": {
            "exists": db_ok,
            "connected": db_connected
        },
        "faiss": {
            "clip_count": faiss_clip.index.ntotal,
            "face_count": faiss_face.index.ntotal
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
