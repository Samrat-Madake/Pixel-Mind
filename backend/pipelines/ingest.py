import os
import hashlib
import asyncio
import traceback
from pathlib import Path
from typing import List, Generator
from PIL import Image

from backend.db.db import get_db_connection
from backend.pipelines.clip_pipeline import get_clip_pipeline
from backend.pipelines.face_pipeline import get_face_pipeline
from backend.pipelines.exif_pipeline import exif_pipeline
from backend.pipelines.dedup_pipeline import dedup_pipeline
from backend.utils.thumbnail import thumbnail_pipeline
from backend.search.faiss_store import faiss_clip

class IngestModule:
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}

    def __init__(self):
        self.queue = asyncio.Queue()
        self.is_processing = False
        self.processed_count = 0
        self.total_count = 0

    def scan_folder(self, folder_path: str) -> List[Path]:
        path = Path(folder_path)
        if not path.exists():
            return []
        
        image_paths = []
        for ext in self.ALLOWED_EXTENSIONS:
            image_paths.extend(path.rglob(f"*{ext}"))
            image_paths.extend(path.rglob(f"*{ext.upper()}"))
        return list(set(image_paths))

    @staticmethod
    def compute_sha256(file_path: Path) -> str:
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"SHA-256 error for {file_path}: {e}")
            return None

    def get_image_id_by_sha256(self, sha256: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM images WHERE sha256 = ?", (sha256,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    async def add_to_queue(self, folder_path: str):
        files = self.scan_folder(folder_path)
        self.total_count += len(files)
        for file in files:
            await self.queue.put(file)
        
        if not self.is_processing:
            asyncio.create_task(self.process_queue())
        
        return len(files)

    async def process_queue(self):
        """Orchestrate all AI pipelines for each image in the queue."""
        self.is_processing = True
        
        # Lazy load heavy pipelines only when processing starts
        clip = get_clip_pipeline()
        face_p = get_face_pipeline()
        
        # Persistent connection for the duration of processing to avoid lock contention
        conn = get_db_connection()
        
        while not self.queue.empty():
            file_path = await self.queue.get()
            try:
                # 1. SHA-256 binary dedup
                sha256 = self.compute_sha256(file_path)
                if not sha256: continue
                
                # Check within the persistent connection
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM images WHERE sha256 = ?", (sha256,))
                existing_id = cursor.fetchone()
                
                if existing_id:
                    print(f"Skipping already indexed: {file_path}")
                    self.processed_count += 1
                    continue

                print(f"Processing: {file_path}")
                img_obj = Image.open(file_path)
                width, height = img_obj.size
                
                # 2. Add to images table
                cursor.execute(
                    "INSERT INTO images (file_path, sha256, width, height) VALUES (?, ?, ?, ?)",
                    (str(file_path), sha256, width, height)
                )
                image_id = cursor.lastrowid
                
                # 3. CLIP Semantic Encoding
                clip_vec = clip.encode_image(str(file_path))
                faiss_id = faiss_clip.add(clip_vec)
                cursor.execute(
                    "INSERT INTO embeddings_map (image_id, faiss_index_id) VALUES (?, ?)",
                    (image_id, int(faiss_id))
                )
                
                # 4. EXIF & Metadata
                metadata = exif_pipeline.extract(str(file_path))
                cursor.execute(
                    """INSERT INTO metadata 
                       (image_id, shot_date, lat, lon, camera_make, camera_model, location) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (image_id, metadata["shot_date"], metadata["lat"], 
                     metadata["lon"], metadata["camera_make"], 
                     metadata["camera_model"], metadata["location"])
                )
                
                # 5. Semantic Dedup (pHash)
                phash = dedup_pipeline.compute_phash(str(file_path))
                cursor.execute("UPDATE images SET phash = ? WHERE id = ?", (phash, image_id))
                
                # 6. Face Detection & Clustering
                faces = face_p.detect_and_embed(str(file_path))
                for f in faces:
                    cluster_id = face_p.assign_cluster(f["embedding"], cursor=cursor)
                    # Save embedding to FAISS
                    from backend.search.faiss_store import faiss_face
                    f_faiss_id = faiss_face.add(f["embedding"])
                    
                    cursor.execute(
                        """INSERT INTO faces 
                           (image_id, bbox_x, bbox_y, bbox_w, bbox_h, cluster_id, faiss_index_id, confidence) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (image_id, f["bbox"][0], f["bbox"][1], 
                         f["bbox"][2]-f["bbox"][0], f["bbox"][3]-f["bbox"][1], 
                         int(cluster_id), int(f_faiss_id), f["confidence"])
                    )
                
                # 7. Thumbnails
                thumbnail_pipeline.generate(str(file_path), image_id)
                
                # 8. Late-stage dedup check (requires image to be in DB first)
                dedup_pipeline.check_and_register_duplicates(image_id, phash, cursor=cursor)

                # Commit everything for this image
                conn.commit()
                
                print(f"Indexed {image_id}: {file_path}")

            except Exception as e:
                print(f"Failed to process {file_path}: {e}")
                traceback.print_exc()
                conn.rollback()
            finally:
                self.processed_count += 1
                self.queue.task_done()
        
        conn.close()
        self.is_processing = False
        print("Queue processing complete.")

# Global instance
ingest_module = IngestModule()
