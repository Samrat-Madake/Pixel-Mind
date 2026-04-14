from fastapi import APIRouter
from backend.db.db import get_db_connection
from backend.utils.config import THUMBNAILS_DIR
import os

router = APIRouter(prefix="/people", tags=["people"])

@router.get("/")
async def get_people():
    """Get all face clusters with metadata."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch clusters with their representative thumbnail if available
    cursor.execute("""
        SELECT id, label, face_count, thumbnail_face_id 
        FROM clusters 
        ORDER BY face_count DESC
    """)
    clusters = []
    for row in cursor.fetchall():
        cluster_info = dict(row)
        
        # If no custom label, give a default one
        if not cluster_info["label"]:
            cluster_info["label"] = f"Person {cluster_info['id']}"
            
        clusters.append(cluster_info)
        
    conn.close()
    return clusters

@router.get("/{cluster_id}/images")
async def get_cluster_images(cluster_id: int):
    """Get all images containing a specific person cluster."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT images.id, images.file_path, faces.bbox_x, faces.bbox_y, faces.bbox_w, faces.bbox_h
        FROM faces
        JOIN images ON faces.image_id = images.id
        WHERE faces.cluster_id = ?
    """, (cluster_id,))
    
    results = []
    for row in cursor.fetchall():
        results.append({
            "id": row["id"],
            "file_path": row["file_path"],
            "filename": os.path.basename(row["file_path"]),
            "bbox": [row["bbox_x"], row["bbox_y"], row["bbox_w"], row["bbox_h"]]
        })
        
    conn.close()
    return results
