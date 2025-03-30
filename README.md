# Quiz Master

A Flask-based e-learning platform that facilitates quiz management and assessment across multiple subjects.
![Screenshot 2025-03-30 111503](https://github.com/user-attachments/assets/28422fba-2c7a-4292-971a-8f17f97a5b59)
![Screenshot 2025-03-30 111517](https://github.com/user-attachments/assets/428e998f-03a2-46c3-853e-2b6420956b8c)
![Screenshot 2025-03-30 111734](https://github.com/user-attachments/assets/257e1c90-2750-4b03-9428-02cf3b0fe6b2)
![Screenshot 2025-03-30 111751](https://github.com/user-attachments/assets/dc8715b0-16e2-43c9-bc70-1f016e274684)


## Project Overview

Quiz Master is a web application that enables administrators to create and manage quizzes while allowing users to participate in timed assessments. The platform follows a hierarchical structure: Subjects → Chapters → Quizzes → Questions.

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
## Contributors:
### Veditha R 23f3004007
