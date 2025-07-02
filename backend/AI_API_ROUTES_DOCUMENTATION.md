# AI-Powered Past Questions App - API Routes Documentation

## Overview

This document provides comprehensive documentation for all AI-related API endpoints in the AI-Powered Past Questions App. The API provides advanced AI functionality including embeddings, question processing, similarity search, personalization, and learning analytics.

## Base URL
```
/api/v1/ai/
```

## Authentication
All endpoints require JWT authentication unless specified as demo endpoints.

---

## 🧠 Core AI Endpoints

### 1. Text Analysis

#### `POST /analyze-question`
Analyze question text to determine type, difficulty, and extract metadata.

**Request Body:**
```json
{
  "text": "What is the derivative of f(x) = x^2 + 3x?",
  "subject": "mathematics",
  "expected_difficulty": 2
}
```

**Response:**
```json
{
  "question_type": "short_answer",
  "difficulty_score": 0.75,
  "keywords": ["derivative", "function", "calculus"],
  "mathematical_expressions": ["f(x) = x^2 + 3x"],
  "estimated_time": 120,
  "confidence": 0.85
}
```

#### `POST /analyze-image`
Extract text and analyze content from uploaded question images.

**Request:** Multipart form with image file

**Response:**
```json
{
  "extracted_text": "What is the integral of x^2 dx?",
  "confidence": 0.92,
  "language": "en",
  "has_mathematical_content": true,
  "mathematical_expressions": ["x^2", "dx"],
  "processing_time": 1.2
}
```

---

## 🔗 Embedding Endpoints

### 2. Text Embeddings

#### `POST /embeddings/text`
Generate text embeddings for semantic search and similarity.

**Request Body:**
```json
{
  "text": "What is the derivative of x^2?",
  "task_type": "RETRIEVAL_DOCUMENT"
}
```

**Response:**
```json
{
  "embedding": [0.1, -0.2, 0.3, ...],
  "dimension": 768,
  "task_type": "RETRIEVAL_DOCUMENT",
  "processing_time": 0.5
}
```

### 3. Image Embeddings

#### `POST /embeddings/image`
Generate embeddings for images with OCR and content analysis.

**Request:** Multipart form with image file OR form data with base64 encoded image

**Response:**
```json
{
  "embedding": [0.1, -0.2, 0.3, ...],
  "dimension": 768,
  "ocr_text": "What is 2+2?",
  "ocr_confidence": 0.95,
  "description": "Mathematical equation with simple arithmetic",
  "content_analysis": {
    "content_type": "equation",
    "subject_area": "mathematics",
    "complexity": "basic"
  },
  "processing_time": 2.1
}
```

### 4. Hybrid Embeddings

#### `POST /embeddings/hybrid`
Generate combined text and image embeddings for multimodal questions.

**Request Body:**
```json
{
  "question_text": "Analyze the diagram and solve for x",
  "image_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "metadata": {
    "subject": "geometry",
    "keywords": ["diagram", "solve"]
  },
  "fusion_method": "concatenation"
}
```

**Response:**
```json
{
  "hybrid_embedding": [0.1, -0.2, 0.3, ...],
  "text_embedding": [0.1, -0.2, ...],
  "image_embedding": [0.3, 0.4, ...],
  "fusion_method": "concatenation",
  "text_weight": 0.7,
  "image_weight": 0.3,
  "dimension": 1536,
  "processing_time": 3.2
}
```

---

## 🔧 Question Processing Endpoints

### 5. Single Question Processing

#### `POST /process-question`
Comprehensive AI processing of a single question including metadata extraction, embeddings, explanations, and similarity search.

**Request Body:**
```json
{
  "question_id": 123,
  "question_text": "What is the derivative of f(x) = x^2?",
  "answer": "f'(x) = 2x",
  "subject": "calculus",
  "topic": "derivatives",
  "difficulty_level": "intermediate",
  "question_type": "short_answer",
  "image_urls": [],
  "generate_explanations": true,
  "generate_hints": true,
  "find_similar": true
}
```

**Response:**
```json
{
  "question_id": 123,
  "processing_status": "completed",
  "metadata_extracted": {
    "keywords": ["derivative", "function"],
    "concepts": ["calculus", "differentiation"],
    "clarity_score": 0.8,
    "completeness_score": 0.7
  },
  "embeddings_generated": true,
  "vector_id": "question_123",
  "explanations": ["To find the derivative, apply the power rule..."],
  "hints": ["Remember the power rule for derivatives"],
  "similar_questions": [
    {
      "question_id": "similar_1",
      "similarity_score": 0.9,
      "question_text": "Find the derivative of g(x) = x^3"
    }
  ],
  "processing_time": 5.2,
  "errors": []
}
```

