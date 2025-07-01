# papa

AI powered past questions app

# AI-Powered Past Questions App - Project Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Core Features](#core-features)
5. [User Experience Design](#user-experience-design)
6. [Technical Architecture](#technical-architecture)
7. [AI Pipeline Architecture](#ai-pipeline-architecture)
8. [Database Design](#database-design)
9. [API Specifications](#api-specifications)
10. [Development Phases](#development-phases)
11. [Security & Privacy](#security--privacy)
12. [Performance Considerations](#performance-considerations)
13. [Deployment Strategy](#deployment-strategy)

---

## Project Overview

### Vision Statement

An AI-powered mobile application that revolutionizes exam preparation by providing personalized, intelligent access to past questions with adaptive learning capabilities.

### Mission

To create a comprehensive, AI-driven platform that helps students efficiently prepare for semester exams through personalized question recommendations, intelligent explanations, and adaptive difficulty progression.

### Target Audience

- University students preparing for semester exams
- Students seeking targeted practice for specific subjects
- Learners who want personalized, adaptive study experiences

### Key Value Propositions

1. **Personalized Learning**: AI-driven recommendations based on individual performance
2. **Intelligent Content**: Multi-modal question processing with smart categorization
3. **Priority-Based Study**: Automatic identification of frequently repeated questions
4. **Progressive Difficulty**: Adaptive difficulty adjustment based on user performance
5. **Comprehensive Analytics**: Detailed performance tracking and insights

---

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mobile App    │    │   FastAPI       │    │   AI Services   │
│  (React Native) │◄──►│   Backend       │◄──►│   (Google APIs) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Database      │
                    │ PostgreSQL +    │
                    │ Chroma Vector   │
                    └─────────────────┘
```

### Component Overview

- **Mobile Frontend**: React Native app for cross-platform compatibility
- **API Backend**: FastAPI server handling business logic and AI integration
- **Vector Database**: Chroma for semantic search and question matching
- **Relational Database**: PostgreSQL for structured data
- **AI Services**: Google Gemini for LLM, Google Cloud Vision for OCR
- **File Storage**: Cloud storage for images and documents

---

## Technology Stack

### Frontend (Mobile)

- **Framework**: React Native 0.72+
- **State Management**: Redux Toolkit with RTK Query
- **Navigation**: React Navigation v6
- **UI Components**: React Native Elements / NativeBase
- **Charts**: Victory Native for analytics
- **Offline Storage**: React Native Async Storage
- **Push Notifications**: React Native Firebase

### Backend

- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **Authentication**: FastAPI-Users with JWT
- **Database ORM**: SQLAlchemy 2.0+
- **Async Support**: AsyncIO with Uvicorn
- **Background Tasks**: Celery with Redis
- **API Documentation**: Automatic OpenAPI/Swagger

### Database & Storage

- **Primary Database**: PostgreSQL 15+
- **Vector Database**: Chroma 0.4+
- **Cache**: Redis 7+
- **File Storage**: AWS S3 / Google Cloud Storage
- **Search Engine**: PostgreSQL Full-Text Search + Vector Search

### AI & ML Services

- **LLM**: Google Gemini Pro
- **Embeddings**: Google Text-Embedding-004
- **OCR**: Google Document AI / Cloud Vision API
- **Image Processing**: Google Cloud Vision API
- **Text Processing**: spaCy, NLTK

### DevOps & Infrastructure

- **Containerization**: Docker & Docker Compose
- **Orchestration**: Kubernetes (production)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: Structured logging with Loguru
- **Cloud Provider**: Google Cloud Platform / AWS

---

## Core Features

### 1. User Management & Personalization

- **User Registration/Login**: Email, social login options
- **Onboarding Process**: Academic level, subjects, goals, study preferences
- **Profile Management**: Academic information, study preferences, goals
- **Personalization Engine**: AI-driven content recommendations

### 2. Question Management

- **Multi-Modal Support**: Text, images, PDFs, mathematical equations
- **Smart Categorization**: Subject, topic, difficulty, question type
- **Priority Flagging**: Automatic identification of frequently repeated questions
- **Quality Assurance**: Duplicate detection, content validation
- **User-Generated Content**: Community contributions with moderation

### 3. Intelligent Search & Discovery

- **Semantic Search**: Vector similarity search for question matching
- **Advanced Filtering**: Subject, year, difficulty, question type, priority
- **Mixed Browsing**: Multiple discovery paths (subject-first, difficulty-first, random)
- **Smart Recommendations**: Personalized question suggestions
- **Trending Content**: Popular and recently added questions

### 4. Study Features

- **Practice Modes**: Quick practice, targeted study, full mock tests
- **Adaptive Difficulty**: Progressive difficulty adjustment
- **Spaced Repetition**: Intelligent review scheduling
- **Bookmarking**: Save questions for later review
- **Progress Tracking**: Comprehensive performance analytics

### 5. AI-Powered Learning

- **Intelligent Explanations**: Step-by-step solutions with multiple approaches
- **Progressive Hints**: Multi-level hint system
- **Similar Questions**: AI-generated variations for additional practice
- **Weak Area Identification**: Pattern analysis for targeted improvement
- **Smart Study Plans**: Personalized study schedules

### 6. Analytics & Insights

- **Performance Dashboard**: Visual analytics and progress tracking
- **Subject-Wise Analysis**: Strength and weakness mapping
- **Time Management**: Study time optimization suggestions
- **Achievement System**: Badges, streaks, and milestones
- **Comparative Analytics**: Anonymous peer comparisons

---

## User Experience Design

### Onboarding Flow

1. **Welcome Screen**: App introduction and value proposition
2. **Account Creation**: Registration with basic information
3. **Academic Profile**: University, degree, year, subjects
4. **Learning Preferences**: Study goals, available time, difficulty preference
5. **Initial Assessment**: Optional quick assessment for personalization
6. **Dashboard Introduction**: Feature walkthrough

### Navigation Structure

```
Bottom Tab Navigation:
├── Home (Dashboard)
├── Practice (Question browsing)
├── Analytics (Performance insights)
├── Profile (Settings & preferences)

Top-Level Screens:
├── Question Detail & Practice
├── Subject Selection
├── Mock Test Interface
├── Explanation & Hints
├── Bookmarks & Saved Content
```

### Key User Flows

1. **Quick Practice**: Home → Select subject → Practice questions → Review results
2. **Targeted Study**: Practice → Filter by criteria → Study session → Analytics
3. **Mock Test**: Home → Full test mode → Timed session → Detailed results
4. **Content Discovery**: Browse → Search/Filter → Preview → Practice

---

## Technical Architecture

### Backend Architecture Pattern

- **Clean Architecture**: Separation of concerns with clear boundaries
- **Repository Pattern**: Data access abstraction
- **Service Layer**: Business logic encapsulation
- **Dependency Injection**: FastAPI's built-in DI system

### API Design Principles

- **RESTful Design**: Standard HTTP methods and status codes
- **Versioning**: URL-based versioning (/api/v1/)
- **Pagination**: Cursor-based pagination for large datasets
- **Rate Limiting**: User-based and endpoint-based limits
- **Error Handling**: Consistent error response format

### Data Flow Architecture

```
Mobile App → API Gateway → FastAPI Routes → Services → Repositories → Database
                                      ↓
                               AI Services (Async)
                                      ↓
                              Background Processing
```

### Caching Strategy

- **Application Cache**: Redis for frequent queries
- **Database Query Cache**: PostgreSQL query result caching
- **Vector Cache**: Chroma similarity search result caching
- **CDN**: Static asset delivery optimization

---

## AI Pipeline Architecture

### Question Processing Pipeline

```
Raw Input → Content Extraction → Metadata Enrichment → Vector Embedding → Quality Scoring → Database Storage
```

#### 1. Content Extraction

- **Text Questions**: Direct text processing with cleaning and normalization
- **Image Questions**: OCR using Google Document AI for text extraction
- **PDF Questions**: Text extraction with layout preservation
- **Mathematical Content**: LaTeX/MathML recognition and processing

#### 2. Metadata Enrichment

- **Subject Classification**: AI-powered subject and topic tagging
- **Difficulty Assessment**: Multi-factor difficulty scoring
- **Question Type Detection**: MCQ, short answer, essay, numerical
- **Keyword Extraction**: Important terms and concepts identification

#### 3. Vector Embedding Generation

- **Text Embeddings**: Google Text-Embedding-004 for semantic similarity
- **Image Embeddings**: Visual feature extraction for image-based questions
- **Hybrid Embeddings**: Combined text+image representations
- **Metadata Embeddings**: Structured information encoding

#### 4. Quality Scoring System

- **Duplicate Detection**: Similarity threshold-based duplicate identification
- **Completeness Score**: Assessment of question and answer quality
- **Frequency Analysis**: Cross-exam appearance tracking
- **Community Validation**: User feedback integration

### Personalization Engine

```
User Behavior → Performance Analysis → Learning Pattern Recognition → Recommendation Generation
```

#### Components:

1. **User Modeling**: Learning preferences, performance patterns, knowledge gaps
2. **Content Matching**: Vector similarity + collaborative filtering
3. **Difficulty Adaptation**: Dynamic difficulty adjustment algorithm
4. **Study Path Generation**: Personalized learning sequences

### AI Response Generation

- **Explanation Engine**: Multi-step solution generation with reasoning
- **Hint System**: Progressive hint delivery without spoiling answers
- **Similar Question Generator**: Variation creation maintaining difficulty and topic
- **Weak Area Analyzer**: Pattern recognition in incorrect responses

---

## Database Design

### PostgreSQL Schema (Relational Data)

#### Core Tables

```sql
-- Users and Authentication
users (id, email, username, hashed_password, created_at, updated_at)
user_profiles (user_id, academic_level, university, degree, year, subjects)
user_preferences (user_id, study_goals, difficulty_preference, study_time)

-- Questions and Content
questions (id, title, content, type, subject_id, difficulty_level, created_at)
question_metadata (question_id, tags, keywords, source, year, priority_score)
question_images (id, question_id, image_url, ocr_text, processed_at)
subjects (id, name, code, department, description)
topics (id, subject_id, name, parent_topic_id)

-- User Interactions
user_attempts (id, user_id, question_id, answer, is_correct, time_taken, created_at)
user_bookmarks (user_id, question_id, created_at)
user_progress (user_id, subject_id, total_questions, correct_answers, last_practiced)

-- AI Generated Content
explanations (id, question_id, content, type, ai_generated, created_at)
hints (id, question_id, level, content, created_at)
similar_questions (original_question_id, similar_question_id, similarity_score)
```

### Chroma Vector Database Schema

```python
# Question Vectors Collection
questions_collection = {
    "name": "questions",
    "metadata_schema": {
        "question_id": "string",
        "subject": "string",
        "topic": "string",
        "difficulty": "integer",
        "type": "string",
        "priority_score": "float",
        "year": "integer"
    }
}

# User Learning Vectors Collection
user_learning_collection = {
    "name": "user_learning_patterns",
    "metadata_schema": {
        "user_id": "string",
        "subject": "string",
        "performance_level": "float",
        "learning_style": "string"
    }
}
```

---

## API Specifications

### Authentication Endpoints

```
POST /api/v1/auth/register - User registration
POST /api/v1/auth/login - User login
POST /api/v1/auth/refresh - Token refresh
POST /api/v1/auth/logout - User logout
POST /api/v1/auth/forgot-password - Password reset request
```

### User Management

```
GET /api/v1/users/profile - Get user profile
PUT /api/v1/users/profile - Update profile
GET /api/v1/users/preferences - Get user preferences
PUT /api/v1/users/preferences - Update preferences
GET /api/v1/users/analytics - Get user analytics
```

### Question Management

```
GET /api/v1/questions - List questions with filters
GET /api/v1/questions/{id} - Get specific question
POST /api/v1/questions - Create new question (admin/contributor)
PUT /api/v1/questions/{id} - Update question
DELETE /api/v1/questions/{id} - Delete question

GET /api/v1/questions/search - Semantic search
GET /api/v1/questions/recommendations - Personalized recommendations
GET /api/v1/questions/similar/{id} - Find similar questions
```

### Practice & Learning

```
POST /api/v1/practice/start - Start practice session
POST /api/v1/practice/submit - Submit answer
GET /api/v1/practice/results/{session_id} - Get session results
POST /api/v1/practice/bookmark - Bookmark question
GET /api/v1/practice/bookmarks - Get bookmarked questions

GET /api/v1/explanations/{question_id} - Get AI explanation
GET /api/v1/hints/{question_id}/{level} - Get progressive hints
```

### Analytics & Progress

```
GET /api/v1/analytics/dashboard - User dashboard data
GET /api/v1/analytics/performance - Performance metrics
GET /api/v1/analytics/subjects - Subject-wise analytics
GET /api/v1/analytics/progress - Learning progress tracking
```

---

## Development Phases

### Phase 1: MVP Foundation (Months 1-3)

**Backend:**

- User authentication and profile management
- Basic question CRUD operations
- PostgreSQL database setup
- Simple search functionality
- Basic API endpoints

**Frontend:**

- User authentication flows
- Basic question browsing interface
- Simple practice mode
- User profile management
- Core navigation structure

**Deliverables:**

- Working authentication system
- Basic question database with 100+ sample questions
- Simple mobile app with core functionality
- Basic deployment setup

### Phase 2: AI Integration (Months 4-6)

**Backend:**

- Chroma vector database integration
- Google Gemini API integration
- Semantic search implementation
- Basic AI explanation generation
- OCR processing pipeline

**Frontend:**

- Advanced search and filtering
- AI-powered explanations interface
- Improved question display (multi-modal)
- Basic analytics dashboard
- Offline capabilities

**Deliverables:**

- AI-powered search and recommendations
- Intelligent explanation system
- Enhanced mobile app with offline support
- 1000+ processed questions in database

### Phase 3: Advanced Features (Months 7-9)

**Backend:**

- Personalization engine
- Advanced analytics system
- Background job processing
- Performance optimization
- Admin dashboard

**Frontend:**

- Comprehensive analytics
- Gamification features
- Advanced study modes
- Social features (leaderboards)
- Push notifications

**Deliverables:**

- Full personalization system
- Comprehensive analytics dashboard
- Gamified learning experience
- Production-ready application

### Phase 4: Scale & Polish (Months 10-12)

**Backend:**

- Performance optimization
- Advanced caching
- Monitoring and logging
- Security hardening
- API rate limiting

**Frontend:**

- UI/UX improvements
- Performance optimization
- Advanced offline capabilities
- Beta testing feedback integration
- App store preparation

**Deliverables:**

- Production-grade application
- App store releases (iOS/Android)
- Comprehensive documentation
- Monitoring and analytics setup

---

## Security & Privacy

### Authentication & Authorization

- **JWT-based authentication** with refresh tokens
- **Role-based access control** (Student, Contributor, Admin)
- **OAuth integration** for social login
- **Multi-factor authentication** option
- **Session management** with automatic expiry

### Data Protection

- **Data encryption** at rest and in transit
- **Personal data anonymization** for analytics
- **GDPR compliance** for EU users
- **User consent management** for data usage
- **Right to deletion** implementation

### API Security

- **Rate limiting** per user and endpoint
- **Input validation** and sanitization
- **SQL injection protection** via ORM
- **CORS configuration** for mobile apps
- **API key management** for external services

### Infrastructure Security

- **Container security** scanning
- **Environment variable** protection
- **Database access control** with limited privileges
- **Regular security updates** and patches
- **Vulnerability scanning** in CI/CD

---

## Performance Considerations

### Database Optimization

- **Database indexing** strategy for frequent queries
- **Query optimization** with EXPLAIN analysis
- **Connection pooling** for efficient resource usage
- **Read replicas** for scaling read operations
- **Partitioning** for large tables (user_attempts)

### Caching Strategy

- **Redis caching** for frequent API responses
- **Vector search caching** for similar queries
- **Database query result caching**
- **CDN caching** for static assets
- **Application-level caching** for computed results

### Mobile App Performance

- **Lazy loading** for question lists
- **Image optimization** and compression
- **Offline data storage** strategy
- **Bundle size optimization**
- **Memory management** for large datasets

### Scalability Planning

- **Horizontal scaling** with load balancers
- **Microservices architecture** consideration
- **Database sharding** strategy
- **AI service rate limiting** and optimization
- **Background job scaling** with Celery workers

---

## Deployment Strategy

### Development Environment

- **Docker Compose** for local development
- **Hot reloading** for both backend and frontend
- **Local database** with sample data
- **Mock AI services** for development
- **Automated testing** setup

### Staging Environment

- **Kubernetes cluster** mirroring production
- **Continuous deployment** from develop branch
- **Integration testing** with real AI services
- **Performance testing** and monitoring
- **User acceptance testing** environment

### Production Environment

- **Multi-zone deployment** for high availability
- **Auto-scaling** based on load metrics
- **Database clustering** with failover
- **CDN integration** for global content delivery
- **Monitoring and alerting** system

### CI/CD Pipeline

- **Automated testing** (unit, integration, e2e)
- **Code quality checks** with linting and formatting
- **Security scanning** for vulnerabilities
- **Automated deployment** to staging and production
- **Rollback capability** for failed deployments

### Monitoring & Observability

- **Application metrics** with Prometheus
- **Log aggregation** with structured logging
- **Error tracking** with Sentry
- **Performance monitoring** with APM tools
- **User analytics** with privacy-compliant tracking

---

## Success Metrics & KPIs

### User Engagement

- Daily/Monthly Active Users (DAU/MAU)
- Session duration and frequency
- Question completion rates
- Feature adoption rates
- User retention (1-day, 7-day, 30-day)

### Learning Effectiveness

- Improvement in user accuracy over time
- Adaptive difficulty system effectiveness
- Spaced repetition engagement rates
- Time to competency in subjects
- User-reported learning outcomes

### Technical Performance

- API response times (p95, p99)
- Database query performance
- AI service response times
- Mobile app crash rates
- System uptime and availability

### Business Metrics

- User acquisition cost
- User lifetime value
- Content generation rate (user-contributed)
- Premium feature conversion rates
- Customer satisfaction scores

---

api endopoints:
[
"/",
"/api/v1/ai/adapt-difficulty",
"/api/v1/ai/analyze-image",
"/api/v1/ai/analyze-question",
"/api/v1/ai/demo/analyze-text",
"/api/v1/ai/demo/test-recommendation",
"/api/v1/ai/health",
"/api/v1/ai/learning-path",
"/api/v1/ai/recommendations",
"/api/v1/ai/similar-questions/{question_id}",
"/api/v1/ai/submit-interaction",
"/api/v1/ai/user-profile",
"/api/v1/auth/login",
"/api/v1/auth/login-json",
"/api/v1/auth/logout",
"/api/v1/auth/refresh",
"/api/v1/auth/register",
"/api/v1/auth/token",
"/api/v1/test/database/status",
"/api/v1/test/repository/user/active",
"/api/v1/test/repository/user/by-university",
"/api/v1/test/repository/user/create-sample",
"/api/v1/test/repository/user/leaderboard",
"/api/v1/test/repository/user/methods",
"/api/v1/test/repository/user/search",
"/api/v1/users/",
"/api/v1/users/active",
"/api/v1/users/by-university",
"/api/v1/users/leaderboard",
"/api/v1/users/me",
"/api/v1/users/me/password",
"/api/v1/users/me/profile",
"/api/v1/users/me/statistics",
"/api/v1/users/me/update-last-login",
"/api/v1/users/search",
"/api/v1/users/statistics/{user_id}",
"/api/v1/users/test/repository-methods",
"/api/v1/users/{user_id}",
"/api/v1/users/{user_id}/deactivate",
"/api/v1/users/{user_id}/reactivate"
/api/v1/subjects/ # Subject and topic management
/api/v1/questions/ # Question CRUD and search
/api/v1/practice/ # Practice sessions and progress
/api/v1/analytics/ # User analytics and insights
/api/v1/search/ # Advanced search functionality
/api/v1/admin/ # Administrative functions
/api/v1/auth/ # Authentication (existing)
/api/v1/users/ # User management (existing)
/api/v1/ai/ # AI features (existing)
]
