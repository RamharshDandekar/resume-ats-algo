# IntelliHire Backend - AI-Powered Resume Screening & Hiring System

## Project Overview

IntelliHire is a professional HR tech platform that automates resume screening, candidate matching, and interview scheduling using advanced algorithms and NLP techniques.

### Core Features

✅ **Resume Analyzer** - Extract structured data from PDFs and DOCX files
✅ **Job Description Matching** - Calculate match scores using LCS algorithm
✅ **Candidate Ranking** - Select top candidates using 0/1 Knapsack algorithm
✅ **Interview Scheduler** - Generate conflict-free schedules using Activity Selection
✅ **Smart Dashboard API** - REST API for frontend integration

---

## Architecture & Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB (NoSQL)
- **File Parsing**: PyPDF2, python-docx
- **NLP**: spaCy integration for future expansion
- **Testing**: pytest with asyncio support

### DAA Algorithms Implemented

| Algorithm | Feature | Complexity | Use Case |
|-----------|---------|-----------|----------|
| **Longest Common Subsequence (LCS)** | Skill Matching | O(m*n) | Measures skill overlap between resume and job description |
| **0/1 Knapsack (Greedy)** | Candidate Ranking | O(n log n) | Selects top N candidates for limited interview slots |
| **Activity Selection (Greedy)** | Interview Scheduling | O(n log n) | Creates conflict-free interview schedule |

---

## Project Structure

```
backend/
├── main.py                          # FastAPI entry point
├── requirements.txt                 # Python dependencies
├── pytest.ini                       # pytest configuration
│
├── core/                            # Core algorithms & logic
│   ├── __init__.py
│   ├── skill_matcher.py            # LCS algorithm for skill matching
│   ├── candidate_ranker.py         # Knapsack algorithm
│   ├── interview_scheduler.py      # Activity Selection algorithm
│   └── resume_parser.py            # NLP-based resume parser
│
├── db/                              # Database connection
│   ├── __init__.py
│   └── mongo.py                     # MongoDB manager (singleton)
│
├── models/                          # Pydantic schemas
│   ├── __init__.py
│   └── schemas.py                   # Data models
│
├── routers/                         # API endpoints
│   ├── __init__.py
│   ├── candidates_router.py        # /api/candidates
│   ├── jobs_router.py              # /api/jobs
│   ├── matching_router.py          # /api/matching (LCS)
│   └── scheduler_router.py         # /api/scheduler (Knapsack + Activity Selection)
│
└── tests/                           # Unit tests
    ├── __init__.py
    ├── test_skill_matcher.py       # LCS tests
    ├── test_candidate_ranker.py    # Knapsack tests
    ├── test_interview_scheduler.py # Activity Selection tests
    └── test_resume_parser.py       # Parser tests
```

---

## Setup & Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. MongoDB Setup

Make sure MongoDB is running locally (or update the connection string in `main.py`):

```bash
# On Windows with MongoDB installed
mongod

# On Mac with homebrew
brew services start mongodb-community

# Or use Docker
docker run -d -p 27017:27017 mongo:latest
```

### 3. Run the Backend Server

```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at: `http://localhost:8000`

API Documentation (Swagger UI): `http://localhost:8000/docs`

---

## API Endpoints Reference

### Candidates API (`/api/candidates`)

#### Upload Resume
```http
POST /api/candidates/upload-resume
Content-Type: multipart/form-data

file: <resume_file.pdf or .docx>

Response:
{
  "status": "success",
  "candidate_id": "507f1f77bcf86cd799439011",
  "name": "John Doe",
  "email": "john@example.com",
  "skills_count": 8,
  "education_count": 1,
  "experience_count": 2
}
```

#### List Candidates
```http
GET /api/candidates/list?skip=0&limit=10

Response:
{
  "status": "success",
  "total": 42,
  "skip": 0,
  "limit": 10,
  "candidates": [...]
}
```

#### Get Candidate
```http
GET /api/candidates/{candidate_id}
```

#### Search by Skill
```http
GET /api/candidates/search/by-skill?skill=python
```

#### Delete Candidate
```http
DELETE /api/candidates/{candidate_id}
```

