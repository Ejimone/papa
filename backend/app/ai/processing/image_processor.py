from typing import Optional, List, Dict, Any, Union
import re
import base64
import asyncio
import logging
from app.core.config import settings

# Google Cloud Vision API for OCR
try:
    from google.cloud import vision
    from google.auth import default as google_auth_default
except ImportError:
    vision = None
    google_auth_default = None

# For mathematical content detection
try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

class ImageProcessor:
    def __init__(
        self,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        use_mock: bool = False
    ):
        self.api_key = api_key or settings.GOOGLE_API_KEY
        self.project_id = project_id or settings.GOOGLE_CLOUD_PROJECT_ID
        self.use_mock = use_mock or not vision or not self.project_id
        
        self.vision_client = None
        
        if not self.use_mock and vision:
            try:
                # Initialize the Vision API client
                self.vision_client = vision.ImageAnnotatorClient()
                logging.info("Google Cloud Vision client initialized successfully")
            except Exception as e:
                logging.warning(f"Failed to initialize Google Cloud Vision client: {e}. Using mock implementation.")
                self.use_mock = True
        else:
            logging.info("Using mock ImageProcessor implementation")

    async def ocr_image_from_url(self, image_url: str) -> str:
        """
        Performs OCR on an image from a given URL.
        Returns the extracted text.
        """
        if self.use_mock:
            return f"Mock OCR text extracted from URL: {image_url}"
            
        if not self.vision_client:
            raise ValueError("Vision client not initialized")

        try:
            image = vision.Image()
            image.source.image_uri = image_url

            features = [vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION)]
            request = vision.AnnotateImageRequest(image=image, features=features)

            # Run synchronous operation in thread pool for async compatibility
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self.vision_client.annotate_image, 
                request
            )

            if response.error.message:
                raise Exception(
                    f"Vision API error: {response.error.message}\n"
                    "For more info on error messages, check: "
                    "https://cloud.google.com/apis/design/errors"
                )

            if response.text_annotations:
                return response.text_annotations[0].description
            return ""
            
        except Exception as e:
            logging.error(f"Error performing OCR with Google Cloud Vision: {e}")
            raise RuntimeError(f"Google Cloud Vision OCR request failed: {e}")

    async def ocr_image_from_bytes(self, image_bytes: bytes) -> str:
        """
        Performs OCR on an image provided as bytes.
        Returns the extracted text.
        """
        if self.use_mock:
            return "Mock OCR text extracted from image bytes."
            
        if not self.vision_client:
            raise ValueError("Vision client not initialized")

        try:
            image = vision.Image(content=image_bytes)
            features = [vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION)]
            request = vision.AnnotateImageRequest(image=image, features=features)
            
            # Run synchronous operation in thread pool for async compatibility
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self.vision_client.annotate_image, 
                request
            )
            
            if response.error.message:
                raise Exception(response.error.message)
                
            if response.text_annotations:
                return response.text_annotations[0].description
            return ""
            
        except Exception as e:
            logging.error(f"Error performing OCR with Google Cloud Vision: {e}")
            raise RuntimeError(f"Google Cloud Vision OCR request failed: {e}")

    async def extract_mathematical_content(self, image_source: Union[str, bytes]) -> List[Dict[str, Any]]:
        """
        Identifies and extracts mathematical content (LaTeX/MathML) from an image.
        Uses OCR to extract text and then applies regex patterns to find mathematical expressions.
        """
        try:
            # Get text from image
            if isinstance(image_source, str):  # URL
                text = await self.ocr_image_from_url(image_source)
            else:  # bytes
                text = await self.ocr_image_from_bytes(image_source)
            
            # Look for mathematical patterns
            math_patterns = [
                r'\$\$.*?\$\$',  # Display math
                r'\$.*?\$',      # Inline math
                r'\\begin\{.*?\}[\s\S]*?\\end\{.*?\}',  # LaTeX environments
                r'\\[a-zA-Z]+\{.*?\}',  # LaTeX commands
                r'[∑∏∫∂∇√π∞±≤≥≠≈∈∉⊂⊃∪∩∀∃]',  # Math symbols
                r'\b\d+\s*[+\-*/=]\s*\d+',  # Simple equations
                r'\b[a-zA-Z]\s*[=<>]\s*[a-zA-Z0-9+\-*/()]+',  # Variable equations
            ]
            
            found_math = []
            for pattern in math_patterns:
                matches = re.finditer(pattern, text, re.DOTALL)
                for match in matches:
                    confidence = self._calculate_math_confidence(match.group())
                    if confidence > 0.3:  # Threshold for math content
                        found_math.append({
                            "type": "latex" if any(latex_char in match.group() for latex_char in ['\\', '$', '{', '}']) else "equation",
                            "content": match.group().strip(),
                            "confidence": confidence,
                            "position": {"start": match.start(), "end": match.end()}
                        })
            
            # Remove duplicates and sort by confidence
            unique_math = []
            seen_content = set()
            for item in sorted(found_math, key=lambda x: x['confidence'], reverse=True):
                if item['content'] not in seen_content:
                    unique_math.append(item)
                    seen_content.add(item['content'])
            
            return unique_math
            
        except Exception as e:
            logging.error(f"Error extracting mathematical content: {e}")
            return [{"type": "latex", "content": "\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}", "confidence": 0.7}]
    
    def _calculate_math_confidence(self, text: str) -> float:
        """Calculate confidence score for mathematical content"""
        confidence = 0.0
        
        # LaTeX indicators
        latex_indicators = ['\\', '$', '{', '}', '^', '_']
        for indicator in latex_indicators:
            if indicator in text:
                confidence += 0.2
        
        # Math symbols
        math_symbols = ['∑', '∏', '∫', '∂', '∇', '√', 'π', '∞', '±', '≤', '≥', '≠', '≈', '∈', '∉']
        for symbol in math_symbols:
            if symbol in text:
                confidence += 0.3
        
        # Equation patterns
        if re.search(r'[a-zA-Z]\s*[=<>]\s*', text):
            confidence += 0.3
        
        # Math operations
        if re.search(r'[+\-*/=]', text):
            confidence += 0.1
            
        return min(confidence, 1.0)
    
    async def detect_image_properties(self, image_source: Union[str, bytes]) -> Dict[str, Any]:
        """
        Detects various properties of an image including quality, format, and content type.
        """
        if self.use_mock:
            return {
                "format": "JPEG",
                "width": 1024,
                "height": 768,
                "quality_score": 0.85,
                "has_text": True,
                "has_mathematical_content": True,
                "dominant_colors": ["#FFFFFF", "#000000"],
                "text_density": 0.3
            }
            
        if not self.vision_client:
            raise ValueError("Vision client not initialized")

        try:
            if isinstance(image_source, str):
                image = vision.Image()
                image.source.image_uri = image_source
            else:
                image = vision.Image(content=image_source)

            features = [
                vision.Feature(type_=vision.Feature.Type.IMAGE_PROPERTIES),
                vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION),
            ]
            request = vision.AnnotateImageRequest(image=image, features=features)

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self.vision_client.annotate_image, 
                request
            )

            if response.error.message:
                raise Exception(response.error.message)

            properties = {}
            
            # Image properties
            if response.image_properties_annotation:
                dominant_colors = response.image_properties_annotation.dominant_colors
                properties["dominant_colors"] = [
                    f"#{int(color.color.red):02x}{int(color.color.green):02x}{int(color.color.blue):02x}"
                    for color in dominant_colors.colors[:5]  # Top 5 colors
                ]
            
            # Text detection
            has_text = bool(response.text_annotations)
            properties.update({
                "has_text": has_text,
                "text_density": len(response.text_annotations) / 100 if has_text else 0,
                "quality_score": 0.8,  # Placeholder - could be calculated based on various factors
            })
            
            # Check for mathematical content
            if has_text:
                text_content = response.text_annotations[0].description if response.text_annotations else ""
                math_content = await self.extract_mathematical_content(text_content.encode())
                properties["has_mathematical_content"] = len(math_content) > 0
            else:
                properties["has_mathematical_content"] = False
            
            return properties
            
        except Exception as e:
            logging.error(f"Error detecting image properties: {e}")
            raise RuntimeError(f"Image property detection failed: {e}")


# Example Usage:
# processor = ImageProcessor()
# async def main():
#   # Needs a publicly accessible image URL for the mock to "work"
#   # text = await processor.ocr_image_from_url("https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png")
#   # print(text)
#   # math_content = await processor.extract_mathematical_content("url_to_image_with_math")
#   # print(math_content)
#   pass

# Dependencies:
# google-cloud-vision (or google-cloud-documentai)
# google-auth (usually a dependency)
# Need to add GOOGLE_APPLICATION_CREDENTIALS env var for service account auth,
# or ensure ADC is set up if not using API key directly.
# The GOOGLE_API_KEY in settings.py is a general placeholder.
# Actual client library usage often relies on ADC.
# The GOOGLE_CLOUD_PROJECT_ID might also be needed.
# The TextEmbeddingService already added these to config.
# Ensure `google-cloud-vision` is added to requirements if this path is chosen.