### 6. Batch Processing

#### `POST /process-questions-batch`
Start batch processing of multiple questions in the background.

**Request Body:**
```json
{
  "question_ids": [1, 2, 3, 4, 5],
  "subject_id": 1,
  "batch_size": 10,
  "reprocess": false,
  "generate_embeddings": true,
  "extract_metadata": true,
  "process_images": true
}
```

**Response:**
```json
{
  "job_id": "job_uuid_123",
  "status": "started",
  "total_questions": 5,
  "estimated_completion_time": "Calculating...",
  "batch_size": 10
}
```

#### `GET /processing-status/{job_id}`
Get the status of a batch processing job.

**Response:**
```json
{
  "job_id": "job_uuid_123",
  "status": "processing",
  "progress": 60.0,
  "processed": 3,
  "failed": 0,
  "total": 5,
  "current_question": "Question 4",
  "estimated_remaining_time": "30 seconds",
  "errors": []
}
```

---

## 🔍 Search and Similarity Endpoints

### 7. Metadata Extraction

#### `POST /extract-metadata`
Extract comprehensive metadata from questions using AI.

**Request Body:**
```json
{
  "question_text": "What is the integral of x^2?",
  "answer": "x^3/3 + C",
  "subject": "calculus",
  "image_data": "base64_encoded_image"
}
```

**Response:**
```json
{
  "keywords": ["integral", "calculus", "function"],
  "concepts": ["integration", "antiderivative"],
  "prerequisites": ["basic algebra", "functions"],
  "learning_objectives": ["understand integration", "apply power rule"],
  "clarity_score": 0.9,
  "completeness_score": 0.8,
  "difficulty_confidence": 0.85,
  "processing_time": 1.5
}
```

### 8. Similarity Calculation

#### `POST /calculate-similarity`
Calculate similarity between two embeddings.

**Request Body:**
```json
{
  "embedding1": [0.1, 0.2, 0.3, ...],
  "embedding2": [0.2, 0.3, 0.1, ...],
  "similarity_type": "cosine"
}
```

**Response:**
```json
{
  "similarity_score": 0.85,
  "similarity_type": "cosine",
  "embedding_dimension": 768
}
```

### 9. Advanced Similar Question Search

#### `POST /find-similar-questions`
Find similar questions using advanced search capabilities.

**Request Body:**
```json
{
  "question_text": "What is the derivative of x^2?",
  "question_id": 123,
  "embedding": [0.1, 0.2, ...],
  "subject_filter": "mathematics",
  "difficulty_filter": [1, 2, 3],
  "limit": 10,
  "threshold": 0.5
}
```

**Response:**
```json
{
  "query_info": {
    "query_type": "text",
    "subject_filter": "mathematics",
    "difficulty_filter": [1, 2, 3],
    "threshold": 0.5
  },
  "similar_questions": [
    {
      "question_id": "similar_1",
      "question_text": "Find the derivative of f(x) = x^3",
      "similarity_score": 0.92,
      "subject": "mathematics",
      "difficulty": 2,
      "question_type": "short_answer"
    }
  ],
  "total_found": 5,
  "search_time": 0.3
}
```

---

## 🎯 Personalization Endpoints

### 10. Recommendations

#### `POST /recommendations`
Get personalized question recommendations.

**Request Body:**
```json
{
  "subject": "mathematics",
  "limit": 10,
  "difficulty_range": [1, 3],
  "exclude_attempted": true
}
```

**Response:**
```json
[
  {
    "question_id": "rec_123",
    "recommendation_strategy": "adaptive_learning",
    "confidence_score": 0.85,
    "reasoning": "Based on your weak areas in calculus",
    "estimated_difficulty": 2
  }
]
```

### 11. Learning Path Generation

#### `POST /learning-path`
Generate personalized learning paths.

**Request Body:**
```json
{
  "subject": "mathematics",
  "objectives": ["mastery", "exam_prep"],
  "path_type": "sequential",
  "max_sessions": 10,
  "session_duration_minutes": 30
}
```

**Response:**
```json
{
  "path_id": "path_uuid_123",
  "subject": "mathematics",
  "path_type": "sequential",
  "total_sessions": 8,
  "total_duration_minutes": 240,
  "estimated_completion_days": 14,
  "sessions": [
    {
      "session_type": "practice",
      "total_duration": 30,
      "steps_count": 3,
      "focus_areas": ["derivatives", "integrals"],
      "difficulty_range": [1, 3],
      "steps": [...]
    }
  ]
}
```