---

### Jobs API (`/api/jobs`)

#### Create Job
```http
POST /api/jobs/create
Content-Type: application/json

{
  "title": "Senior Software Engineer",
  "company": "TechCorp",
  "description": "Looking for...",
  "required_skills": ["python", "react", "docker"],
  "min_years_experience": 3,
  "education_level": "B.Tech/Bachelor"
}
```

#### List Jobs
```http
GET /api/jobs/list?skip=0&limit=10
```

#### Get Job
```http
GET /api/jobs/{job_id}
```

#### Update Job
```http
PUT /api/jobs/{job_id}
```

#### Delete Job
```http
DELETE /api/jobs/{job_id}
```

---

### Skill Matching API (`/api/matching`) - **LCS Algorithm**

#### Calculate Match Score
```http
POST /api/matching/calculate-score?candidate_id={id}&job_id={id}

Response:
{
  "status": "success",
  "candidate_id": "507f1f77bcf86cd799439011",
  "job_id": "507f1f77bcf86cd799439012",
  "skill_match_score": 85.5,
  "experience_match_score": 90.0,
  "education_match_score": 75.0,
  "overall_score": 84.25,
  "matched_skills": ["python", "react", "docker"],
  "missing_skills": ["kubernetes"]
}
```

#### Get Top Candidates for Job
```http
GET /api/matching/top-candidates/{job_id}?limit=10
```

#### Get All Matches for Job
```http
GET /api/matching/job/{job_id}?min_score=70
```

---

### Interview Scheduler API (`/api/scheduler`)

#### Rank Candidates - **0/1 Knapsack**
```http
POST /api/scheduler/rank-candidates/{job_id}?num_interviews=10

Optional JSON body:
{
  "weights": {
    "skill": 0.6,
    "experience": 0.3,
    "education": 0.1
  }
}

Response:
{
  "status": "success",
  "job_id": "507f1f77bcf86cd799439011",
  "total_candidates_ranked": 10,
  "interview_slots": 10,
  "ranked_candidates": [
    {
      "rank": 1,
      "candidate_id": "id",
      "name": "Alice",
      "overall_score": 92.5
    },
    ...
  ]
}
```

#### Schedule Interviews - **Activity Selection**
```http
POST /api/scheduler/schedule-interviews/{job_id}
?scheduled_date=2024-04-25&num_interviews=10&start_hour=9&end_hour=17

Response:
{
  "status": "success",
  "job_id": "507f1f77bcf86cd799439011",
  "scheduled_date": "2024-04-25",
  "total_interviews": 10,
  "scheduled_count": 9,
  "schedule": [
    {
      "rank": 1,
      "candidate_id": "id",
      "candidate_name": "Alice",
      "start_time": "2024-04-25T09:00:00",
      "end_time": "2024-04-25T09:45:00"
    },
    ...
  ]
}
```

#### Get Schedule
```http
GET /api/scheduler/get-schedule/{job_id}
```

#### Get Ranking
```http
GET /api/scheduler/get-ranking/{job_id}
```

---

## Running Tests

### Run all tests
```bash
pytest backend/tests/ -v
```

### Run specific test file
```bash
pytest backend/tests/test_skill_matcher.py -v
```

### Run specific test class
```bash
pytest backend/tests/test_skill_matcher.py::TestLCS -v
```

### Run with coverage
```bash
pytest backend/tests/ --cov=backend --cov-report=html
```

---

## Algorithm Explanations

### 1. Longest Common Subsequence (LCS) - Skill Matching

**Problem**: How similar are the candidate's skills to the job requirements?

**Solution**:
1. Extract skills from both candidate resume and job description
2. Sort skills alphabetically for canonical comparison
3. Apply LCS algorithm to find common subsequence
4. Calculate match score as: `(LCS length / Job skills length) × 100`

**Example**:
```
Candidate Skills: Docker, FastAPI, MongoDB, Python, React
Job Required:    Python, React, Docker, Kubernetes

Canonical strings:
- Candidate: Docker,FastAPI,MongoDB,Python,React
- Job:       Docker,Kubernetes,Python,React

LCS: Docker,Python,React (length = 3)
Match Score = (3 / 4) × 100 = 75%
```

