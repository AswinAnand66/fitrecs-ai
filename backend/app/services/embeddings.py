from typing import List, Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

from ..core.config import settings
from ..db import models

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self._model = None
        
    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info(f"Loading model {settings.MODEL_NAME}")
            self._model = SentenceTransformer(settings.MODEL_NAME)
        return self._model
        
    def compute_embedding(self, text: str) -> np.ndarray:
        """Compute embedding for a single text string"""
        return self.model.encode([text])[0]
        
    def compute_item_embedding(self, item: models.Item) -> np.ndarray:
        """Compute embedding for a fitness content item"""
        # Combine item fields into a single text
        text_parts = [
            item.title,
            item.description or "",
            " ".join(item.tags),
            str(item.difficulty),
            f"{item.duration} minutes",
            str(item.type)
        ]
        text = " ".join(text_parts)
        return self.compute_embedding(text)
        
    def compute_batch_embeddings(
        self, 
        items: List[models.Item],
        batch_size: int = 32
    ) -> Dict[int, np.ndarray]:
        """Compute embeddings for multiple items in batches"""
        embeddings = {}
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            # Prepare texts for the batch
            texts = []
            batch_ids = []
            for item in batch:
                text_parts = [
                    item.title,
                    item.description or "",
                    " ".join(item.tags),
                    str(item.difficulty),
                    f"{item.duration} minutes",
                    str(item.type)
                ]
                texts.append(" ".join(text_parts))
                batch_ids.append(item.id)
                
            # Compute embeddings for the batch
            batch_embeddings = self.model.encode(texts)
            
            # Store results
            for item_id, embedding in zip(batch_ids, batch_embeddings):
                embeddings[item_id] = embedding
                
        return embeddings

# Global instance
embedding_service = EmbeddingService()