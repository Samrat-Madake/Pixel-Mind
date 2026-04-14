import torch
import open_clip
from PIL import Image
import numpy as np
from backend.utils.config import CLIP_MODEL_NAME, CLIP_PRETRAINED, MODELS_DIR

class CLIPPipeline:
    def __init__(self):
        self.device = "cpu"
        print(f"Loading CLIP model {CLIP_MODEL_NAME} on {self.device}...")
        
        cache_dir = str(MODELS_DIR / "clip")
        model, _, preprocess = open_clip.create_model_and_transforms(
            CLIP_MODEL_NAME, 
            pretrained=CLIP_PRETRAINED,
            device=self.device,
            cache_dir=cache_dir
        )
        self.model = model
        self.preprocess = preprocess
        self.tokenizer = open_clip.get_tokenizer(CLIP_MODEL_NAME)
        self.model.eval()
        print("CLIP model loaded.")

    def encode_image(self, image_path: str) -> np.ndarray:
        """Encode image to 512-D normalized vector."""
        image = Image.open(image_path).convert("RGB")
        image_input = self.preprocess(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            image_features = self.model.encode_image(image_input)
            image_features /= image_features.norm(dim=-1, keepdim=True)
            
        return image_features.cpu().numpy().flatten()

    def encode_text(self, text: str) -> np.ndarray:
        """Encode search query text to 512-D normalized vector."""
        text_input = self.tokenizer([text]).to(self.device)
        
        with torch.no_grad():
            text_features = self.model.encode_text(text_input)
            text_features /= text_features.norm(dim=-1, keepdim=True)
            
        return text_features.cpu().numpy().flatten()

# Global instance (Lazy loaded on first use in actual workers)
_clip_pipeline = None

def get_clip_pipeline():
    global _clip_pipeline
    if _clip_pipeline is None:
        _clip_pipeline = CLIPPipeline()
    return _clip_pipeline