### 2. 0/1 Knapsack (Greedy) - Candidate Ranking

**Problem**: Select the top N candidates for limited interview slots to maximize value

**Solution**:
1. Calculate weighted score for each candidate:
   - `Value = 0.6 × Skill Score + 0.3 × Experience + 0.1 × Education`
2. Sort candidates by value (descending)
3. Select top N candidates
4. This greedy approach is optimal when all weights (interview slots) are equal

**Example**:
```
Candidates (after scoring):
- Alice: 92.5 ← Select (Rank 1)
- Charlie: 81.0 ← Select (Rank 2)
- Bob: 69.0 ← Select (Rank 3)
- Diana: 55.5 ← Skip (if only 3 slots)
```

### 3. Activity Selection - Interview Scheduling

**Problem**: Schedule maximum non-conflicting interviews in a day

**Solution**:
1. Create list of interview "activities" with start/end times
2. Sort by finish time (earliest finish first)
3. Greedily select interviews that don't conflict
4. This ensures maximum number of interviews scheduled

**Example**:
```
Available Slots: 9 AM - 5 PM (8 hours)
Each interview: 45 minutes

Schedule (greedy by earliest finish):
- 9:00-9:45: Alice ✓
- 10:00-10:45: Bob ✓ (no conflict)
- 11:00-11:45: Charlie ✓ (no conflict)
- 14:00-14:45: Diana ✓ (noon break)
...
Total: 9 interviews scheduled
```

---

## Database Schema (MongoDB)

### Candidates Collection
```json
{
  "_id": ObjectId,
  "candidate_id": "c_timestamp",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "123-456-7890",
  "education": [
    {
      "degree": "B.Tech",
      "institution": "Tech University",
      "cgpa": 8.5
    }
  ],
  "experience": [
    {
      "role": "Software Engineer",
      "company": "TechCorp",
      "duration_months": 24
    }
  ],
  "skills": ["python", "react", "docker"],
  "raw_text": "...",
  "created_at": ISODate
}
```

### Jobs Collection
```json
{
  "_id": ObjectId,
  "job_id": "j_timestamp",
  "title": "Senior Software Engineer",
  "company": "TechCorp",
  "description": "...",
  "requirements": {
    "required_skills": ["python", "react"],
    "min_years_experience": 3,
    "education_level": "B.Tech"
  },
  "created_at": ISODate
}
```

### Matches Collection
```json
{
  "_id": ObjectId,
  "candidate_id": "507f...",
  "job_id": "507f...",
  "skill_match_score": 85.5,
  "experience_match_score": 90.0,
  "education_match_score": 75.0,
  "overall_score": 84.25,
  "matched_skills": ["python", "react"],
  "missing_skills": ["docker"],
  "created_at": ISODate
}
```

---

## Next Steps - Frontend Development

The backend API is complete. Next phase is building the React frontend with:
- Resume upload UI
- Dashboard with candidate cards
- Score visualization (progress bars, charts)
- Advanced filtering and export
- Interview scheduler view

Frontend: `/frontend` directory (React 19 + Tailwind v4)

---

## Troubleshooting

### MongoDB Connection Error
- Ensure MongoDB is running: `mongod`
- Check connection string in `main.py`
- For Docker: `docker ps` to verify container is running

### Tests Failing
- Install all dependencies: `pip install -r requirements.txt`
- Run from project root: `pytest backend/tests/ -v`

### Import Errors
- Ensure you're running from the project root directory
- Check that all `__init__.py` files exist in package folders

---

## Performance Notes

- **LCS Algorithm**: O(m*n) time, best with sorted skill lists
- **Knapsack Greedy**: O(n log n) time, optimal for equal weights
- **Activity Selection**: O(n log n) time for sorting, O(n) for selection
- **Resume Parsing**: ~500ms per file (depends on file size)

---

## Author & Version

**Version**: 1.0.0  
**Last Updated**: April 2024  
**Status**: Backend Complete, Frontend Pending
