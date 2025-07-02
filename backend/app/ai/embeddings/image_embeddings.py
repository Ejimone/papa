from typing import List, Optional, Dict, Any
import base64
import io
from PIL import Image
import google.generativeai as genai
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ImageEmbeddingService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("Gemini API key is not configured for image embeddings.")
        
        genai.configure(api_key=self.api_key)
        
        # Model for vision and embeddings
        self.vision_model_name = "gemini-pro-vision"
        self.embedding_model_name = "text-embedding-004"  # Will be used for text extracted from images
        
        self._vision_model = None

    @property
    def vision_model(self):
        if self._vision_model is None:
            self._vision_model = genai.GenerativeModel(self.vision_model_name)
        return self._vision_model

    def _prepare_image(self, image_data: bytes) -> Image.Image:
        """Prepare image data for processing."""
        try:
            image = Image.open(io.BytesIO(image_data))
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return image
        except Exception as e:
            logger.error(f"Error preparing image: {e}")
            raise ValueError(f"Invalid image data: {e}")

    async def extract_text_from_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Extract text from image using OCR capabilities.
        Returns extracted text and confidence information.
        """
        try:
            image = self._prepare_image(image_data)
            
            prompt = """Extract all text from this image. 
            If this is a mathematical expression, diagram, or chart, also describe the visual elements.
            Format your response as follows:
            TEXT: [extracted text]
            DESCRIPTION: [description of visual elements]
            CONFIDENCE: [your confidence level from 0.0 to 1.0]"""
            
            response = self.vision_model.generate_content([prompt, image])
            
            # Parse the response
            response_text = response.text
            lines = response_text.split('\n')
            
            extracted_text = ""
            description = ""
            confidence = 0.8  # Default confidence
            
            for line in lines:
                line = line.strip()
                if line.startswith("TEXT:"):
                    extracted_text = line[5:].strip()
                elif line.startswith("DESCRIPTION:"):
                    description = line[12:].strip()
                elif line.startswith("CONFIDENCE:"):
                    try:
                        confidence = float(line[11:].strip())
                    except ValueError:
                        confidence = 0.8
            
            return {
                "text": extracted_text,
                "description": description,
                "confidence": confidence,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return {
                "text": "",
                "description": "",
                "confidence": 0.0,
                "success": False,
                "error": str(e)
            }

    async def analyze_image_content(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze image content to understand what type of academic content it contains.
        """
        try:
            image = self._prepare_image(image_data)
            
            prompt = """Analyze this academic image and provide:
            1. CONTENT_TYPE: [diagram, chart, graph, equation, text, table, etc.]
            2. SUBJECT_AREA: [mathematics, physics, chemistry, biology, etc.]
            3. COMPLEXITY: [basic, intermediate, advanced]
            4. VISUAL_ELEMENTS: [list key visual elements]
            5. EDUCATIONAL_VALUE: [description of what this teaches]"""
            
            response = self.vision_model.generate_content([prompt, image])
            
            # Parse the structured response
            response_text = response.text
            analysis = {}
            
            for line in response_text.split('\n'):
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    analysis[key] = value.strip()
            
            return {
                "analysis": analysis,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image content: {e}")
            return {
                "analysis": {},
                "success": False,
                "error": str(e)
            }

    async def generate_image_description_embedding(self, image_data: bytes) -> List[float]:
        """
        Generate semantic embedding from image description.
        First analyzes the image, then creates embedding from the description.
        """
        try:
            # First, get a detailed description of the image
            image = self._prepare_image(image_data)
            
            prompt = """Provide a detailed semantic description of this academic image that would be useful for similarity search. Include:
            - What type of content it shows
            - Key concepts or topics
            - Visual elements and their relationships
            - Educational context
            Keep the description comprehensive but concise."""
            
            response = self.vision_model.generate_content([prompt, image])
            description = response.text
            
            # Generate embedding from the description using text embedding service
            # Note: In a real implementation, you'd use the TextEmbeddingService here
            # For now, we'll create a placeholder that represents the semantic meaning
            
            # Convert description to a simple vector representation
            # This is a simplified approach - in production, use proper text embeddings
            words = description.lower().split()
            
            # Create a basic embedding (in production, use TextEmbeddingService)
            embedding_dim = 768
            embedding = [0.0] * embedding_dim
            
            # Simple hash-based embedding for demonstration
            for i, word in enumerate(words[:embedding_dim]):
                embedding[i % embedding_dim] += hash(word) % 1000 / 1000.0
            
            # Normalize
            magnitude = sum(x*x for x in embedding) ** 0.5
            if magnitude > 0:
                embedding = [x / magnitude for x in embedding]
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating image description embedding: {e}")
            # Return zero vector on error
            return [0.0] * 768

    async def process_question_image(self, image_data: bytes, image_url: str) -> Dict[str, Any]:
        """
        Complete processing of a question image including text extraction,
        content analysis, and embedding generation.
        """
        try:
            # Extract text
            text_result = await self.extract_text_from_image(image_data)
            
            # Analyze content
            analysis_result = await self.analyze_image_content(image_data)
            
            # Generate embedding
            embedding = await self.generate_image_description_embedding(image_data)
            
            # Get image properties
            image = self._prepare_image(image_data)
            width, height = image.size
            
            return {
                "ocr_text": text_result.get("text", ""),
                "ocr_confidence": text_result.get("confidence", 0.0),
                "description": text_result.get("description", ""),
                "content_analysis": analysis_result.get("analysis", {}),
                "embedding": embedding,
                "width": width,
                "height": height,
                "file_size": len(image_data),
                "success": True,
                "processing_error": None
            }
            
        except Exception as e:
            logger.error(f"Error processing question image: {e}")
            return {
                "ocr_text": "",
                "ocr_confidence": 0.0,
                "description": "",
                "content_analysis": {},
                "embedding": [0.0] * 768,
                "width": 0,
                "height": 0,
                "file_size": len(image_data) if image_data else 0,
                "success": False,
                "processing_error": str(e)
            }

    def calculate_image_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two image embeddings."""
        try:
            if len(embedding1) != len(embedding2):
                return 0.0
            
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            magnitude1 = sum(a * a for a in embedding1) ** 0.5
            magnitude2 = sum(b * b for b in embedding2) ** 0.5
            
            if magnitude1 == 0.0 or magnitude2 == 0.0:
                return 0.0
            
            similarity = dot_product / (magnitude1 * magnitude2)
            return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]
            
        except Exception as e:
            logger.error(f"Error calculating image similarity: {e}")
            return 0.0

# Singleton instance
image_embedding_service = ImageEmbeddingService()
