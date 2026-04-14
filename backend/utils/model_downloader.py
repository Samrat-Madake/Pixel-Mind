import os
import torch
import open_clip
from facenet_pytorch import MTCNN, InceptionResnetV1
from backend.utils.config import MODELS_DIR, CLIP_MODEL_NAME, CLIP_PRETRAINED

def download_models():
    print("Initializing model downloads...")
    os.makedirs(MODELS_DIR, exist_ok=True)

    # 1. CLIP Download
    print(f"Downloading CLIP {CLIP_MODEL_NAME}...")
    # This automatically caches weights in the torch cache, 
    # but we will move/symlink or just rely on default torch cache for now
    # to keep it simple, while verifying it works offline.
    model, _, preprocess = open_clip.create_model_and_transforms(
        CLIP_MODEL_NAME, 
        pretrained=CLIP_PRETRAINED,
        cache_dir=str(MODELS_DIR / "clip")
    )
    print("CLIP download complete.")

    # 2. Face Detection (MTCNN)
    print("Downloading MTCNN weights...")
    mtcnn = MTCNN(
        device='cpu', 
        keep_all=True
    )
    print("MTCNN download complete.")

    # 3. Face Embedding (FaceNet)
    print("Downloading FaceNet weights...")
    resnet = InceptionResnetV1(
        pretrained='vggface2', 
        device='cpu'
    ).eval()
    print("FaceNet download complete.")

if __name__ == "__main__":
    download_models()