### 12. Difficulty Adaptation

#### `POST /adapt-difficulty`
Analyze performance and recommend difficulty adjustments.

**Request Body:**
```json
{
  "subject": "mathematics",
  "recent_interactions_count": 10
}
```

**Response:**
```json
{
  "current_difficulty": 2,
  "recommended_difficulty": 3,
  "confidence": "medium",
  "reasoning": ["Consistent improvement shown", "Ready for harder questions"],
  "should_adapt": true
}
```

---

## 👤 User Analytics Endpoints

### 13. User Profile

#### `GET /user-profile`
Get user's AI-generated profile and learning analytics.

**Response:**
```json
{
  "user_id": "user_123",
  "performance_level": "developing",
  "learning_style": "mixed",
  "preferred_difficulty": 2,
  "strong_subjects": ["algebra", "geometry"],
  "weak_subjects": ["calculus", "statistics"],
  "study_preferences": ["visual", "practice"],
  "learning_patterns": {
    "peak_hours": "evening",
    "preferred_session_length": 30
  },
  "total_interactions": 156
}
```

#### `POST /submit-interaction`
Submit question interaction for AI analysis.

**Form Data:**
```
question_id: "123"
subject: "mathematics"
difficulty: 2
is_correct: true
time_taken: 45
attempts: 1
hint_used: false
```

**Response:**
```json
{
  "status": "success",
  "message": "Interaction recorded successfully",
  "interaction_id": "interaction_uuid_123"
}
```

---

## 🔗 Legacy and Utility Endpoints

### 14. Similar Questions (Legacy)

#### `GET /similar-questions/{question_id}`
Find questions similar to a given question ID.

**Parameters:**
- `question_id`: ID of the question
- `limit`: Number of results (default: 5)

**Response:**
```json
{
  "original_question_id": "123",
  "similar_questions": [
    {
      "question_id": "sim_1",
      "similarity_score": 0.9,
      "subject": "mathematics",
      "difficulty": 2,
      "question_type": "multiple_choice"
    }
  ],
  "total_found": 3
}
```

### 15. System Information

