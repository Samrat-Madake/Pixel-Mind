from fastapi import APIRouter
from typing import List, Dict, Any
import numpy as np
from sklearn.cluster import KMeans
from backend.search.faiss_store import faiss_clip
from backend.pipelines.clip_pipeline import get_clip_pipeline
from backend.db.db import get_db_connection

router = APIRouter(prefix="/things", tags=["things"])

# Broad categories for auto-labeling clusters
LABEL_CANDIDATES = [
    "Cars", "Mountains", "Beaches", "Dogs", "Cats", "Food", "Cityscapes", 
    "Nature", "Architecture", "Sunsets", "Portraits", "Documents", "Flowers",
    "Interiors", "Forest", "Night", "Sports", "Art", "Selfies", "Group Photos"
]

@router.get("/")
async def get_things():
    total_images = faiss_clip.index.ntotal
    if total_images < 5:
        return []

    # 1. Fetch all embeddings
    # FAISS IndexFlatL2 allows reconstruction
    embeddings = []
    image_ids = []
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for i in range(total_images):
        try:
            cursor.execute("SELECT image_id FROM embeddings_map WHERE faiss_index_id = ?", (i,))
            res = cursor.fetchone()
            if res:
                vec = faiss_clip.reconstruct(i)
                embeddings.append(vec)
                image_ids.append(res["image_id"])
        except Exception as e:
            print(f"Error reconstructing embedding {i}: {e}")
            continue
            
    if not embeddings:
        conn.close()
        return []

    embeddings = np.array(embeddings)
    
    # 2. Cluster
    n_clusters = min(12, max(3, total_images // 10))
    kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    cluster_labels = kmeans.fit_predict(embeddings)
    
    # 3. Label Clusters using Zero-Shot
    clip = get_clip_pipeline()
    text_features = np.array([clip.encode_text(c) for c in LABEL_CANDIDATES])
    
    results = []
    for i in range(n_clusters):
        cluster_indices = np.where(cluster_labels == i)[0]
        if len(cluster_indices) < 2: continue # Skip tiny clusters
        
        centroid = kmeans.cluster_centers_[i]
        centroid = centroid / np.linalg.norm(centroid)
        
        # Find best label
        similarities = np.dot(text_features, centroid)
        best_label_idx = np.argmax(similarities)
        
        label = LABEL_CANDIDATES[best_label_idx]
        if similarities[best_label_idx] < 0.20:
            label = f"Collection {i+1}"
            
        # Representative image (closest to centroid)
        cluster_embs = embeddings[cluster_indices]
        dists = np.linalg.norm(cluster_embs - kmeans.cluster_centers_[i], axis=1)
        rep_idx = cluster_indices[np.argmin(dists)]
        
        results.append({
            "id": f"cluster_{i}",
            "label": label,
            "image_count": len(cluster_indices),
            "thumbnail_image_id": image_ids[rep_idx],
            "image_ids": [image_ids[idx] for idx in cluster_indices]
        })
        
    conn.close()
    # Sort by count
    results.sort(key=lambda x: x["image_count"], reverse=True)
    return results

@router.get("/{cluster_id}")
async def get_thing_images(cluster_id: str):
    # This is a bit inefficient as it re-clusters, but for small sets it's fine.
    # In a real app, we'd persist cluster assignments.
    all_things = await get_things()
    for thing in all_things:
        if thing["id"] == cluster_id:
            return [{"id": img_id} for img_id in thing["image_ids"]]
    return []
