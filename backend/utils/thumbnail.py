from PIL import Image
from pathlib import Path
from backend.utils.config import THUMBNAILS_DIR, THUMBNAIL_SIZE

class ThumbnailPipeline:
    @staticmethod
    def generate(image_path: str, image_id: int) -> str:
        """Generate 256x256 thumbnail for the given image."""
        try:
            img = Image.open(image_path)
            # Use thumbnail() to preserve aspect ratio
            img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            
            # Create a clean canvas to handle transparency issues if any
            canvas = Image.new("RGB", img.size, (0, 0, 0))
            canvas.paste(img)
            
            thumb_path = THUMBNAILS_DIR / f"{image_id}.jpg"
            canvas.save(thumb_path, "JPEG", quality=85)
            
            return str(thumb_path)
        except Exception as e:
            print(f"Thumbnail generation error for image {image_id}: {e}")
            return None

# Global instance
thumbnail_pipeline = ThumbnailPipeline()
