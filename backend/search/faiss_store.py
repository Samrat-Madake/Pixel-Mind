import faiss
import numpy as np
import os
from backend.utils.config import FAISS_CLIP_PATH, FAISS_FACE_PATH, CLIP_DIM, FACE_DIM, FAISS_NLIST

class FaissStore:
    def __init__(self, path, dimension, nlist=FAISS_NLIST):
        self.path = path
        self.dimension = dimension
        self.nlist = nlist
        self.index = self._load_or_create()

    def _load_or_create(self):
        if os.path.exists(self.path):
            return faiss.read_index(str(self.path))
        else:
            # Using FlatL2 initially as per strategy for small datasets
            # Will switch to IVFFlat when dataset grows as per plan
            index = faiss.IndexFlatL2(self.dimension)
            return index

    def add(self, vector):
        if vector.ndim == 1:
            vector = vector.reshape(1, -1)
        self.index.add(vector.astype('float32'))
        self.save()
        return self.index.ntotal - 1

    def search(self, vector, k=50):
        if vector.ndim == 1:
            vector = vector.reshape(1, -1)
        distances, indices = self.index.search(vector.astype('float32'), k)
        return indices[0], distances[0]

    def reconstruct(self, index_id):
        return self.index.reconstruct(int(index_id))

    def save(self):
        faiss.write_index(self.index, str(self.path))

# Global instances for the app
faiss_clip = FaissStore(FAISS_CLIP_PATH, CLIP_DIM)
faiss_face = FaissStore(FAISS_FACE_PATH, FACE_DIM)
