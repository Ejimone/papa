from typing import List, Optional, Dict, Any, Tuple
import numpy as np
from app.ai.embeddings.text_embeddings import TextEmbeddingService
from app.ai.embeddings.image_embeddings import ImageEmbeddingService
import logging

logger = logging.getLogger(__name__)

class HybridEmbeddingService:
    def __init__(
        self,
        text_service: Optional[TextEmbeddingService] = None,
        image_service: Optional[ImageEmbeddingService] = None,
        fusion_method: str = "concatenation"  # concatenation, weighted_average, attention
    ):
        self.text_service = text_service or TextEmbeddingService()
        self.image_service = image_service or ImageEmbeddingService()
        self.fusion_method = fusion_method
        
        # Fusion weights for different modalities
        self.text_weight = 0.7
        self.image_weight = 0.3
        
        # Standard embedding dimensions
        self.text_dim = 768
        self.image_dim = 768
        
        # Hybrid embedding dimension based on fusion method
        if fusion_method == "concatenation":
            self.hybrid_dim = self.text_dim + self.image_dim
        else:
            self.hybrid_dim = max(self.text_dim, self.image_dim)

    async def create_question_embedding(
        self, 
        question_text: str, 
        question_images: Optional[List[bytes]] = None,
        question_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a hybrid embedding for a question that may contain text and images.
        """
        try:
            embeddings = {}
            
            # Generate text embedding
            full_text = self._prepare_text_for_embedding(question_text, question_metadata)
            text_embedding = await self.text_service.get_single_embedding(full_text)
            embeddings['text'] = text_embedding
            
            # Generate image embeddings if images exist
            image_embeddings = []
            if question_images:
                for image_data in question_images:
                    img_embedding = await self.image_service.generate_image_description_embedding(image_data)
                    image_embeddings.append(img_embedding)
            
            # Combine multiple image embeddings if present
            if image_embeddings:
                combined_image_embedding = self._combine_image_embeddings(image_embeddings)
                embeddings['image'] = combined_image_embedding
            else:
                embeddings['image'] = [0.0] * self.image_dim
            
            # Create hybrid embedding
            hybrid_embedding = self._fuse_embeddings(
                embeddings['text'], 
                embeddings['image']
            )
            
            return {
                "hybrid_embedding": hybrid_embedding,
                "text_embedding": embeddings['text'],
                "image_embedding": embeddings['image'],
                "fusion_method": self.fusion_method,
                "text_weight": self.text_weight,
                "image_weight": self.image_weight,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error creating question embedding: {e}")
            return {
                "hybrid_embedding": [0.0] * self.hybrid_dim,
                "text_embedding": [0.0] * self.text_dim,
                "image_embedding": [0.0] * self.image_dim,
                "fusion_method": self.fusion_method,
                "text_weight": 0.0,
                "image_weight": 0.0,
                "success": False,
                "error": str(e)
            }

    def _prepare_text_for_embedding(self, question_text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Prepare comprehensive text for embedding by combining question text with metadata.
        """
        components = [question_text]
        
        if metadata:
            # Add keywords if available
            if 'keywords' in metadata and metadata['keywords']:
                keywords_text = " ".join(metadata['keywords'])
                components.append(f"Keywords: {keywords_text}")
            
            # Add concepts if available
            if 'concepts' in metadata and metadata['concepts']:
                concepts_text = " ".join(metadata['concepts'])
                components.append(f"Concepts: {concepts_text}")
            
            # Add subject/topic information
            if 'subject' in metadata:
                components.append(f"Subject: {metadata['subject']}")
            
            if 'topic' in metadata:
                components.append(f"Topic: {metadata['topic']}")
            
            # Add OCR text from images if available
            if 'ocr_text' in metadata and metadata['ocr_text']:
                components.append(f"Image text: {metadata['ocr_text']}")
        
        return " ".join(components)

    def _combine_image_embeddings(self, image_embeddings: List[List[float]]) -> List[float]:
        """
        Combine multiple image embeddings into a single representative embedding.
        """
        if not image_embeddings:
            return [0.0] * self.image_dim
        
        if len(image_embeddings) == 1:
            return image_embeddings[0]
        
        # Average the embeddings
        combined = [0.0] * self.image_dim
        for embedding in image_embeddings:
            for i, value in enumerate(embedding):
                if i < self.image_dim:
                    combined[i] += value
        
        # Normalize by number of embeddings
        num_embeddings = len(image_embeddings)
        combined = [value / num_embeddings for value in combined]
        
        # Normalize the vector
        magnitude = sum(x * x for x in combined) ** 0.5
        if magnitude > 0:
            combined = [x / magnitude for x in combined]
        
        return combined

    def _fuse_embeddings(self, text_embedding: List[float], image_embedding: List[float]) -> List[float]:
        """
        Fuse text and image embeddings using the specified fusion method.
        """
        if self.fusion_method == "concatenation":
            return self._concatenation_fusion(text_embedding, image_embedding)
        elif self.fusion_method == "weighted_average":
            return self._weighted_average_fusion(text_embedding, image_embedding)
        elif self.fusion_method == "attention":
            return self._attention_fusion(text_embedding, image_embedding)
        else:
            logger.warning(f"Unknown fusion method {self.fusion_method}, defaulting to concatenation")
            return self._concatenation_fusion(text_embedding, image_embedding)

    def _concatenation_fusion(self, text_embedding: List[float], image_embedding: List[float]) -> List[float]:
        """Simple concatenation of text and image embeddings."""
        return text_embedding + image_embedding

    def _weighted_average_fusion(self, text_embedding: List[float], image_embedding: List[float]) -> List[float]:
        """Weighted average of text and image embeddings."""
        # Ensure both embeddings have the same dimension
        max_dim = max(len(text_embedding), len(image_embedding))
        
        # Pad shorter embedding with zeros
        text_padded = text_embedding + [0.0] * (max_dim - len(text_embedding))
        image_padded = image_embedding + [0.0] * (max_dim - len(image_embedding))
        
        # Weighted combination
        fused = [
            self.text_weight * text_val + self.image_weight * image_val
            for text_val, image_val in zip(text_padded, image_padded)
        ]
        
        # Normalize
        magnitude = sum(x * x for x in fused) ** 0.5
        if magnitude > 0:
            fused = [x / magnitude for x in fused]
        
        return fused

    def _attention_fusion(self, text_embedding: List[float], image_embedding: List[float]) -> List[float]:
        """
        Attention-based fusion that dynamically weights modalities.
        Simplified version - in production, this would use learned attention weights.
        """
        # Calculate attention weights based on embedding magnitudes
        text_magnitude = sum(x * x for x in text_embedding) ** 0.5
        image_magnitude = sum(x * x for x in image_embedding) ** 0.5
        
        total_magnitude = text_magnitude + image_magnitude
        if total_magnitude == 0:
            return [0.0] * max(len(text_embedding), len(image_embedding))
        
        # Dynamic weights based on content strength
        dynamic_text_weight = text_magnitude / total_magnitude
        dynamic_image_weight = image_magnitude / total_magnitude
        
        # Apply attention weights
        max_dim = max(len(text_embedding), len(image_embedding))
        text_padded = text_embedding + [0.0] * (max_dim - len(text_embedding))
        image_padded = image_embedding + [0.0] * (max_dim - len(image_embedding))
        
        fused = [
            dynamic_text_weight * text_val + dynamic_image_weight * image_val
            for text_val, image_val in zip(text_padded, image_padded)
        ]
        
        # Normalize
        magnitude = sum(x * x for x in fused) ** 0.5
        if magnitude > 0:
            fused = [x / magnitude for x in fused]
        
        return fused

    def calculate_hybrid_similarity(
        self, 
        embedding1: List[float], 
        embedding2: List[float],
        similarity_type: str = "cosine"
    ) -> float:
        """
        Calculate similarity between two hybrid embeddings.
        """
        try:
            if len(embedding1) != len(embedding2):
                logger.warning("Embedding dimensions don't match for similarity calculation")
                return 0.0
            
            if similarity_type == "cosine":
                return self._cosine_similarity(embedding1, embedding2)
            elif similarity_type == "euclidean":
                return self._euclidean_similarity(embedding1, embedding2)
            elif similarity_type == "dot_product":
                return self._dot_product_similarity(embedding1, embedding2)
            else:
                logger.warning(f"Unknown similarity type {similarity_type}, defaulting to cosine")
                return self._cosine_similarity(embedding1, embedding2)
                
        except Exception as e:
            logger.error(f"Error calculating hybrid similarity: {e}")
            return 0.0

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0.0 or magnitude2 == 0.0:
            return 0.0
        
        similarity = dot_product / (magnitude1 * magnitude2)
        return max(0.0, min(1.0, similarity))

    def _euclidean_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate similarity based on Euclidean distance (converted to similarity score)."""
        distance = sum((a - b) ** 2 for a, b in zip(vec1, vec2)) ** 0.5
        # Convert distance to similarity (inverse relationship)
        # Normalize by maximum possible distance in unit hypersphere
        max_distance = (2 * len(vec1)) ** 0.5
        similarity = 1.0 - (distance / max_distance)
        return max(0.0, min(1.0, similarity))

    def _dot_product_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate normalized dot product similarity."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        # Normalize to [0, 1] range assuming unit vectors
        return max(0.0, min(1.0, (dot_product + 1.0) / 2.0))

    async def find_similar_questions(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[Tuple[int, List[float]]],
        top_k: int = 10,
        threshold: float = 0.5
    ) -> List[Tuple[int, float]]:
        """
        Find similar questions based on hybrid embeddings.
        
        Args:
            query_embedding: The query question's hybrid embedding
            candidate_embeddings: List of (question_id, embedding) tuples
            top_k: Number of top similar questions to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of (question_id, similarity_score) tuples, sorted by similarity
        """
        try:
            similarities = []
            
            for question_id, candidate_embedding in candidate_embeddings:
                similarity = self.calculate_hybrid_similarity(query_embedding, candidate_embedding)
                
                if similarity >= threshold:
                    similarities.append((question_id, similarity))
            
            # Sort by similarity (descending) and return top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding similar questions: {e}")
            return []

    def get_embedding_info(self) -> Dict[str, Any]:
        """Get information about the hybrid embedding configuration."""
        return {
            "fusion_method": self.fusion_method,
            "text_weight": self.text_weight,
            "image_weight": self.image_weight,
            "text_dim": self.text_dim,
            "image_dim": self.image_dim,
            "hybrid_dim": self.hybrid_dim,
            "supported_fusion_methods": ["concatenation", "weighted_average", "attention"],
            "supported_similarity_types": ["cosine", "euclidean", "dot_product"]
        }

# Singleton instance
hybrid_embedding_service = HybridEmbeddingService()
