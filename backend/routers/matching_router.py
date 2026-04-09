from fastapi import APIRouter, HTTPException
from bson import ObjectId

from db import mongo_manager
from models import MatchScore
from core import calculate_skill_match_score

router = APIRouter()


@router.post("/calculate-score", response_model=dict)
async def calculate_match_score(candidate_id: str, job_id: str):
    """
    Calculate match score between a candidate and a job using LCS algorithm.
    
    Query parameters:
    - **candidate_id**: MongoDB object ID of the candidate
    - **job_id**: MongoDB object ID of the job
    
    Returns:
    - Skill match score (LCS-based)
    - Experience match score
    - Education match score
    - Overall weighted score
    """
    try:
        # Fetch candidate
        candidates_col = mongo_manager.get_collection("candidates")
        candidate = candidates_col.find_one({"_id": ObjectId(candidate_id)})
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Fetch job
        jobs_col = mongo_manager.get_collection("jobs")
        job = jobs_col.find_one({"_id": ObjectId(job_id)})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Extract required data
        candidate_skills = candidate.get("skills", [])
        required_skills = job.get("requirements", {}).get("required_skills", [])
        min_experience = job.get("requirements", {}).get("min_years_experience", 0)
        
        # Calculate skill match score using LCS
        skill_score, matched_skills, missing_skills = calculate_skill_match_score(
            candidate_skills,
            required_skills
        )
        
        # Calculate experience match score
        candidate_experience = candidate.get("experience", [])
        total_months = sum(exp.get("duration_months", 0) for exp in candidate_experience)
        total_years = total_months / 12
        experience_score = min((total_years / max(min_experience, 1)) * 100, 100)
        
        # Calculate education match score
        candidate_education = candidate.get("education", [])
        education_score = 50 if len(candidate_education) > 0 else 0
        for edu in candidate_education:
            if "master" in edu.get("degree", "").lower():
                education_score = 100
                break
            elif "bachelor" in edu.get("degree", "").lower():
                education_score = 75
        
        # Calculate overall score (weighted)
        overall_score = (
            skill_score * 0.6 +
            experience_score * 0.3 +
            education_score * 0.1
        )
        
        # Create match score object
        match_score = MatchScore(
            candidate_id=candidate_id,
            job_id=job_id,
            skill_match_score=round(skill_score, 2),
            experience_match_score=round(experience_score, 2),
            education_match_score=round(education_score, 2),
            overall_score=round(overall_score, 2),
            matched_skills=matched_skills,
            missing_skills=missing_skills
        )
        
        # Save to MongoDB
        matches_col = mongo_manager.get_collection("matches")
        match_dict = match_score.model_dump()
        matches_col.insert_one(match_dict)
        
        return {
            "status": "success",
            "candidate_id": candidate_id,
            "job_id": job_id,
            "skill_match_score": match_score.skill_match_score,
            "experience_match_score": match_score.experience_match_score,
            "education_match_score": match_score.education_match_score,
            "overall_score": match_score.overall_score,
            "matched_skills": match_score.matched_skills,
            "missing_skills": match_score.missing_skills
        }
    
    except ObjectId as e:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/job/{job_id}", response_model=dict)
async def get_all_matches_for_job(job_id: str, min_score: float = 0):
    """
    Get all candidate match scores for a specific job, sorted by overall score.
    
    - **job_id**: MongoDB object ID of the job
    - **min_score**: Minimum overall score to include (default: 0)
    """
    try:
        matches_col = mongo_manager.get_collection("matches")
        candidates_col = mongo_manager.get_collection("candidates")
        
        # Find all matches for this job
        matches = list(matches_col.find(
            {
                "job_id": job_id,
                "overall_score": {"$gte": min_score}
            }
        ).sort("overall_score", -1))
        
        # Enrich with candidate names
        for match in matches:
            candidate = candidates_col.find_one({"_id": ObjectId(match["candidate_id"])})
            if candidate:
                match["candidate_name"] = candidate.get("name", "Unknown")
            match['_id'] = str(match['_id'])
        
        return {
            "status": "success",
            "job_id": job_id,
            "total_matches": len(matches),
            "min_score": min_score,
            "matches": matches
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/candidate/{candidate_id}", response_model=dict)
async def get_all_matches_for_candidate(candidate_id: str, min_score: float = 0):
    """
    Get all job match scores for a specific candidate.
    
    - **candidate_id**: MongoDB object ID of the candidate
    - **min_score**: Minimum overall score to include (default: 0)
    """
    try:
        matches_col = mongo_manager.get_collection("matches")
        jobs_col = mongo_manager.get_collection("jobs")
        
        # Find all matches for this candidate
        matches = list(matches_col.find(
            {
                "candidate_id": candidate_id,
                "overall_score": {"$gte": min_score}
            }
        ).sort("overall_score", -1))
        
        # Enrich with job titles
        for match in matches:
            job = jobs_col.find_one({"_id": ObjectId(match["job_id"])})
            if job:
                match["job_title"] = job.get("title", "Unknown")
            match['_id'] = str(match['_id'])
        
        return {
            "status": "success",
            "candidate_id": candidate_id,
            "total_matches": len(matches),
            "min_score": min_score,
            "matches": matches
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-candidates/{job_id}", response_model=dict)
async def get_top_candidates(job_id: str, limit: int = 10):
    """
    Get top matched candidates for a job.
    
    - **job_id**: MongoDB object ID of the job
    - **limit**: Number of top candidates to return (default: 10)
    """
    try:
        matches_col = mongo_manager.get_collection("matches")
        candidates_col = mongo_manager.get_collection("candidates")
        
        # Get top candidates
        matches = list(matches_col.find({"job_id": job_id})
                      .sort("overall_score", -1)
                      .limit(limit))
        
        # Enrich with candidate details
        for match in matches:
            candidate = candidates_col.find_one({"_id": ObjectId(match["candidate_id"])})
            if candidate:
                match["candidate_name"] = candidate.get("name", "Unknown")
                match["candidate_email"] = candidate.get("email", "N/A")
            match['_id'] = str(match['_id'])
        
        return {
            "status": "success",
            "job_id": job_id,
            "limit": limit,
            "top_candidates": matches
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
