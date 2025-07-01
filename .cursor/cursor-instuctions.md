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

Backend-File-Structure:
backend/
├── app/
│ ├── **init**.py
│ ├── main.py # FastAPI application entry point
│ ├── config.py # Configuration settings
│ ├── dependencies.py # Dependency injection
│ ├── exceptions.py # Custom exceptions
│ ├── middleware.py # Custom middleware
│ │
│ ├── api/ # API layer
│ │ ├── **init**.py
│ │ ├── deps.py # API dependencies
│ │ ├── errors/ # Error handlers
│ │ │ ├── **init**.py
│ │ │ ├── http_error.py
│ │ │ └── validation_error.py
│ │ │
│ │ └── v1/ # API version 1
│ │ ├── **init**.py
│ │ ├── api.py # Main API router
│ │ └── endpoints/ # API endpoints
│ │ ├── **init**.py
│ │ ├── auth.py # Authentication endpoints
│ │ ├── users.py # User management
│ │ ├── questions.py # Question management
│ │ ├── practice.py # Practice sessions
│ │ ├── analytics.py # Analytics endpoints
│ │ ├── search.py # Search functionality
│ │ ├── subjects.py # Subject management
│ │ └── admin.py # Admin endpoints
│ │
│ ├── core/ # Core functionality
│ │ ├── **init**.py
│ │ ├── config.py # Core configuration
│ │ ├── security.py # Security utilities
│ │ ├── database.py # Database configuration
│ │ ├── redis.py # Redis configuration
│ │ ├── logging.py # Logging configuration
│ │ └── events.py # Application events
│ │
│ ├── models/ # Database models
│ │ ├── **init**.py
│ │ ├── base.py # Base model class
│ │ ├── user.py # User models
│ │ ├── question.py # Question models
│ │ ├── subject.py # Subject models
│ │ ├── practice.py # Practice session models
│ │ ├── analytics.py # Analytics models
│ │ └── associations.py # Many-to-many relationships
│ │
│ ├── schemas/ # Pydantic schemas
│ │ ├── **init**.py
│ │ ├── base.py # Base schema classes
│ │ ├── user.py # User schemas
│ │ ├── question.py # Question schemas
│ │ ├── subject.py # Subject schemas
│ │ ├── practice.py # Practice schemas
│ │ ├── analytics.py # Analytics schemas
│ │ ├── auth.py # Authentication schemas
│ │ └── common.py # Common schemas
│ │
│ ├── services/ # Business logic layer
│ │ ├── **init**.py
│ │ ├── base.py # Base service class
│ │ ├── user_service.py # User business logic
│ │ ├── question_service.py # Question business logic
│ │ ├── practice_service.py # Practice session logic
│ │ ├── analytics_service.py # Analytics logic
│ │ ├── search_service.py # Search logic
│ │ ├── auth_service.py # Authentication logic
│ │ └── notification_service.py # Notification logic
│ │
│ ├── repositories/ # Data access layer
│ │ ├── **init**.py
│ │ ├── base.py # Base repository class
│ │ ├── user_repository.py # User data access
│ │ ├── question_repository.py # Question data access
│ │ ├── practice_repository.py # Practice data access
│ │ ├── analytics_repository.py # Analytics data access
│ │ └── subject_repository.py # Subject data access
│ │
│ ├── ai/ # AI/ML functionality
│ │ ├── **init**.py
│ │ ├── embeddings/ # Embedding generation
│ │ │ ├── **init**.py
│ │ │ ├── text_embeddings.py # Text embedding service
│ │ │ ├── image_embeddings.py # Image embedding service
│ │ │ └── hybrid_embeddings.py # Combined embeddings
│ │ │
│ │ ├── vector_db/ # Vector database operations
│ │ │ ├── **init**.py
│ │ │ ├── client.py # Chroma client
│ │ │ ├── collections.py # Collection management
│ │ │ └── queries.py # Vector queries
│ │ │
│ │ ├── llm/ # Large Language Model integration
│ │ │ ├── **init**.py
│ │ │ ├── gemini_client.py # Google Gemini client
│ │ │ ├── prompt_templates.py # Prompt templates
│ │ │ └── response_parser.py # Response parsing
│ │ │
│ │ ├── processing/ # Content processing
│ │ │ ├── **init**.py
│ │ │ ├── text_processor.py # Text processing
│ │ │ ├── image_processor.py # Image/OCR processing
│ │ │ ├── pdf_processor.py # PDF processing
│ │ │ └── metadata_extractor.py # Metadata extraction
│ │ │
│ │ ├── personalization/ # Personalization engine
│ │ │ ├── **init**.py
│ │ │ ├── user_modeling.py # User behavior modeling
│ │ │ ├── recommendation.py # Recommendation engine
│ │ │ ├── difficulty_adapter.py # Difficulty adaptation
│ │ │ └── learning_path.py # Learning path generation
│ │ │
│ │ └── utils/ # AI utilities
│ │ ├── **init**.py
│ │ ├── similarity.py # Similarity calculations
│ │ ├── clustering.py # Content clustering
│ │ └── evaluation.py # Model evaluation
│ │
│ ├── utils/ # General utilities
│ │ ├── **init**.py
│ │ ├── helpers.py # Helper functions
│ │ ├── validators.py # Custom validators
│ │ ├── formatters.py # Data formatters
│ │ ├── file_utils.py # File operations
│ │ ├── image_utils.py # Image utilities
│ │ └── cache_utils.py # Caching utilities
│ │
│ ├── tasks/ # Background tasks
│ │ ├── **init**.py
│ │ ├── celery_app.py # Celery configuration
│ │ ├── question_processing.py # Question processing tasks
│ │ ├── analytics_tasks.py # Analytics computation
│ │ ├── notification_tasks.py # Notification tasks
│ │ └── maintenance_tasks.py # Maintenance tasks
│ │
│ └── tests/ # Test files
│ ├── **init**.py
│ ├── conftest.py # Test configuration
│ ├── test_auth.py # Authentication tests
│ ├── test_questions.py # Question tests
│ ├── test_users.py # User tests
│ ├── test_practice.py # Practice tests
│ ├── test_ai.py # AI functionality tests
│ └── test_utils.py # Utility tests
│
├── alembic/ # Database migrations
│ ├── versions/ # Migration files
│ ├── env.py # Alembic environment
│ ├── script.py.mako # Migration template
│ └── alembic.ini # Alembic configuration
│
├── scripts/ # Utility scripts
│ ├── init_db.py # Database initialization
│ ├── seed_data.py # Seed sample data
│ ├── backup_db.py # Database backup
│ ├── process_questions.py # Bulk question processing
│ └── migrate_data.py # Data migration scripts
│
├── requirements/ # Python dependencies
│ ├── base.txt # Base requirements
│ ├── dev.txt # Development requirements
│ ├── prod.txt # Production requirements
│ └── test.txt # Testing requirements
│
├── Dockerfile # Docker configuration
├── docker-compose.yml # Docker compose for development
├── .env.example # Environment variables template
├── .gitignore # Git ignore rules
├── pyproject.toml # Python project configuration
├── README.md # Backend documentation
└── run.py # Application runner

