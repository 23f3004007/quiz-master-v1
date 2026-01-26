# Quiz Master

A Flask-based e-learning platform that facilitates quiz management and assessment across multiple subjects.
![Screenshot 2025-03-30 111503](https://github.com/user-attachments/assets/28422fba-2c7a-4292-971a-8f17f97a5b59)
![Screenshot 2025-03-30 111517](https://github.com/user-attachments/assets/428e998f-03a2-46c3-853e-2b6420956b8c)
![Screenshot 2025-03-30 111734](https://github.com/user-attachments/assets/257e1c90-2750-4b03-9428-02cf3b0fe6b2)
![Screenshot 2025-03-30 111751](https://github.com/user-attachments/assets/dc8715b0-16e2-43c9-bc70-1f016e274684)


## Project Overview

Quiz Master is a web application that enables administrators to create and manage quizzes while allowing users to participate in timed assessments. The platform follows a hierarchical structure: Subjects → Chapters → Quizzes → Questions.

## Vision Document

### Project Name & Overview

**Quiz Master** – A comprehensive Flask-based e-learning assessment platform designed to streamline quiz creation, management, and participation across multiple subjects and chapters.

The platform provides administrators with powerful tools to organize subjects hierarchically (Subject → Chapter → Quiz → Question) and enables users to engage in timed, proctored assessments with real-time scoring and performance tracking.

---

### Problem It Solves

Educational institutions and online learning platforms face several challenges:

1. **Manual Quiz Management** – Creating, organizing, and managing quizzes across multiple subjects and chapters is time-consuming and error-prone.
2. **Lack of Standardization** – No unified system for administering assessments, leading to inconsistent scoring and tracking.
3. **Limited Analytics** – Educators lack real-time insights into student performance and learning patterns.
4. **Assessment Integrity** – Difficulty in preventing cheating or ensuring fair assessment with timed, synchronized quizzes.
5. **User Experience Gaps** – Students need an intuitive interface to discover quizzes, track their progress, and understand their strengths and weaknesses.

**Quiz Master solves these by providing:**
- A centralized platform for quiz creation and hierarchical organization
- Automated scoring and real-time timer synchronization
- Comprehensive performance analytics dashboards
- Role-based access control for secure administration
- User-friendly interface for seamless quiz participation

---

### Target Users (Personas)

#### Persona 1: Admin / Educator
- **Name:** Prof. Sharma
- **Role:** Subject Matter Expert, Quiz Administrator
- **Goals:**
  - Create and organize quizzes efficiently across multiple subjects
  - Track student performance and identify learning gaps
  - Schedule quizzes and manage user access
  - Analyze class-wide performance metrics
- **Pain Points:** Manual quiz creation, no real-time performance insights, difficulty scaling
- **Usage Pattern:** Creates quizzes quarterly, reviews analytics weekly

#### Persona 2: Student / Quiz Taker
- **Name:** Rahul
- **Role:** Learner, Quiz Participant
- **Goals:**
  - Find and attempt quizzes relevant to their coursework
  - Get immediate feedback on quiz performance
  - Track learning progress over time
  - Compare performance with personalized insights
- **Pain Points:** Quiz scattered across platforms, no centralized progress tracking, unclear scoring criteria
- **Usage Pattern:** Attempts quizzes daily, reviews performance weekly

#### Persona 3: Institution Administrator
- **Name:** Dr. Patel
- **Role:** Educational Institution Manager
- **Goals:**
  - Deploy and manage the platform for the entire organization
  - Monitor institutional performance and student engagement
  - Ensure data security and system uptime
  - Scale the platform as enrollment grows
- **Pain Points:** Platform fragmentation, manual user management, data silos
- **Usage Pattern:** Monitors dashboards monthly, manages users as needed

---

### Vision Statement

**To empower educators and learners with an intuitive, scalable, and secure assessment platform that transforms how quizzes are created, delivered, and analyzed – making education more data-driven, engaging, and equitable.**

---

### Key Features / Goals

#### Phase 1 (Current - MVP)
- ✅ **Quiz Hierarchy Management** – Organize quizzes by Subject → Chapter → Quiz → Question
- ✅ **Role-Based Access Control** – Admin and User roles with secure authentication
- ✅ **Real-Time Quiz Timer** – Synchronized server-client timer to prevent cheating
- ✅ **Automated Scoring** – Instant score calculation with atomic database updates
- ✅ **Performance Dashboard** – Analytics and visualizations for admins (Chart.js)
- ✅ **Quiz Scheduling** – Admins can schedule quizzes with timezone support
- ✅ **User Management** – CRUD operations for user accounts and roles

#### Phase 2 (Future Enhancements)
- **Question Bank & Randomization** – Randomize questions per attempt, question difficulty levels
- **Detailed Performance Analytics** – Per-question analysis, time-spent metrics, learning curves
- **Exam Proctoring Features** – Webcam monitoring, screen-share detection, cheating alerts
- **API Expansion** – Public REST API for third-party integrations (LMS, analytics tools)
- **Mobile App** – Native mobile client for on-the-go quiz participation
- **AI-Powered Recommendations** – Suggest quizzes based on performance and learning patterns
- **Bulk Operations** – Import questions via CSV, export results to Excel/PDF

#### Phase 3 (Long-Term Vision)
- **Multi-Tenancy** – Support multiple institutions on a single platform
- **Advanced Proctoring** – AI-based behavior analysis, biometric authentication
- **Adaptive Learning Paths** – Personalized quiz sequences based on performance
- **Gamification** – Leaderboards, badges, achievement tracking
- **Marketplace** – Share quizzes between educators, curated question banks

---

### Success Metrics

#### For Admins / Educators
1. **Quiz Creation Efficiency** – Measure time to create and deploy a quiz (Target: < 10 minutes)
2. **Student Engagement** – Track quiz participation rates (Target: ≥ 80% student participation)
3. **Platform Adoption** – Monitor active educators using the platform monthly (Target: ≥ 95%)
4. **Analytics Utilization** – % of educators accessing performance dashboards (Target: ≥ 70%)

#### For Students / Users
1. **Quiz Completion Rate** – % of assigned quizzes completed (Target: ≥ 85%)
2. **Time to First Quiz** – Time from account creation to first quiz attempt (Target: ≤ 2 days)
3. **User Satisfaction** – NPS or satisfaction survey score (Target: ≥ 8/10)
4. **Performance Improvement** – Track score progression over multiple quiz attempts (Target: 15% avg. improvement)

#### For the Platform
1. **System Availability** – Uptime percentage (Target: ≥ 99.5%)
2. **Response Time** – Page load and API response latency (Target: < 500ms avg.)
3. **Data Integrity** – Zero unintended data loss incidents over 6 months
4. **Scalability** – Support ≥ 5,000 concurrent users without performance degradation
5. **Security** – Zero critical vulnerabilities in annual security audit

---

### Assumptions & Constraints

#### Assumptions
1. **User Base** – Assuming 500–2,000 initial users (students + educators) with expected 20% monthly growth.
2. **Internet Connectivity** – Users have reliable internet access; offline functionality not prioritized.
3. **Device Types** – Primary access via desktop/laptop browsers; mobile responsiveness is secondary.
4. **Assessment Context** – Designed for formative and low-stakes summative assessments; not for high-stakes standardized testing initially.
5. **User Trust** – Users assume the platform is reasonably secure; advanced proctoring not enforced without opt-in.
6. **Question Quality** – Educators are responsible for question quality; AI-based validation not yet implemented.

#### Constraints

##### Technical
- **Technology Stack** – Flask (backend), SQLite (local dev), Jinja2 + Bootstrap (frontend)
- **Scalability Limit** – Current SQLite architecture supports up to 10,000 concurrent connections; beyond that requires migration to PostgreSQL/MySQL
- **Browser Support** – Target modern browsers (Chrome, Edge, Firefox); IE11 not supported
- **Deployment** – Deployed on Vercel (frontend) and standard VM/container (backend); no serverless auto-scaling currently

##### Resource
- **Development Team** – Single developer (Veditha R) for current phase
- **Budget** – Open-source tech stack; hosting costs minimal (free tier for MVP)
- **Timeline** – MVP completed; Phase 2 features planned for 2–3 month iterations

##### Regulatory & Compliance
- **Data Privacy** – Must comply with basic data protection; GDPR/CCPA not prioritized for initial MVP
- **Accessibility** – WCAG 2.1 AA compliance targeted but not fully audited
- **Exam Integrity** – Basic cheating prevention (timer sync, no copy-paste); advanced proctoring requires legal/privacy framework

##### User Experience
- **Training Overhead** – Platform designed for minimal onboarding; no video tutorials or live support initially
- **Customization** – Limited theming/white-label support; standardized UI/UX
- **Localization** – English-only initially; multi-language support planned for Phase 2

---


## Architecture

### Backend
- Flask framework for routing and business logic
- SQLAlchemy ORM for database management
- SQLite database for data persistence
- Werkzeug for security features

### Frontend
- Jinja2 templating engine
- Bootstrap for responsive design
- Chart.js for data visualization
- Custom CSS for styling

## Database Schema
![DB Schema diagram](https://github.com/user-attachments/assets/8695d2e5-c77b-47a4-9806-dbb88f4c90a1)
## Features

### Authentication System
- Role-based access control (Admin/User)
- Secure password hashing
- Session management

### Admin Features
- Subject Management (CRUD operations)
- Chapter Management
- Quiz Creation and Scheduling
- Question Bank Management
- User Management
- Performance Analytics Dashboard

### User Features
- Quiz Participation
- Real-time Quiz Timer
- Score Tracking
- Performance History
- Subject/Quiz Search

### API Endpoints
- `/api/subjects`: Get all subjects
- `/api/chapters/<subject_id>`: Get chapters by subject
- `/api/quizzes/<chapter_id>`: Get quizzes by chapter
- `/api/scores/<user_id>`: Get user scores

## Issues faced and Solutions implemented

### 1. Quiz Timer Synchronization
**Issue:** Timer desynchronization between client and server.
**Solution:** Implemented server-side timestamp validation and client-side JavaScript timer

### 2. Concurrent Quiz Attempts
**Issue:** Multiple submissions from same user
**Solution:** Added session-based attempt tracking and server-side validation

### 3. Quiz Scheduling
**Issue:** Timezone inconsistencies
**Solution:** Standardized to UTC storage with IST conversion for display

### 4. Score Calculation
**Issue:** Inconsistent score tracking
**Solution:** Implemented atomic score updates and JSON-based answer storage

## Setup Instructions

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Initialize the database:
```bash
python app.py
```
4. Access the application:
- URL: http://localhost:5000
- Default Admin Credentials:
  - Email: admin@example.com
  - Password: admin_password

## Branching Strategy
This project follows a GitHub Flow style workflow:
- main is the stable, production-ready branch.
- New work is done on short-lived feature branches created from main

### Typical workflow:
1. Update local main:
```bash
git checkout main
git pull origin main
```
2. Create a feature branch from main:
```bash
git checkout -b feature/docker-setup
```
3. Commit and push changes to the feature branch:
```bash
git add .
git commit -m "Describe your change"
git push -u origin feature/docker-setup
```
4. Open a Pull Request from the feature branch into main, review, test, and then merge.

5. After merging, delete the feature branch to keep the branch list clean.

## Quick Start - Local Development (Docker)
### Prerequisites
- Docker Desktop installed and running
- Git Installed
## Steps
1. Clone the repository:
```bash
git clone https://github.com/23f3004007/quiz-master-v1.git
cd quiz-master-v1
```
2. Build Docker image:
```bash
docker build -t quiz-master-v1 .
```
3. Run the container
```bash
docker run -p 5000:5000 quiz-master-v1
```
4.Access the application in your browser.
## Project Structure
```bash
quiz-master-v1/
├── app.py
├── templates/
│   ├── admin/
│   └── user/
├── static/
│   ├── css/
│   └── js/
├── instance/
│   └── quiz_master_database.sqlite3
├── api.yaml
└──requirements.txt
```

## Local Development Tools
- **Python 3.x** – Core runtime for the Flask application.
- **Flask, SQLAlchemy, SQLite** – Backend web framework, ORM, and database.
- **Docker / Docker Desktop** – Containerized local development and running the app in an isolated environment.
- **VS Code** – Primary code editor for development and debugging.
- **Web browser (Chrome/Edge)** – Used to test the web UI at `http://localhost:5000`.
## Contributors:
### Veditha R 23f3004007