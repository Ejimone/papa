# AI API Endpoints Testing Guide

## Overview

This guide helps you test the comprehensive AI functionality we've implemented for the past questions app.

## Quick Start

### Option 1: Automated Testing (Recommended)

```bash
cd backend
./test_ai.sh
```

This script will:

1. Start the FastAPI server
2. Run automated tests for all AI endpoints
3. Keep the server running for manual testing
4. Show results and next steps

### Option 2: Manual Testing

1. **Start the server:**

   ```bash
   cd backend
   python run.py
   ```

2. **Open API Documentation:**

   - Go to: http://localhost:4321/api/v1/docs
   - This shows all available endpoints with interactive testing

3. **Run basic tests:**
   ```bash
   python test_ai_simple.py
   ```

## AI Endpoints Available

### 1. Health Check

- **Endpoint:** `GET /api/v1/ai/health`
- **Description:** Check if all AI services are working
- **No authentication required**

### 2. Question Analysis

- **Endpoint:** `POST /api/v1/ai/analyze-question`
- **Description:** Analyze question text for type, difficulty, keywords
- **Requires authentication**

### 3. Image Processing (OCR)

- **Endpoint:** `POST /api/v1/ai/analyze-image`
- **Description:** Extract text from images and analyze mathematical content
- **Requires authentication**

### 4. Personalized Recommendations

- **Endpoint:** `POST /api/v1/ai/recommendations`
- **Description:** Get personalized question recommendations
- **Requires authentication**

### 5. Learning Path Generation

- **Endpoint:** `POST /api/v1/ai/learning-path`
- **Description:** Generate personalized study plans
- **Requires authentication**

### 6. Difficulty Adaptation

- **Endpoint:** `POST /api/v1/ai/adapt-difficulty`
- **Description:** Adapt question difficulty based on performance
- **Requires authentication**

### 7. User AI Profile

- **Endpoint:** `GET /api/v1/ai/user-profile`
- **Description:** Get AI-generated user learning profile
- **Requires authentication**

### 8. Similar Questions

- **Endpoint:** `GET /api/v1/ai/similar-questions/{question_id}`
- **Description:** Find semantically similar questions
- **Requires authentication**

### 9. Submit Interaction

- **Endpoint:** `POST /api/v1/ai/submit-interaction`
- **Description:** Track user interactions for personalization
- **Requires authentication**

## Example Test Requests

### Health Check

```bash
curl http://localhost:4321/api/v1/ai/health
```

### Question Analysis (with auth)

```bash
curl -X POST "http://localhost:4321/api/v1/ai/analyze-question" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What is the derivative of f(x) = x^2 + 3x - 5?",
    "subject": "mathematics"
  }'
```

### Get Recommendations

```bash
curl -X POST "http://localhost:4321/api/v1/ai/recommendations" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "mathematics",
    "limit": 5,
    "exclude_attempted": true
  }'
```

## Authentication

Most AI endpoints require authentication. To get a token:

1. **Register or login through the auth endpoints**
2. **Use the token in the Authorization header:**
   ```
   Authorization: Bearer YOUR_TOKEN_HERE
   ```

## Environment Variables

Make sure these are set in your `.env` file:

```env
# Google AI
GOOGLE_API_KEY=your_google_api_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost/database_name

# Redis (for caching)
REDIS_URL=redis://localhost:6379

# JWT
SECRET_KEY=your_secret_key_here
```

## AI Services Status

The AI implementation includes:

✅ **Text Processing**

- Question type detection (MCQ, short answer, essay, numerical)
- Difficulty scoring based on multiple factors
- Keyword extraction and topic identification
- Mathematical content detection

✅ **Image Processing**

- OCR using Google Cloud Vision API
- Mathematical formula recognition
- Text extraction with layout preservation

✅ **Vector Database**

- ChromaDB integration for semantic search
- Question embeddings for similarity matching
- Efficient retrieval and ranking

✅ **Personalization Engine**

- User behavior modeling
- Performance pattern analysis
- Adaptive recommendation strategies

✅ **Learning Path Generation**

- Sequential, spiral, and weakness-focused paths
- Spaced repetition integration
- Progress tracking and adaptation

✅ **Difficulty Adaptation**

- Real-time difficulty adjustment
- Performance-based scaling
- Confidence interval analysis

## Troubleshooting

### Common Issues

1. **Server won't start:**

   - Check if port 4321 is available
   - Verify Python dependencies are installed
   - Check environment variables

2. **AI endpoints return errors:**

   - Verify Google API key is set
   - Check database connection
   - Ensure Redis is running (if using caching)

3. **Authentication errors:**
   - Get a valid token from `/api/v1/auth/login`
   - Check token expiration
   - Verify user permissions

### Dependency Installation

```bash
cd backend
pip install -r requirements/dev.txt
```

### Database Setup

```bash
cd backend
python scripts/init_db.py
python scripts/seed_data.py
```

## Next Steps

After successful testing:

1. **Add more test data** - Questions, users, interactions
2. **Configure production AI services** - Google Cloud APIs
3. **Implement caching** - Redis for performance
4. **Add monitoring** - Track AI service performance
5. **Mobile app integration** - Connect React Native frontend

## Support

For issues or questions:

1. Check the FastAPI logs in the terminal
2. Review the error responses from endpoints
3. Verify all dependencies and environment variables
4. Check the project documentation in `copilot-instructions.md`
