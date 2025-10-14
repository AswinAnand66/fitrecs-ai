import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import faiss
import json
import os
from implicit.als import AlternatingLeastSquares
from scipy.sparse import csr_matrix, lil_matrix
import logging
from datetime import datetime

from ..core.config import settings
from ..db import models
from ..schemas import item as item_schemas

logger = logging.getLogger(__name__)

class RecommenderService:
    def __init__(self):
        self.model = None
        self.faiss_index = None
        self.item_mapping = {}  # item_id -> faiss_id
        self.reverse_mapping = {}  # faiss_id -> item_id
        self.als_model = None
        self.user_factors = None
        self.item_factors = None
        
    def get_model(self) -> SentenceTransformer:
        if self.model is None:
            logger.info("Loading sentence transformer model...")
            self.model = SentenceTransformer(settings.MODEL_NAME)
        return self.model
        
    def create_faiss_index(self, dimension: int = 384) -> None:
        """Initialize a new FAISS index"""
        self.faiss_index = faiss.IndexFlatL2(dimension)
        
    def load_faiss_index(self) -> bool:
        """Load FAISS index from disk if it exists"""
        try:
            if os.path.exists(settings.FAISS_INDEX_PATH):
                self.faiss_index = faiss.read_index(settings.FAISS_INDEX_PATH)
                with open(settings.ITEM_MAPPING_PATH, 'r') as f:
                    mapping_data = json.load(f)
                    self.item_mapping = {int(k): int(v) for k, v in mapping_data['item_mapping'].items()}
                    self.reverse_mapping = {int(v): int(k) for k, v in self.item_mapping.items()}
                return True
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
        return False
        
    def save_faiss_index(self) -> None:
        """Save FAISS index and mapping to disk"""
        if self.faiss_index and self.item_mapping:
            os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True)
            faiss.write_index(self.faiss_index, settings.FAISS_INDEX_PATH)
            with open(settings.ITEM_MAPPING_PATH, 'w') as f:
                json.dump({
                    'item_mapping': self.item_mapping,
                    'updated_at': datetime.utcnow().isoformat()
                }, f)

    def compute_item_embedding(self, item: models.Item) -> np.ndarray:
        """Compute embedding for a single item"""
        text = f"{item.title} {item.description or ''} {' '.join(item.tags)}"
        return self.get_model().encode([text])[0]

    def add_item_to_index(self, item: models.Item, embedding: np.ndarray) -> int:
        """Add a single item to the FAISS index"""
        if self.faiss_index is None:
            self.create_faiss_index()
        
        faiss_id = self.faiss_index.ntotal
        self.faiss_index.add(embedding.reshape(1, -1))
        self.item_mapping[item.id] = faiss_id
        self.reverse_mapping[faiss_id] = item.id
        return faiss_id

    def find_similar_items(
        self, 
        item_id: int, 
        k: int = 10
    ) -> List[Tuple[int, float]]:
        """Find k most similar items to the given item_id"""
        if item_id not in self.item_mapping:
            return []
            
        faiss_id = self.item_mapping[item_id]
        item_vector = self.faiss_index.reconstruct(faiss_id)
        
        D, I = self.faiss_index.search(item_vector.reshape(1, -1), k + 1)
        
        # Convert faiss IDs back to item IDs and include similarity scores
        similar_items = []
        for idx, (dist, faiss_idx) in enumerate(zip(D[0], I[0])):
            if idx == 0:  # Skip the query item itself
                continue
            if faiss_idx in self.reverse_mapping:
                item_id = self.reverse_mapping[faiss_idx]
                similarity = 1.0 / (1.0 + dist)  # Convert distance to similarity score
                similar_items.append((item_id, similarity))
                
        return similar_items

    def build_interaction_matrix(
        self, 
        interactions: List[models.Interaction]
    ) -> Tuple[csr_matrix, Dict[int, int], Dict[int, int]]:
        """Build user-item interaction matrix for collaborative filtering"""
        # Create mappings for users and items
        unique_users = sorted(set(inter.user_id for inter in interactions))
        unique_items = sorted(set(inter.item_id for inter in interactions))
        
        user_to_idx = {uid: idx for idx, uid in enumerate(unique_users)}
        item_to_idx = {iid: idx for idx, iid in enumerate(unique_items)}
        
        # Create sparse matrix
        matrix = lil_matrix((len(unique_users), len(unique_items)), dtype=np.float32)
        
        # Fill matrix with interaction weights
        for inter in interactions:
            user_idx = user_to_idx[inter.user_id]
            item_idx = item_to_idx[inter.item_id]
            # Weight by interaction type
            weight = {
                models.InteractionType.VIEW: 1.0,
                models.InteractionType.LIKE: 3.0,
                models.InteractionType.COMPLETE: 5.0
            }[inter.interaction_type]
            matrix[user_idx, item_idx] += weight
            
        return matrix.tocsr(), user_to_idx, item_to_idx

    def fit_collaborative(
        self, 
        interactions: List[models.Interaction],
        factors: int = 50,
        iterations: int = 15
    ) -> None:
        """Train ALS model on interaction data"""
        interaction_matrix, user_mapping, item_mapping = self.build_interaction_matrix(interactions)
        
        self.als_model = AlternatingLeastSquares(
            factors=factors,
            iterations=iterations,
            calculate_training_loss=True
        )
        
        self.als_model.fit(interaction_matrix)
        
        # Store learned factors and mappings
        self.user_factors = self.als_model.user_factors
        self.item_factors = self.als_model.item_factors
        self.user_mapping = user_mapping
        self.item_mapping_als = item_mapping
        self.reverse_item_mapping_als = {v: k for k, v in item_mapping.items()}
        
    def get_user_recommendations(
        self, 
        user_id: int,
        n_items: int = 10,
        filter_viewed: bool = True,
        viewed_items: List[int] = None
    ) -> List[Tuple[int, float]]:
        """Get collaborative filtering recommendations for a user"""
        if user_id not in self.user_mapping:
            return []
            
        user_idx = self.user_mapping[user_id]
        scores = self.als_model.recommend(
            user_idx,
            interaction_matrix[user_idx],
            N=n_items + len(viewed_items) if viewed_items else n_items,
            filter_already_liked_items=filter_viewed
        )
        
        # Convert back to item IDs and scores
        recommendations = []
        for item_idx, score in zip(scores[0], scores[1]):
            item_id = self.reverse_item_mapping_als[item_idx]
            if not filter_viewed or item_id not in (viewed_items or []):
                recommendations.append((item_id, float(score)))
                if len(recommendations) >= n_items:
                    break
                    
        return recommendations

    def get_hybrid_recommendations(
        self, 
        user_id: int,
        item_id: Optional[int] = None,
        n_items: int = 10,
        alpha: float = 0.5,
        viewed_items: List[int] = None
    ) -> List[Tuple[int, float]]:
        """Get hybrid recommendations combining collaborative and content-based"""
        cf_recs = self.get_user_recommendations(
            user_id, 
            n_items=n_items*2,  # Get more for blending
            viewed_items=viewed_items
        )
        
        if item_id:
            cb_recs = self.find_similar_items(
                item_id,
                k=n_items*2
            )
        else:
            cb_recs = []
            
        # Normalize scores within each method
        def normalize_scores(recs):
            if not recs:
                return {}
            scores = [score for _, score in recs]
            min_score = min(scores)
            max_score = max(scores)
            return {
                item_id: (score - min_score) / (max_score - min_score)
                for item_id, score in recs
            } if max_score > min_score else {
                item_id: 1.0 
                for item_id, _ in recs
            }
            
        cf_scores = normalize_scores(cf_recs)
        cb_scores = normalize_scores(cb_recs)
        
        # Blend scores
        all_items = set(cf_scores.keys()) | set(cb_scores.keys())
        if viewed_items:
            all_items = all_items - set(viewed_items)
            
        blended_scores = []
        for item_id in all_items:
            cf_score = cf_scores.get(item_id, 0.0)
            cb_score = cb_scores.get(item_id, 0.0)
            
            # Weighted blend
            final_score = (alpha * cf_score) + ((1 - alpha) * cb_score)
            blended_scores.append((item_id, final_score))
            
        # Sort and return top N
        blended_scores.sort(key=lambda x: x[1], reverse=True)
        return blended_scores[:n_items]

# Global instance
recommender = RecommenderService()