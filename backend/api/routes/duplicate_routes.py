from fastapi import APIRouter, HTTPException
from backend.db.db import get_db_connection
from pydantic import BaseModel
import os

router = APIRouter(prefix="/duplicates", tags=["duplicates"])

@router.get("/")
async def get_duplicates(threshold: int = 8):
    """List near-duplicate image pairs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch pairs and their file paths
    cursor.execute("""
        SELECT d.image_id_a, d.image_id_b, d.phash_distance,
               i1.file_path as path_a, i2.file_path as path_b
        FROM duplicates d
        JOIN images i1 ON d.image_id_a = i1.id
        JOIN images i2 ON d.image_id_b = i2.id
        WHERE d.phash_distance <= ?
        ORDER BY d.phash_distance ASC
    """, (threshold,))
    
    results = []
    for row in cursor.fetchall():
        results.append({
            "image_a": {
                "id": row["image_id_a"],
                "path": row["path_a"],
                "filename": os.path.basename(row["path_a"])
            },
            "image_b": {
                "id": row["image_id_b"],
                "path": row["path_b"],
                "filename": os.path.basename(row["path_b"])
            },
            "distance": row["phash_distance"]
        })
        
    conn.close()
    return results

class DeleteDuplicateRequest(BaseModel):
    keep_id: int
    delete_id: int

@router.post("/delete")
async def delete_duplicate(req: DeleteDuplicateRequest):
    """Delete a confirmed duplicate image."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Verify both exist and are in the duplicates table
    cursor.execute("""
        SELECT 1 FROM duplicates 
        WHERE (image_id_a = ? AND image_id_b = ?) 
           OR (image_id_a = ? AND image_id_b = ?)
    """, (req.keep_id, req.delete_id, req.delete_id, req.keep_id))
    
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Images are not marked as duplicates")
        
    # 2. Get file path to delete
    cursor.execute("SELECT file_path FROM images WHERE id = ?", (req.delete_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Image to delete not found")
        
    file_path = row["file_path"]
    
    # 3. Delete from database (cascade should handle related records)
    cursor.execute("DELETE FROM images WHERE id = ?", (req.delete_id,))
    
    # Also delete the duplicate relationship explicitly just in case cascade fails
    cursor.execute("""
        DELETE FROM duplicates 
        WHERE (image_id_a = ? AND image_id_b = ?) 
           OR (image_id_a = ? AND image_id_b = ?)
    """, (req.keep_id, req.delete_id, req.delete_id, req.keep_id))
    
    conn.commit()
    conn.close()
    
    # 4. Delete from filesystem
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        # DB deletion succeeded but FS failed
        return {"message": f"Deleted from DB, but failed to delete file: {e}"}
        
    return {"message": "Duplicate deleted successfully"}
