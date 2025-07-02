# Complete API Documentation - AI-Powered Past Questions App

## 🎯 Overview

This comprehensive guide documents all API endpoints available in the AI-Powered Past Questions App backend. The API provides complete functionality for user management, content delivery, practice sessions, analytics, AI-powered features, and administrative controls.

## 🔧 Base Configuration

**Base URL:** `http://localhost:8000/api/v1/`

**Authentication:** JWT Bearer tokens (except for demo endpoints)

**Content-Type:** `application/json` (unless specified otherwise)

---

## 📋 API Categories Summary

| Category | Endpoint Prefix | Description | Auth Required |
|----------|----------------|-------------|---------------|
| Authentication | `/auth` | User registration, login, token management | Partial |
| User Management | `/users` | Profile, settings, statistics | ✅ |
| Questions | `/questions` | CRUD, search, filtering | ✅ |
| Subjects & Topics | `/subjects` | Content organization | ✅ |
| Practice Sessions | `/practice` | Learning sessions, attempts, progress | ✅ |
| Analytics | `/analytics` | Performance insights, reports | ✅ |
| Search | `/search` | Advanced search, discovery | ✅ |
| AI Features | `/ai` | 23+ AI-powered endpoints | ✅ |
| File Upload | `/upload` | Image and document upload | ✅ |
| Notifications | `/notifications` | Real-time notifications, WebSocket | ✅ |
| Admin | `/admin` | Administrative controls | ✅ (Admin) |
| Testing | `/test` | Development/testing endpoints | ❌ |

---

## 🔐 Authentication Endpoints (`/auth`)

### User Registration
**`POST /register`**
```json
// Request
{
  "email": "student@university.edu",
  "username": "student123",
  "password": "securePassword123"
}

// Response
{
  "id": 1,
  "email": "student@university.edu",
  "username": "student123",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### User Login
**`POST /login`** or **`POST /token`**
```json
// Request
{
  "email": "student@university.edu",
  "password": "securePassword123"
}

// Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Token Refresh
**`POST /refresh`**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 👤 User Management (`/users`)

### Current User Profile
**`GET /me`** - Get current user profile  
**`PUT /me`** - Update profile  
**`PUT /me/password`** - Change password  

### User Statistics & Analytics
**`GET /me/statistics`** - Comprehensive user stats
```json
{
  "total_questions_attempted": 150,
  "correct_answers": 120,
  "accuracy_rate": 80.0,
  "total_study_time_minutes": 1440,
  "practice_sessions_completed": 25,
  "current_streak": 7,
  "achievements_unlocked": 3
}
```

**`GET /leaderboard`** - User rankings
- Query: `metric` (accuracy/volume), `days`, `limit`

---

## 📚 Questions Management (`/questions`)

### Browse & Search
**`GET /`** - List questions with filters  
**`GET /search`** - Text search with filters  
**`GET /random`** - Random questions for practice  

Query Parameters:
- `subject_id`, `topic_id`, `difficulty`, `question_type`
- `verified_only`, `skip`, `limit`

### Question Details
**`GET /{question_id}`** - Full question details  
**`GET /{question_id}/public`** - Question without answer (practice mode)  
**`GET /{question_id}/similar`** - Find similar questions  

### Question Management
**`POST /`** - Create new question  
**`POST /bulk`** - Bulk question creation  
**`PUT /{question_id}`** - Update question  
**`DELETE /{question_id}`** - Delete question  

### Metadata Management
**`POST /{question_id}/metadata`** - Add metadata  
**`POST /{question_id}/explanations`** - Add explanations  
**`POST /{question_id}/hints`** - Add hints  

---

## 📖 Subjects & Topics (`/subjects`)

### Subject Management
**`GET /`** - List all subjects  
**`GET /with-topics`** - Subjects with topics included  
**`GET /{subject_id}`** - Subject details  
**`POST /`** - Create subject (admin only)  

### Topic Management
**`GET /{subject_id}/topics`** - Topics for subject  
**`GET /{subject_id}/topics/with-question-count`** - Topics with counts  
**`POST /{subject_id}/topics`** - Create topic  
**`GET /topics/{topic_id}`** - Topic details  

