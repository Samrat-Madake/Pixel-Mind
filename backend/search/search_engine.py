import numpy as np
from typing import List, Dict, Any, Optional
from backend.pipelines.clip_pipeline import get_clip_pipeline
from backend.search.faiss_store import faiss_clip
from backend.search.filters import SQLiteFilters
from backend.graph.graph_manager import graph_manager
from backend.db.db import get_db_connection
import os

class SearchEngine:
    def __init__(self):
        self.clip = None

    def _get_clip(self):
        if self.clip is None:
            self.clip = get_clip_pipeline()
        return self.clip

    def search(self, query: str = None, filters: dict = None, person: str = None, k: int = 50) -> List[Dict[str, Any]]:
        """
        3-path merge + re-ranking search engine.
        """
        results_sets = []
        
        # 1. Text Query (Semantic Search)
        clip_scores = {}
        if query:
            clip = self._get_clip()
            query_vector = clip.encode_text(query)
            indices, distances = faiss_clip.search(query_vector, k=k*2) # Fetch more to allow intersection
            
            clip_ids = []
            conn = get_db_connection()
            cursor = conn.cursor()
            
            for idx_id, dist in zip(indices, distances):
                if idx_id == -1: continue
                cursor.execute("SELECT image_id FROM embeddings_map WHERE faiss_index_id = ?", (int(idx_id),))
                row = cursor.fetchone()
                if row:
                    img_id = row["image_id"]
                    clip_ids.append(img_id)
                    clip_scores[img_id] = float(dist)
                    
            conn.close()
            if clip_ids:
                results_sets.append(set(clip_ids))
            else:
                return [] # Fast fail if semantic query yields no internal DB mapping

        # 2. Metadata Filters
        if filters and any(filters.values()):
            filter_ids = SQLiteFilters.apply(filters)
            if filter_ids is not None:
                if not filter_ids:
                    return [] # Filter returned nothing
                results_sets.append(set(filter_ids))

        # 3. Person Search (Graph/DB)
        if person:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Lookup cluster by label
            cursor.execute("SELECT id FROM clusters WHERE label LIKE ?", (f"%{person}%",))
            cluster_rows = cursor.fetchall()
            
            if not cluster_rows:
                conn.close()
                return []
                
            cluster_ids = [row["id"] for row in cluster_rows]
            
            # Fetch images containing these clusters
            placeholders = ",".join(["?"] * len(cluster_ids))
            cursor.execute(f"SELECT DISTINCT image_id FROM faces WHERE cluster_id IN ({placeholders})", cluster_ids)
            person_ids = [row["image_id"] for row in cursor.fetchall()]
            conn.close()
            
            if person_ids:
                results_sets.append(set(person_ids))
            else:
                return []

        # Merge Engine (AND logic)
        if not results_sets:
            # If no query, return recent images
            final_ids = self._get_recent_images(k)
        else:
            merged_ids = set.intersection(*results_sets) if len(results_sets) > 1 else results_sets[0]
            final_ids = list(merged_ids)

        # Ranker
        # If semantic query exists, sort by clip score (lower distance is better)
        if query and clip_scores:
            final_ids.sort(key=lambda x: clip_scores.get(x, 999.0))
        
        # Limit to k
        final_ids = final_ids[:k]
        
        # Thumbnail Fetcher
        return self._fetch_details(final_ids, clip_scores)
        
    def _get_recent_images(self, k: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM images ORDER BY indexed_at DESC LIMIT ?", (k,))
        ids = [row["id"] for row in cursor.fetchall()]
        conn.close()
        return ids
        
    def _fetch_details(self, image_ids: list, clip_scores: dict):
        if not image_ids:
            return []
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        placeholders = ",".join(["?"] * len(image_ids))
        cursor.execute(f"""
            SELECT images.id, images.file_path, images.width, images.height, 
                   metadata.shot_date, metadata.location
            FROM images 
            LEFT JOIN metadata ON images.id = metadata.image_id
            WHERE images.id IN ({placeholders})
        """, image_ids)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row["id"],
                "file_path": row["file_path"],
                "filename": os.path.basename(row["file_path"]),
                "width": row["width"],
                "height": row["height"],
                "shot_date": row["shot_date"],
                "location": row["location"],
                "score": clip_scores.get(row["id"], 0.0)
            })
            
        conn.close()
        
        # Sort results to match input ID order
        id_order = {id: i for i, id in enumerate(image_ids)}
        results.sort(key=lambda x: id_order.get(x["id"], 999))
        
        return results

# Global instance
search_engine = SearchEngine()