Frontend-File-Structure(React Native):
frontend/
├── src/
│ ├── components/ # Reusable UI components
│ │ ├── common/ # Common components
│ │ │ ├── Button/
│ │ │ │ ├── index.tsx
│ │ │ │ ├── Button.tsx
│ │ │ │ └── Button.styles.ts
│ │ │ ├── Input/
│ │ │ │ ├── index.tsx
│ │ │ │ ├── Input.tsx
│ │ │ │ └── Input.styles.ts
│ │ │ ├── Loading/
│ │ │ │ ├── index.tsx
│ │ │ │ ├── Loading.tsx
│ │ │ │ └── Loading.styles.ts
│ │ │ ├── Modal/
│ │ │ ├── Card/
│ │ │ ├── Header/
│ │ │ ├── Footer/
│ │ │ └── index.ts # Component exports
│ │ │
│ │ ├── forms/ # Form components
│ │ │ ├── LoginForm/
│ │ │ ├── RegisterForm/
│ │ │ ├── ProfileForm/
│ │ │ ├── QuestionForm/
│ │ │ └── index.ts
│ │ │
│ │ ├── question/ # Question-related components
│ │ │ ├── QuestionCard/
│ │ │ ├── QuestionList/
│ │ │ ├── QuestionDetail/
│ │ │ ├── AnswerInput/
│ │ │ ├── ExplanationView/
│ │ │ ├── HintSystem/
│ │ │ └── index.ts
│ │ │
│ │ ├── practice/ # Practice session components
│ │ │ ├── PracticeSession/
│ │ │ ├── TimerComponent/
│ │ │ ├── ProgressBar/
│ │ │ ├── ResultsView/
│ │ │ └── index.ts
│ │ │
│ │ ├── analytics/ # Analytics components
│ │ │ ├── PerformanceChart/
│ │ │ ├── SubjectAnalytics/
│ │ │ ├── ProgressChart/
│ │ │ ├── StatCard/
│ │ │ └── index.ts
│ │ │
│ │ └── navigation/ # Navigation components
│ │ ├── TabBar/
│ │ ├── DrawerContent/
│ │ └── index.ts
│ │
│ ├── screens/ # Screen components
│ │ ├── auth/ # Authentication screens
│ │ │ ├── LoginScreen.tsx
│ │ │ ├── RegisterScreen.tsx
│ │ │ ├── ForgotPasswordScreen.tsx
│ │ │ ├── OnboardingScreen.tsx
│ │ │ └── index.ts
│ │ │
│ │ ├── home/ # Home screens
│ │ │ ├── HomeScreen.tsx
│ │ │ ├── DashboardScreen.tsx
│ │ │ └── index.ts
│ │ │
│ │ ├── practice/ # Practice screens
│ │ │ ├── PracticeHomeScreen.tsx
│ │ │ ├── QuestionBrowserScreen.tsx
│ │ │ ├── PracticeSessionScreen.tsx
│ │ │ ├── ResultsScreen.tsx
│ │ │ ├── BookmarksScreen.tsx
│ │ │ └── index.ts
│ │ │
│ │ ├── subjects/ # Subject screens
│ │ │ ├── SubjectListScreen.tsx
│ │ │ ├── SubjectDetailScreen.tsx
│ │ │ ├── TopicListScreen.tsx
│ │ │ └── index.ts
│ │ │
│ │ ├── analytics/ # Analytics screens
│ │ │ ├── AnalyticsScreen.tsx
│ │ │ ├── PerformanceScreen.tsx
│ │ │ ├── ProgressScreen.tsx
│ │ │ └── index.ts
│ │ │
│ │ ├── profile/ # Profile screens
│ │ │ ├── ProfileScreen.tsx
│ │ │ ├── SettingsScreen.tsx
│ │ │ ├── PreferencesScreen.tsx
│ │ │ ├── HelpScreen.tsx
│ │ │ └── index.ts
│ │ │
│ │ └── search/ # Search screens
│ │ ├── SearchScreen.tsx
│ │ ├── FilterScreen.tsx
│ │ └── index.ts
│ │
│ ├── navigation/ # Navigation configuration
│ │ ├── AppNavigator.tsx # Main navigation
│ │ ├── AuthNavigator.tsx # Auth navigation
│ │ ├── MainNavigator.tsx # Main app navigation
│ │ ├── TabNavigator.tsx # Bottom tab navigation
│ │ ├── StackNavigator.tsx # Stack navigation
│ │ └── index.ts
│ │
│ ├── store/ # Redux store
│ │ ├── index.ts # Store configuration
│ │ ├── rootReducer.ts # Root reducer
│ │ ├── middleware.ts # Custom middleware
│ │ │
│ │ ├── slices/ # Redux slices
│ │ │ ├── authSlice.ts # Authentication state
│ │ │ ├── userSlice.ts # User state
│ │ │ ├── questionSlice.ts # Question state
│ │ │ ├── practiceSlice.ts # Practice state
│ │ │ ├── analyticsSlice.ts # Analytics state
│ │ │ ├── searchSlice.ts # Search state
│ │ │ └── index.ts
│ │ │
│ │ └── api/ # RTK Query API
│ │ ├── baseApi.ts # Base API configuration
│ │ ├── authApi.ts # Authentication API
│ │ ├── userApi.ts # User API
│ │ ├── questionApi.ts # Question API
│ │ ├── practiceApi.ts # Practice API
│ │ ├── analyticsApi.ts # Analytics API
│ │ └── index.ts
│ │
│ ├── hooks/ # Custom React hooks
│ │ ├── useAuth.ts # Authentication hook
│ │ ├── useLocalStorage.ts # Local storage hook
│ │ ├── useNetworkStatus.ts # Network status hook
│ │ ├── usePracticeSession.ts # Practice session hook
│ │ ├── useAnalytics.ts # Analytics hook
│ │ ├── useDebounce.ts # Debounce hook
│ │ ├── usePermissions.ts # Permissions hook
│ │ └── index.ts
│ │
│ ├── services/ # Service layer
│ │ ├── api/ # API services
│ │ │ ├── client.ts # API client configuration
│ │ │ ├── auth.ts # Auth API calls
│ │ │ ├── questions.ts # Question API calls
│ │ │ ├── practice.ts # Practice API calls
│ │ │ ├── analytics.ts # Analytics API calls
│ │ │ └── index.ts
│ │ │
│ │ ├── storage/ # Storage services
│ │ │ ├── asyncStorage.ts # AsyncStorage wrapper
│ │ │ ├── secureStorage.ts # Secure storage
│ │ │ ├── cache.ts # Cache management
│ │ │ └── index.ts
│ │ │
│ │ ├── offline/ # Offline functionality
│ │ │ ├── offlineManager.ts # Offline state management
│ │ │ ├── syncManager.ts # Data synchronization
│ │ │ └── index.ts
│ │ │
│ │ └── notifications/ # Notification services
│ │ ├── pushNotifications.ts # Push notifications
│ │ ├── localNotifications.ts# Local notifications
│ │ └── index.ts
│ │
│ ├── utils/ # Utility functions
│ │ ├── constants.ts # App constants
│ │ ├── helpers.ts # Helper functions
│ │ ├── validators.ts # Validation functions
│ │ ├── formatters.ts # Data formatters
│ │ ├── permissions.ts # Permission utilities
│ │ ├── analytics.ts # Analytics utilities
│ │ ├── errorHandler.ts # Error handling
│ │ └── index.ts
│ │
│ ├── styles/ # Global styles
│ │ ├── colors.ts # Color palette
│ │ ├── typography.ts # Typography styles
│ │ ├── spacing.ts # Spacing constants
│ │ ├── dimensions.ts # Screen dimensions
│ │ ├── globalStyles.ts # Global styles
│ │ └── index.ts
│ │
│ ├── types/ # TypeScript types
│ │ ├── auth.ts # Authentication types
│ │ ├── user.ts # User types
│ │ ├── question.ts # Question types
│ │ ├── practice.ts # Practice types
│ │ ├── analytics.ts # Analytics types
│ │ ├── navigation.ts # Navigation types
│ │ ├── api.ts # API types
│ │ └── index.ts
│ │
│ ├── assets/ # Static assets
│ │ ├── images/ # Image assets
│ │ │ ├── icons/ # App icons
│ │ │ ├── illustrations/ # Illustrations
│ │ │ └── backgrounds/ # Background images
│ │ ├── fonts/ # Custom fonts
│ │ └── data/ # Static data files
│ │
│ ├── config/ # Configuration files
│ │ ├── env.ts # Environment configuration
│ │ ├── api.ts # API configuration
│ │ ├── notifications.ts # Notification configuration
│ │ └── index.ts
│ │
│ └── **tests**/ # Test files
│ ├── components/ # Component tests
│ ├── screens/ # Screen tests
│ ├── hooks/ # Hook tests
│ ├── services/ # Service tests
│ ├── utils/ # Utility tests
│ └── **mocks**/ # Mock files
│
├── android/ # Android specific files
│ ├── app/
│ │ ├── src/
│ │ │ └── main/
│ │ │ ├── java/
│ │ │ ├── res/
│ │ │ └── AndroidManifest.xml
│ │ ├── build.gradle
│ │ └── proguard-rules.pro
│ ├── gradle/
│ ├── build.gradle
│ ├── settings.gradle
│ └── gradle.properties
│
├── ios/ # iOS specific files
│ ├── PastQuestionsApp/
│ │ ├── AppDelegate.h
│ │ ├── AppDelegate.mm
│ │ ├── Info.plist
│ │ └── main.m
│ ├── PastQuestionsApp.xcodeproj/
│ ├── PastQuestionsApp.xcworkspace/
│ └── Podfile
│
├── .expo/ # Expo configuration (if using Expo)
├── metro.config.js # Metro bundler configuration
├── babel.config.js # Babel configuration
├── tsconfig.json # TypeScript configuration
├── jest.config.js # Jest testing configuration
├── .eslintrc.js # ESLint configuration
├── .prettierrc # Prettier configuration
├── package.json # Node.js dependencies
├── yarn.lock # Yarn lock file
├── .gitignore # Git ignore rules
└── README.md # Frontend documentation
