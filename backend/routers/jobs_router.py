from fastapi import APIRouter, HTTPException
from typing import List, Optional
from bson import ObjectId

from db import mongo_manager
from models import JobDescription, JobRequirement
from core import ResumeParser

router = APIRouter()


@router.post("/create", response_model=dict)
async def create_job(job_data: dict):
    """
    Create a new job description.
    
    Request body:
    ```json
    {
        "title": "Senior Software Engineer",
        "company": "TechCorp",
        "description": "Looking for...",
        "required_skills": ["python", "react", "docker"],
        "min_years_experience": 3,
        "education_level": "B.Tech/Bachelor"
    }
    ```
    """
    try:
        # Parse required skills from description if not provided
        required_skills = job_data.get("required_skills", [])
        if not required_skills:
            # Try to extract from description
            parsed = ResumeParser.extract_skills(job_data.get("description", ""))
            required_skills = parsed
        
        job = JobDescription(
            title=job_data.get("title"),
            company=job_data.get("company"),
            description=job_data.get("description"),
            requirements=JobRequirement(
                required_skills=required_skills,
                min_years_experience=job_data.get("min_years_experience", 0),
                education_level=job_data.get("education_level")
            )
        )
        
        # Save to MongoDB
        jobs_col = mongo_manager.get_collection("jobs")
        job_dict = job.model_dump()
        result = jobs_col.insert_one(job_dict)
        
        return {
            "status": "success",
            "job_id": str(result.inserted_id),
            "title": job.title,
            "company": job.company,
            "skills_count": len(job.requirements.required_skills)
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating job: {str(e)}")


@router.get("/list", response_model=dict)
async def list_jobs(skip: int = 0, limit: int = 10):
    """
    List all job descriptions with pagination.
    """
    try:
        jobs_col = mongo_manager.get_collection("jobs")
        
        jobs = list(jobs_col.find().skip(skip).limit(limit))
        total = jobs_col.count_documents({})
        
        for job in jobs:
            job['_id'] = str(job['_id'])
        
        return {
            "status": "success",
            "total": total,
            "skip": skip,
            "limit": limit,
            "jobs": jobs
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}", response_model=dict)
async def get_job(job_id: str):
    """
    Get a specific job description by ID.
    """
    try:
        jobs_col = mongo_manager.get_collection("jobs")
        job = jobs_col.find_one({"_id": ObjectId(job_id)})
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job['_id'] = str(job['_id'])
        return {
            "status": "success",
            "job": job
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{job_id}", response_model=dict)
async def update_job(job_id: str, updates: dict):
    """
    Update a job description.
    """
    try:
        jobs_col = mongo_manager.get_collection("jobs")
        result = jobs_col.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": updates}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "status": "success",
            "message": "Job updated successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{job_id}", response_model=dict)
async def delete_job(job_id: str):
    """
    Delete a job description.
    """
    try:
        jobs_col = mongo_manager.get_collection("jobs")
        result = jobs_col.delete_one({"_id": ObjectId(job_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "status": "success",
            "message": "Job deleted successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
