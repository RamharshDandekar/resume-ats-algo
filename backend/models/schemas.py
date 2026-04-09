from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Education(BaseModel):
    """Education entry for a candidate"""
    degree: str
    institution: str
    cgpa: Optional[float] = None
    graduation_year: Optional[int] = None

class Experience(BaseModel):
    """Experience entry for a candidate"""
    role: str
    company: str
    duration_months: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class CandidateProfile(BaseModel):
    """Structured candidate profile extracted from resume"""
    candidate_id: str = Field(default_factory=lambda: f"c_{datetime.now().timestamp()}")
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    education: List[Education] = []
    experience: List[Experience] = []
    skills: List[str] = []
    raw_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class JobRequirement(BaseModel):
    """Job requirement extracted from JD"""
    required_skills: List[str] = []
    min_years_experience: int = 0
    education_level: Optional[str] = None
    additional_requirements: Optional[str] = None

class JobDescription(BaseModel):
    """Job description model"""
    job_id: str = Field(default_factory=lambda: f"j_{datetime.now().timestamp()}")
    title: str
    company: Optional[str] = None
    description: str
    requirements: JobRequirement
    created_at: datetime = Field(default_factory=datetime.now)

class MatchScore(BaseModel):
    """Detailed match score breakdown"""
    candidate_id: str
    job_id: str
    skill_match_score: float  # 0-100
    experience_match_score: float  # 0-100
    education_match_score: float  # 0-100
    overall_score: float  # Weighted average
    matched_skills: List[str]
    missing_skills: List[str]
    created_at: datetime = Field(default_factory=datetime.now)

class InterviewSlot(BaseModel):
    """Interview slot for scheduling"""
    slot_id: str = Field(default_factory=lambda: f"slot_{datetime.now().timestamp()}")
    candidate_id: str
    job_id: str
    start_time: str  # ISO format
    end_time: str  # ISO format
    duration_minutes: int = 45
    status: str = "scheduled"  # scheduled, completed, cancelled

class CandidateRanking(BaseModel):
    """Ranked candidate for interview selection"""
    rank: int
    candidate_id: str
    candidate_name: str
    overall_score: float
    skill_weight: float = 0.6
    experience_weight: float = 0.3
    education_weight: float = 0.1
