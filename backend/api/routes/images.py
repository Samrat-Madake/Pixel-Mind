from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from backend.utils.config import THUMBNAILS_DIR
from backend.db.db import get_db_connection

router = APIRouter(prefix="/images", tags=["images"])

@router.get("/thumbnail/{image_id}")
async def get_thumbnail(image_id: int):
    """Serve a 256x256 thumbnail for the given image ID."""
    thumbnail_path = THUMBNAILS_DIR / f"{image_id}.jpg"
    
    if os.path.exists(thumbnail_path):
        return FileResponse(thumbnail_path)
    else:
        # If thumbnail doesn't exist, we might want to trigger generation 
        # or return a placeholder. For now, 404.
        raise HTTPException(status_code=404, detail="Thumbnail not found")

@router.get("/full/{image_id}")
async def get_full_image(image_id: int):
    """Serve the original full-resolution image."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM images WHERE id = ?", (image_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row and os.path.exists(row["file_path"]):
        return FileResponse(row["file_path"])
    else:
        raise HTTPException(status_code=404, detail="Image path not found in database or filesystem")
