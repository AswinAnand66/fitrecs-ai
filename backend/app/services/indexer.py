from typing import Dict, List, Optional
import faiss
import numpy as np
import json
import os
import logging
from datetime import datetime

from ..core.config import settings
from ..db import models
from .embeddings import embedding_service

logger = logging.getLogger(__name__)

class IndexerService:
    def __init__(self):
        self.index: Optional[faiss.Index] = None
        self.item_mapping: Dict[int, int] = {}  # item_id -> faiss_id
        self.reverse_mapping: Dict[int, int] = {}  # faiss_id -> item_id
        
    def initialize_index(self, dimension: int = 384) -> None:
        """Initialize a new FAISS index"""
        self.index = faiss.IndexFlatL2(dimension)
        self.item_mapping = {}
        self.reverse_mapping = {}
        
    def load_index(self) -> bool:
        """Load saved index and mappings from disk"""
        try:
            if os.path.exists(settings.FAISS_INDEX_PATH):
                self.index = faiss.read_index(settings.FAISS_INDEX_PATH)
                
                if os.path.exists(settings.ITEM_MAPPING_PATH):
                    with open(settings.ITEM_MAPPING_PATH, 'r') as f:
                        mapping_data = json.load(f)
                        self.item_mapping = {
                            int(k): int(v) 
                            for k, v in mapping_data['item_mapping'].items()
                        }
                        self.reverse_mapping = {
                            int(v): int(k) 
                            for k, v in self.item_mapping.items()
                        }
                return True
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            return False
            
        return False
        
    def save_index(self) -> None:
        """Save index and mappings to disk"""
        if self.index is None:
            return
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, settings.FAISS_INDEX_PATH)
        
        # Save mapping
        with open(settings.ITEM_MAPPING_PATH, 'w') as f:
            json.dump({
                'item_mapping': self.item_mapping,
                'updated_at': datetime.utcnow().isoformat()
            }, f)
            
    def add_items(self, items: List[models.Item]) -> None:
        """Add new items to the index"""
        if not items:
            return
            
        if self.index is None:
            # Initialize with dimension from first embedding
            test_embedding = embedding_service.compute_item_embedding(items[0])
            self.initialize_index(dimension=len(test_embedding))
            
        # Compute embeddings in batch
        embeddings = embedding_service.compute_batch_embeddings(items)
        
        # Add to FAISS index
        for item in items:
            if item.id not in self.item_mapping and item.id in embeddings:
                embedding = embeddings[item.id]
                faiss_id = self.index.ntotal
                self.index.add(embedding.reshape(1, -1))
                
                # Update mappings
                self.item_mapping[item.id] = faiss_id
                self.reverse_mapping[faiss_id] = item.id
                
    def rebuild_index(self, items: List[models.Item]) -> None:
        """Rebuild the entire index from scratch"""
        # Initialize new index
        test_embedding = embedding_service.compute_item_embedding(items[0])
        self.initialize_index(dimension=len(test_embedding))
        
        # Add all items
        self.add_items(items)
        
        # Save to disk
        self.save_index()
        
    def search(
        self, 
        query_embedding: np.ndarray,
        k: int = 10
    ) -> List[tuple[int, float]]:
        """Search for similar items given a query embedding"""
        if self.index is None or self.index.ntotal == 0:
            return []
            
        # Search in FAISS index
        D, I = self.index.search(query_embedding.reshape(1, -1), k)
        
        # Convert to item IDs with scores
        results = []
        for dist, faiss_id in zip(D[0], I[0]):
            if faiss_id in self.reverse_mapping:
                item_id = self.reverse_mapping[faiss_id]
                similarity = 1.0 / (1.0 + dist)  # Convert distance to similarity
                results.append((item_id, similarity))
                
        return results
        
    def find_similar(
        self, 
        item_id: int,
        k: int = 10
    ) -> List[tuple[int, float]]:
        """Find similar items to a given item"""
        if self.index is None or item_id not in self.item_mapping:
            return []
            
        # Get query item's vector
        faiss_id = self.item_mapping[item_id]
        query_vector = self.index.reconstruct(faiss_id)
        
        # Search
        D, I = self.index.search(query_vector.reshape(1, -1), k + 1)
        
        # Convert results (skip first result as it's the query item)
        results = []
        for dist, faiss_id in zip(D[0][1:], I[0][1:]):
            if faiss_id in self.reverse_mapping:
                similar_id = self.reverse_mapping[faiss_id]
                similarity = 1.0 / (1.0 + dist)
                results.append((similar_id, similarity))
                
        return results

# Global instance
indexer_service = IndexerService()