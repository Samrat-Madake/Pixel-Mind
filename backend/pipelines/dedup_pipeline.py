import imagehash
from PIL import Image
from backend.utils.config import PHASH_THRESHOLD
from backend.db.db import get_db_connection

class DedupPipeline:
    @staticmethod
    def compute_phash(image_path: str) -> str:
        """Compute pHash (Perceptual Hash) for semantic duplicate check."""
        try:
            img = Image.open(image_path)
            # phash uses 8x8 DCT by default
            p_hash = imagehash.phash(img)
            return str(p_hash)
        except:
            return None

    @staticmethod
    def check_and_register_duplicates(image_id: int, current_phash: str):
        """Find other images with similar pHash and record in duplicates table."""
        if not current_phash: return
        
        current_hash_obj = imagehash.hex_to_hash(current_phash)
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # In a massive database, we wouldn't scan all. 
        # But for 10K-20K photos, fetching hashes is fast.
        cursor.execute("SELECT id, phash FROM images WHERE id != ? AND phash IS NOT NULL", (image_id,))
        rows = cursor.fetchall()
        
        duplicates = []
        for other_id, other_phash in rows:
            other_hash_obj = imagehash.hex_to_hash(other_phash)
            distance = current_hash_obj - other_hash_obj
            
            if distance <= PHASH_THRESHOLD:
                # Lower image_id always first to avoid duplicate entries (a,b) vs (b,a)
                id_a, id_b = min(image_id, other_id), max(image_id, other_id)
                duplicates.append((id_a, id_b, int(distance)))
        
        if duplicates:
            cursor.executemany(
                "INSERT OR REPLACE INTO duplicates (image_id_a, image_id_b, phash_distance) VALUES (?, ?, ?)",
                duplicates
            )
            conn.commit()
            
        conn.close()

# Global instance
dedup_pipeline = DedupPipeline()