#### `GET /health`
Health check for all AI services.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "text_processor": "active",
    "image_processor": "active",
    "vector_database": "active",
    "text_embeddings": "active",
    "image_embeddings": "active",
    "hybrid_embeddings": "active",
    "gemini_client": "active"
  },
  "test_analysis": {
    "success": true,
    "question_type": "multiple_choice"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### `GET /embedding-info`
Get embedding services configuration.

**Response:**
```json
{
  "status": "available",
  "embedding_config": {
    "fusion_method": "concatenation",
    "text_weight": 0.7,
    "image_weight": 0.3,
    "text_dim": 768,
    "image_dim": 768,
    "hybrid_dim": 1536,
    "supported_fusion_methods": ["concatenation", "weighted_average", "attention"],
    "supported_similarity_types": ["cosine", "euclidean", "dot_product"]
  },
  "services": {
    "text_embeddings": true,
    "image_embeddings": true,
    "hybrid_embeddings": true,
    "gemini_client": true
  }
}
```

#### `GET /models/available`
Get information about available AI models.

**Response:**
```json
{
  "text_analysis": {
    "available": true,
    "capabilities": ["question_type_detection", "difficulty_scoring", "keyword_extraction"]
  },
  "image_analysis": {
    "available": true,
    "capabilities": ["ocr", "mathematical_content_detection"]
  },
  "text_embeddings": {
    "available": true,
    "model": "text-embedding-004",
    "dimension": 768
  },
  "image_embeddings": {
    "available": true,
    "model": "gemini-pro-vision",
    "dimension": 768
  },
  "hybrid_embeddings": {
    "available": true,
    "fusion_methods": ["concatenation", "weighted_average", "attention"],
    "dimension": 1536
  },
  "llm": {
    "available": true,
    "model": "gemini-pro",
    "capabilities": ["explanation_generation", "hint_generation", "metadata_extraction"]
  }
}
```

---

## 🧪 Demo Endpoints (No Authentication Required)

### 16. Demo Text Analysis

#### `POST /demo/analyze-text`
Test text analysis without authentication.

**Request Body:**
```json
{
  "text": "What is the derivative of x^2?"
}
```

### 17. Demo Recommendations

#### `POST /demo/test-recommendation`
Test recommendation engine without authentication.

**Response:**
```json
{
  "success": true,
  "demo_profile": {
    "learning_style": "mixed",
    "subjects": ["mathematics", "computer_science"],
    "weak_areas": ["calculus", "algorithms"],
    "strong_areas": ["algebra", "programming"]
  },
  "recommendations": [
    {
      "strategy": "adaptive_learning",
      "reasoning": "Focus on weak areas with personalized difficulty",
      "confidence": 0.85,
      "priority": 0.9
    }
  ]
}
```

### 18. Demo Embeddings

#### `POST /demo/test-embeddings`
Test embedding services without authentication.

**Response:**
```json
{
  "success": true,
  "test_text": "What is the integral of x^2?",
  "services_available": {
    "text_embeddings": true,
    "image_embeddings": true,
    "hybrid_embeddings": true
  },
  "text_embedding": {
    "dimension": 768,
    "sample_values": [0.1, -0.2, 0.3, 0.4, -0.1],
    "success": true
  },
  "hybrid_embedding": {
    "dimension": 1536,
    "fusion_method": "concatenation",
    "success": true
  }
}
```

---

## 🔧 Implementation Details

### Technology Stack
- **FastAPI**: Web framework for API endpoints
- **Pydantic**: Data validation and serialization
- **Google Gemini Pro**: Large language model for text generation
- **Google Gemini Pro Vision**: Multimodal model for image analysis
- **Google Text-Embedding-004**: Text embedding generation
- **ChromaDB**: Vector database for similarity search
- **JWT**: Authentication and authorization
- **Background Tasks**: Asynchronous processing

### AI Services Architecture

#### Core Services
1. **TextEmbeddingService**: Handles text-to-vector conversion
2. **ImageEmbeddingService**: Processes images and generates embeddings
3. **HybridEmbeddingService**: Combines text and image embeddings
4. **GeminiClient**: Interfaces with Google's AI models
5. **ChromaClient**: Manages vector database operations

#### Processing Pipeline
1. **Input Validation**: Pydantic schema validation
2. **AI Processing**: Model inference and analysis
3. **Data Transformation**: Format conversion and normalization
4. **Storage**: Database and vector store updates
5. **Response Generation**: Structured API responses

### Error Handling
- Graceful degradation when AI services are unavailable
- Comprehensive error logging and reporting
- Fallback to mock responses for development
- Structured error responses with appropriate HTTP status codes

### Performance Considerations
- Background task processing for heavy operations
- Caching for frequently accessed data
- Pagination for large result sets
- Request/response compression
- Connection pooling for database operations

### Security Features
- JWT-based authentication for protected endpoints
- Input sanitization and validation
- Rate limiting (to be implemented)
- API key management for external services
- CORS configuration for cross-origin requests

---

## 📝 Usage Examples

### Basic Question Analysis
```python
import requests

# Analyze a question
response = requests.post(
    "http://localhost:8000/api/v1/ai/analyze-question",
    headers={"Authorization": "Bearer your_jwt_token"},
    json={
        "text": "What is the derivative of f(x) = x^2 + 3x?",
        "subject": "calculus"
    }
)
```

### Generate Embeddings
```python
# Generate text embedding
response = requests.post(
    "http://localhost:8000/api/v1/ai/embeddings/text",
    headers={"Authorization": "Bearer your_jwt_token"},
    json={
        "text": "Integration by parts formula",
        "task_type": "RETRIEVAL_DOCUMENT"
    }
)
```

### Process Image
```python
# Analyze question image
with open("question_image.png", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/ai/analyze-image",
        headers={"Authorization": "Bearer your_jwt_token"},
        files={"file": f}
    )
```

### Batch Processing
```python
# Start batch processing
response = requests.post(
    "http://localhost:8000/api/v1/ai/process-questions-batch",
    headers={"Authorization": "Bearer your_jwt_token"},
    json={
        "question_ids": [1, 2, 3, 4, 5],
        "batch_size": 10,
        "generate_embeddings": True
    }
)

job_id = response.json()["job_id"]

# Check status
status_response = requests.get(
    f"http://localhost:8000/api/v1/ai/processing-status/{job_id}",
    headers={"Authorization": "Bearer your_jwt_token"}
)
```

---

## 🚀 Getting Started

1. **Authentication**: Obtain a JWT token through the auth endpoints
2. **Health Check**: Test service availability with `/health`
3. **Model Info**: Check available models with `/models/available`
4. **Demo Endpoints**: Test functionality with demo endpoints (no auth required)
5. **Production Use**: Use authenticated endpoints for full functionality

---

## 📞 Support

For API support and questions:
- Review the endpoint documentation above
- Check the `/health` endpoint for service status
- Use demo endpoints for testing without authentication
- Refer to error messages for troubleshooting guidance

This comprehensive API provides powerful AI capabilities for educational question analysis, processing, and personalization in the AI-Powered Past Questions App. 