import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import numpy as np
from backend.utils.config import MODELS_DIR, DBSCAN_EPS
from backend.db.db import get_db_connection

class FacePipeline:
    def __init__(self):
        self.device = "cpu"
        print("Loading Face models (MTCNN + FaceNet)...")
        
        self.mtcnn = MTCNN(
            device=self.device, 
            keep_all=True
        )
        
        self.facenet = InceptionResnetV1(
            pretrained='vggface2', 
            device=self.device
        ).eval()
        
        # Cache for incremental clustering centroids
        self.centroids = {} # cluster_id -> np.ndarray (mean embedding)
        self.cluster_counts = {} # cluster_id -> int
        self._load_incremental_state()
        print("Face models loaded.")

    def _load_incremental_state(self):
        """Pre-load existing centroids from DB on startup for incremental clustering."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if centroids table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cluster_centroids'")
        if not cursor.fetchone():
            cursor.execute("CREATE TABLE cluster_centroids (cluster_id INTEGER PRIMARY KEY, centroid BLOB)")
            conn.commit()
        
        cursor.execute("SELECT cluster_id, centroid FROM cluster_centroids")
        for row in cursor.fetchall():
            c_id = row['cluster_id']
            centroid = np.frombuffer(row['centroid'], dtype=np.float32)
            self.centroids[c_id] = centroid
            
        cursor.execute("SELECT id, face_count FROM clusters")
        for row in cursor.fetchall():
            self.cluster_counts[row['id']] = row['face_count']
            
        conn.close()

    def detect_and_embed(self, image_path: str):
        """Detect faces in image and return bounding boxes + embeddings."""
        img = Image.open(image_path).convert("RGB")
        
        # 1. Detect faces
        boxes, probs = self.mtcnn.detect(img)
        
        results = []
        if boxes is not None:
            for i, box in enumerate(boxes):
                if probs[i] < 0.90: continue # High confidence only
                
                # 2. Extract and pre-process face crop
                face_crop = img.crop(box)
                face_tensor = self._preprocess_face(face_crop)
                
                # 3. Get 128-D embedding
                with torch.no_grad():
                    embedding = self.facenet(face_tensor.unsqueeze(0)).cpu().numpy().flatten()
                
                results.append({
                    "bbox": box.tolist(),
                    "confidence": float(probs[i]),
                    "embedding": embedding
                })
        
        return results

    def _preprocess_face(self, face_crop):
        """Resize and normalize face crop for FaceNet."""
        face_crop = face_crop.resize((160, 160), Image.BILINEAR)
        face_tensor = np.array(face_crop).astype(np.float32)
        face_tensor = (face_tensor - 127.5) / 128.0 # Normalize
        return torch.from_numpy(face_tensor).permute(2, 0, 1)

 
    def assign_cluster(self, embedding: np.ndarray, cursor=None) -> int:
        """
        Incremental Clustering (Nearest Centroid).
        If nearest centroid is within DBSCAN_EPS, assign to that cluster.
        Otherwise, create new cluster.
        """
        best_cluster_id = -1
        min_dist = float('inf')
        
        # Ensure embedding is L2 normalized for cosine similarity via dot product
        embedding = embedding / np.linalg.norm(embedding)
        
        for cluster_id, centroid in self.centroids.items():
            # Cosine distance (1 - similarity)
            dist = 1.0 - np.dot(embedding, centroid)
            if dist < min_dist:
                min_dist = dist
                best_cluster_id = cluster_id
        
        own_cursor = False
        if cursor is None:
            conn = get_db_connection()
            db_cursor = conn.cursor()
            own_cursor = True
        else:
            db_cursor = cursor
        
        if best_cluster_id != -1 and min_dist < DBSCAN_EPS:
            # Update existing cluster centroid (running mean)
            self._update_centroid(best_cluster_id, embedding)
            # Update DB
            db_cursor.execute("UPDATE clusters SET face_count = face_count + 1 WHERE id = ?", (best_cluster_id,))
            db_cursor.execute("UPDATE cluster_centroids SET centroid = ? WHERE cluster_id = ?", 
                           (self.centroids[best_cluster_id].tobytes(), best_cluster_id))
        else:
            # Create new cluster
            db_cursor.execute("INSERT INTO clusters (face_count) VALUES (1)")
            new_id = db_cursor.lastrowid
            self.centroids[new_id] = embedding
            self.cluster_counts[new_id] = 1
            db_cursor.execute("INSERT INTO cluster_centroids (cluster_id, centroid) VALUES (?, ?)",
                           (new_id, embedding.tobytes()))
            best_cluster_id = new_id
        
        if own_cursor:
            conn.commit()
            conn.close()
            
        return best_cluster_id

    def _update_centroid(self, cluster_id, new_embedding):
        old_mean = self.centroids[cluster_id]
        n = self.cluster_counts.get(cluster_id, 1)
        self.centroids[cluster_id] = (old_mean * n + new_embedding) / (n + 1)
        self.cluster_counts[cluster_id] = n + 1

# Global instance
_face_pipeline = None

def get_face_pipeline():
    global _face_pipeline
    if _face_pipeline is None:
        _face_pipeline = FacePipeline()
    return _face_pipeline