### Search
**`GET /search`** - Search subjects  
**`GET /topics/search`** - Search topics  

---

## 🏃‍♂️ Practice Sessions (`/practice`)

### Session Management
**`POST /sessions`** - Create practice session
```json
{
  "session_type": "timed",
  "subject_id": 1,
  "difficulty_level": "intermediate",
  "question_count": 10,
  "time_limit_minutes": 30
}
```

**`GET /sessions`** - List user sessions  
**`GET /sessions/{session_id}`** - Session details  
**`PUT /sessions/{session_id}/complete`** - Complete session  

### Question Attempts
**`POST /attempts`** - Submit answer attempt
```json
{
  "question_id": 1,
  "session_id": 1,
  "user_answer": "f'(x) = 2x + 3",
  "time_taken_seconds": 45,
  "hint_used": false
}
```

**`GET /attempts`** - Attempts history  

### Bookmarks & Progress
**`POST /bookmarks`** - Bookmark question  
**`GET /bookmarks`** - List bookmarks  
**`GET /progress`** - Learning progress  
**`GET /progress/summary`** - Progress summary  

### User Profile & Preferences
**`GET /profile`** - Academic profile  
**`PUT /profile`** - Update profile  
**`GET /preferences`** - Learning preferences  
**`PUT /preferences`** - Update preferences  

---

## 📊 Analytics & Insights (`/analytics`)

### Dashboard & Overview
**`GET /dashboard`** - Main dashboard data  
**`GET /user-analytics`** - Detailed analytics  
**`GET /performance-trends`** - Performance over time  
**`GET /weekly-activity`** - Weekly breakdown  

### Detailed Analytics
**`GET /subject-performance`** - Performance by subject  
**`GET /learning-insights`** - AI-powered insights  
**`GET /comparison`** - Compare with other users  

### Reporting & Export
**`POST /reports/generate`** - Generate custom reports  
**`GET /export`** - Export data (CSV, JSON, PDF)  
**`POST /events`** - Track learning events  

---

## 🔍 Search & Discovery (`/search`)

### Advanced Search
**`GET /questions`** - Search questions with filters
- Query: `q` (required), `subject_ids`, `difficulty_levels`, `question_types`

**`GET /subjects-topics`** - Search subjects and topics  
**`GET /bookmarks`** - Search user bookmarks  

### Search Assistance
**`GET /suggestions`** - Search suggestions  
**`GET /autocomplete`** - Autocomplete with categories  
**`GET /popular`** - Popular search terms  
**`GET /trending`** - Trending searches  
**`GET /filters/options`** - Available filter options  

---

## 🤖 AI-Powered Features (`/ai`)

> **Full documentation:** See `AI_API_ROUTES_DOCUMENTATION.md`

### Core AI Services (5 endpoints)
- `POST /analyze-question` - AI question analysis
- `POST /analyze-image` - OCR and image analysis
- `POST /embeddings/text` - Text embeddings
- `POST /embeddings/image` - Image embeddings  
- `POST /embeddings/hybrid` - Multimodal embeddings

### Question Processing (4 endpoints)
- `POST /process-question` - Comprehensive processing
- `POST /process-questions-batch` - Batch processing
- `GET /processing-status/{job_id}` - Check batch status
- `POST /extract-metadata` - AI metadata extraction

### Personalization (4 endpoints)
- `POST /recommendations` - Personalized recommendations
- `POST /learning-path` - Generate learning paths
- `POST /adapt-difficulty` - Difficulty adaptation
- `GET /user-profile` - AI-generated profile

### Demo Endpoints (3 endpoints, no auth)
- `POST /demo/analyze-text`
- `POST /demo/test-recommendation`
- `POST /demo/test-embeddings`

---

## 📁 File Upload (`/upload`)

### Upload Operations
**`POST /image`** - Upload image files
- Supports: JPEG, PNG, GIF, WebP
- Max size: 10MB

**`POST /document`** - Upload documents
- Supports: PDF, Word, Text
- Max size: 10MB

**`POST /multiple`** - Upload multiple files (max 10)

