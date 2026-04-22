import sys
import os
import numpy as np

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.pipelines.face_pipeline import get_face_pipeline
from backend.search.faiss_store import faiss_face
from backend.db.db import get_db_connection

def update_clusters():
    print("--- Re-clustering existing faces ---")
    
    pipeline = get_face_pipeline()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Fetch all faces without a cluster_id
    cursor.execute("SELECT id, faiss_index_id FROM faces WHERE cluster_id IS NULL OR cluster_id = 0")
    rows = cursor.fetchall()
    
    if not rows:
        print("No unclustered faces found.")
        conn.close()
        return

    print(f"Found {len(rows)} faces to cluster.")
    
    updated_count = 0
    for row in rows:
        face_db_id = row['id']
        faiss_idx = row['faiss_index_id']
        
        if faiss_idx is None:
            print(f"Warning: Face ID {face_db_id} has no faiss_index_id. Skipping.")
            continue
            
        # 2. Reconstruct vector from FAISS
        try:
            embedding = faiss_face.reconstruct(faiss_idx)
            
            # 3. Assign cluster
            cluster_id = pipeline.assign_cluster(embedding, cursor=cursor)
            
            # 4. Update DB
            cursor.execute("UPDATE faces SET cluster_id = ? WHERE id = ?", (cluster_id, face_db_id))
            updated_count += 1
            
            if updated_count % 10 == 0:
                print(f"Clustered {updated_count}/{len(rows)} faces...")
                
        except Exception as e:
            print(f"Error reconstructing vector for face {face_db_id}: {e}")
            
    conn.commit()
    conn.close()
    print(f"Successfully clustered {updated_count} faces.")

if __name__ == "__main__":
    update_clusters()
