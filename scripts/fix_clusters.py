import sys
import os
import numpy as np

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.pipelines.face_pipeline import get_face_pipeline
from backend.search.faiss_store import faiss_face
from backend.db.db import get_db_connection

def fix_cluster_metadata():
    print("--- Fixing Cluster Metadata ---")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Get all unique cluster IDs from faces
    cursor.execute("SELECT DISTINCT cluster_id FROM faces WHERE cluster_id IS NOT NULL AND cluster_id > 0")
    cluster_ids = [row[0] for row in cursor.fetchall()]
    print(f"Found {len(cluster_ids)} unique clusters in the faces table.")
    
    for c_id in cluster_ids:
        # Check if it exists in clusters table
        cursor.execute("SELECT id FROM clusters WHERE id = ?", (c_id,))
        if not cursor.fetchone():
            # Get face count
            cursor.execute("SELECT COUNT(*) FROM faces WHERE cluster_id = ?", (c_id,))
            count = cursor.fetchone()[0]
            
            # Insert into clusters
            cursor.execute("INSERT INTO clusters (id, label, face_count) VALUES (?, ?, ?)", 
                           (c_id, f"Person {c_id}", count))
            
            # Compute centroid from all faces in this cluster
            cursor.execute("SELECT faiss_index_id FROM faces WHERE cluster_id = ?", (c_id,))
            faiss_ids = [row[0] for row in cursor.fetchall()]
            
            embeddings = []
            for f_id in faiss_ids:
                try:
                    emb = faiss_face.reconstruct(f_id)
                    embeddings.append(emb)
                except:
                    continue
            
            if embeddings:
                centroid = np.mean(embeddings, axis=0)
                centroid = centroid / np.linalg.norm(centroid)
                
                # Check centroids table
                cursor.execute("SELECT cluster_id FROM cluster_centroids WHERE cluster_id = ?", (c_id,))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO cluster_centroids (cluster_id, centroid) VALUES (?, ?)",
                                   (c_id, centroid.tobytes()))
                else:
                    cursor.execute("UPDATE cluster_centroids SET centroid = ? WHERE cluster_id = ?",
                                   (centroid.tobytes(), c_id))
            
            print(f"Initialized Cluster {c_id} with {count} faces.")
            
    conn.commit()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    fix_cluster_metadata()
