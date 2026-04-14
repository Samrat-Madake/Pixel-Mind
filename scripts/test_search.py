import sys
import os
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.pipelines.clip_pipeline import get_clip_pipeline
from backend.search.faiss_store import faiss_clip
from backend.db.db import get_db_connection

def test_search(query: str, k: int = 5):
    print(f"\n--- Testing Search for: '{query}' ---")
    
    # 1. Load CLIP and encode text
    clip = get_clip_pipeline()
    query_vector = clip.encode_text(query)
    
    # 2. Search FAISS index
    indices, distances = faiss_clip.search(query_vector, k=k)
    
    # 3. Lookup image paths in DB
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print(f"\nTop {k} results:")
    print("-" * 50)
    
    found = 0
    for idx_id, dist in zip(indices, distances):
        if idx_id == -1: continue # FAISS returns -1 if not enough results
        
        cursor.execute("""
            SELECT images.id, images.file_path 
            FROM embeddings_map 
            JOIN images ON embeddings_map.image_id = images.id
            WHERE embeddings_map.faiss_index_id = ?
        """, (int(idx_id),))
        row = cursor.fetchone()
        
        if row:
            img_id, path = row
            # Distance in IndexFlatL2 is L2 distance (lower is better)
            # Clip vectors are normalized, so L2 distance relate to cosine similarity
            print(f"[{found+1}] ID: {img_id} | Score (Dist): {dist:.4f} | Path: {os.path.basename(path)}")
            found += 1
    
    if found == 0:
        print("No results found in database for these indices.")
        
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test CLIP semantic search")
    parser.add_argument("query", type=str, help="Search query (e.g., 'mountain')")
    parser.add_argument("--k", type=int, default=5, help="Number of results to return")
    
    args = parser.parse_args()
    test_search(args.query, args.k)
