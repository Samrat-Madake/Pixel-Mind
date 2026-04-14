import numpy as np
from typing import List, Dict, Any, Optional
from backend.pipelines.clip_pipeline import get_clip_pipeline
from backend.search.faiss_store import faiss_clip
from backend.db.db import get_db_connection
import os

class SearchEngine:
    def __init__(self):
        self.clip = None # Lazy load

    def _get_clip(self):
        if self.clip is None:
            self.clip = get_clip_pipeline()
        return self.clip

    def search(self, query: str = None, k: int = 50) -> List[Dict[str, Any]]:
        """
        Main search entry point. 
        Currently supports Semantic Search via CLIP.
        Will be expanded for filters and person search as per Phase 3 plan.
        """
        results = []
        
        if query:
            # 1. Encode query
            clip = self._get_clip()
            query_vector = clip.encode_text(query)
            
            # 2. Search FAISS
            indices, distances = faiss_clip.search(query_vector, k=k)
            
            # 3. Fetch details from DB
            conn = get_db_connection()
            cursor = conn.cursor()
            
            for idx_id, dist in zip(indices, distances):
                if idx_id == -1: continue
                
                # Fetch image metadata and file info
                cursor.execute("""
                    SELECT images.id, images.file_path, images.width, images.height, 
                           metadata.shot_date, metadata.location
                    FROM embeddings_map 
                    JOIN images ON embeddings_map.image_id = images.id
                    LEFT JOIN metadata ON images.id = metadata.image_id
                    WHERE embeddings_map.faiss_index_id = ?
                """, (int(idx_id),))
                
                row = cursor.fetchone()
                if row:
                    results.append({
                        "id": row["id"],
                        "file_path": row["file_path"],
                        "filename": os.path.basename(row["file_path"]),
                        "width": row["width"],
                        "height": row["height"],
                        "shot_date": row["shot_date"],
                        "location": row["location"],
                        "score": float(dist)
                    })
            
            conn.close()
            
        return results

# Global instance
search_engine = SearchEngine()