### File Management
**`GET /info/{filename}`** - File information  
**`DELETE /file/{filename}`** - Delete file  

---

## 🔔 Real-time Notifications (`/notifications`)

### WebSocket Connection
**`WS /ws/{user_id}`** - Real-time notifications
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/notifications/ws/123');
ws.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  console.log('New notification:', notification);
};
```

### Notification Management
**`GET /`** - List notifications  
**`GET /unread-count`** - Unread count  
**`POST /{notification_id}/read`** - Mark as read  
**`POST /read-all`** - Mark all as read  
**`DELETE /{notification_id}`** - Delete notification  

### Settings & Admin
**`GET /settings`** - Notification preferences  
**`POST /settings`** - Update preferences  
**`POST /send`** - Send to user (admin)  
**`POST /broadcast`** - Broadcast (admin)  

---

## 🔧 Admin Panel (`/admin`)

**`GET /dashboard`** - Admin dashboard with system stats  
**`GET /users`** - All users management (admin only)

---

## 🧪 Testing Endpoints (`/test`)

> **No authentication required** - Development/testing only

**`GET /repository/user/methods`** - Test user repository  
**`GET /repository/user/leaderboard`** - Test leaderboard  
**`GET /database/status`** - Database connectivity  
**`GET /repository/user/create-sample`** - Create sample data  

---

## 🚀 Quick Start Guide

### 1. Authentication Flow
```bash
# Register
curl -X POST "/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user123","password":"password"}'

# Login
curl -X POST "/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Use token in subsequent requests
curl -H "Authorization: Bearer YOUR_TOKEN" "/api/v1/users/me"
```

### 2. Basic Operations
```javascript
// Get questions
fetch('/api/v1/questions?subject_id=1&limit=10', {
  headers: { 'Authorization': 'Bearer ' + token }
})

// Start practice session
fetch('/api/v1/practice/sessions', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    session_type: 'timed',
    subject_id: 1,
    question_count: 10
  })
})

// Submit answer
fetch('/api/v1/practice/attempts', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    question_id: 1,
    user_answer: "42",
    time_taken_seconds: 30
  })
})
```

### 3. AI Features
```javascript
// Get AI recommendations
fetch('/api/v1/ai/recommendations', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    subject: "mathematics",
    limit: 5,
    difficulty_range: [1, 3]
  })
})

// Analyze question with AI
fetch('/api/v1/ai/analyze-question', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: "What is the derivative of x^2?",
    subject: "mathematics"
  })
})
```

---

## 📝 Response Formats

### Standard Success Response
```json
{
  "id": 1,
  "data": { /* actual data */ },
  "message": "Operation successful",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Error Response
```json
{
  "detail": "Validation error: Invalid email format",
  "error_code": "VALIDATION_ERROR",
  "status_code": 400,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Paginated Response
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "pages": 5,
  "has_next": true,
  "has_prev": false
}
```

---

## 🔒 Security & Best Practices

### Authentication
- JWT tokens expire after 1 hour (configurable)
- Use refresh tokens for long-term sessions
- Include `Authorization: Bearer <token>` header

### Rate Limiting
- API calls are rate-limited per user
- File uploads have size restrictions (10MB)
- Batch operations have reasonable limits

### Validation
- All inputs are validated using Pydantic models
- File uploads are validated for type and size
- SQL injection protection via SQLAlchemy ORM

---

## 📚 Additional Resources

- **AI Endpoints:** `AI_API_ROUTES_DOCUMENTATION.md` (811 lines)
- **Implementation Details:** `FASTAPI_IMPLEMENTATION_SUMMARY.md` (345 lines)
- **API Testing:** Use Swagger UI at `http://localhost:8000/docs`
- **WebSocket Testing:** Use any WebSocket client with the notification endpoints

---

**Total Endpoints:** 100+ across 12 categories  
**Authentication Required:** Most endpoints (except testing and demos)  
**Real-time Features:** WebSocket notifications  
**AI Features:** 23+ advanced AI endpoints  
**File Support:** Image and document upload/management

This API provides complete backend functionality for a modern, AI-powered educational platform! 🎓🚀 