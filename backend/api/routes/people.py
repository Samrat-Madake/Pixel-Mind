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

from pydantic import BaseModel
from typing import List

class LabelRequest(BaseModel):
    cluster_id: int
    label: str

@router.post("/label-cluster")
async def label_cluster(req: LabelRequest):
    """Assign a string label to a cluster."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE clusters SET label = ? WHERE id = ?", (req.label, req.cluster_id))
    conn.commit()
    conn.close()
    return {"message": f"Cluster {req.cluster_id} labeled as {req.label}"}

class MergeRequest(BaseModel):
    cluster_ids: List[int]
    target_label: str = None

@router.post("/merge-clusters")
async def merge_clusters(req: MergeRequest):
    """Merge multiple clusters into the first one in the list."""
    if len(req.cluster_ids) < 2:
        return {"message": "Need at least 2 clusters to merge"}
        
    primary_id = req.cluster_ids[0]
    other_ids = req.cluster_ids[1:]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Reassign all faces from other_ids to primary_id
    placeholders = ",".join(["?"] * len(other_ids))
    cursor.execute(f"UPDATE faces SET cluster_id = ? WHERE cluster_id IN ({placeholders})", [primary_id] + other_ids)
    
    # 2. Update cluster count for primary_id
    cursor.execute("SELECT COUNT(*) as count FROM faces WHERE cluster_id = ?", (primary_id,))
    new_count = cursor.fetchone()["count"]
    
    # 3. Apply target_label if provided
    if req.target_label:
        cursor.execute("UPDATE clusters SET label = ?, face_count = ? WHERE id = ?", (req.target_label, new_count, primary_id))
    else:
        cursor.execute("UPDATE clusters SET face_count = ? WHERE id = ?", (new_count, primary_id))
        
    # 4. Delete the other clusters
    cursor.execute(f"DELETE FROM clusters WHERE id IN ({placeholders})", other_ids)
    
    conn.commit()
    conn.close()
    
    # Also update graph
    from backend.graph.graph_manager import graph_manager
    # In a full implementation, we'd collapse the nodes in NetworkX
    
    return {"message": f"Merged into cluster {primary_id}"}

