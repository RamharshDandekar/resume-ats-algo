from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId
from typing import List

from db import mongo_manager
from core import (
    select_top_candidates,
    CandidateValue,
    optimize_schedule
)

router = APIRouter()


@router.post("/rank-candidates/{job_id}", response_model=dict)
async def rank_candidates(job_id: str, num_interviews: int = 10, weights: dict = None):
    """
    Rank candidates for a job using 0/1 Knapsack algorithm.
    
    - **job_id**: MongoDB object ID of the job
    - **num_interviews**: Number of interview slots available (knapsack capacity)
    - **weights**: Custom weights for scoring (skill, experience, education)
    
    Returns top candidates sorted by overall score using greedy knapsack selection.
    """
    try:
        if weights is None:
            weights = {"skill": 0.6, "experience": 0.3, "education": 0.1}
        
        matches_col = mongo_manager.get_collection("matches")
        candidates_col = mongo_manager.get_collection("candidates")
        
        # Get all matches for this job
        matches = list(matches_col.find({"job_id": job_id}))
        
        if not matches:
            raise HTTPException(status_code=404, detail="No matches found for this job")
        
        # Create CandidateValue objects
        candidate_values = []
        for match in matches:
            candidate = candidates_col.find_one({"_id": ObjectId(match["candidate_id"])})
            if candidate:
                cv = CandidateValue(
                    candidate_id=match["candidate_id"],
                    name=candidate.get("name", "Unknown"),
                    skill_score=match.get("skill_match_score", 0),
                    experience_score=match.get("experience_match_score", 0),
                    education_score=match.get("education_match_score", 0),
                    skill_weight=weights.get("skill", 0.6),
                    experience_weight=weights.get("experience", 0.3),
                    education_weight=weights.get("education", 0.1)
                )
                candidate_values.append(cv)
        
        # Select top candidates using Knapsack greedy approach
        selected = select_top_candidates(candidate_values, num_interviews)
        
        # Format results
        ranked_candidates = [
            {
                "rank": rank,
                "candidate_id": cv.candidate_id,
                "name": cv.name,
                "skill_score": cv.skill_score,
                "experience_score": cv.experience_score,
                "education_score": cv.education_score,
                "overall_score": score
            }
            for rank, cv, score in selected
        ]
        
        # Save ranking to MongoDB
        ranking_col = mongo_manager.get_collection("rankings")
        ranking = {
            "job_id": job_id,
            "num_interviews": num_interviews,
            "weights": weights,
            "ranked_candidates": ranked_candidates,
            "created_at": datetime.now()
        }
        ranking_col.insert_one(ranking)
        
        return {
            "status": "success",
            "job_id": job_id,
            "total_candidates_ranked": len(selected),
            "interview_slots": num_interviews,
            "ranked_candidates": ranked_candidates
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule-interviews/{job_id}", response_model=dict)
async def schedule_interviews(
    job_id: str,
    scheduled_date: str,  # Format: YYYY-MM-DD
    num_interviews: int = 10,
    start_hour: int = 9,
    end_hour: int = 17,
    interview_duration: int = 45
):
    """
    Schedule interviews for top candidates using Activity Selection algorithm.
    
    - **job_id**: MongoDB object ID of the job
    - **scheduled_date**: Date for interviews (YYYY-MM-DD format)
    - **num_interviews**: Number of candidates to interview
    - **start_hour**: Start hour of the day (24-hour format)
    - **end_hour**: End hour of the day (24-hour format)
    - **interview_duration**: Duration of each interview in minutes
    
    Returns conflict-free schedule with maximum interviews scheduled.
    """
    try:
        # Parse date
        schedule_date = datetime.strptime(scheduled_date, "%Y-%m-%d")
        
        # Get ranked candidates for this job
        ranking_col = mongo_manager.get_collection("rankings")
        ranking = ranking_col.find_one({"job_id": job_id})
        
        if not ranking:
            raise HTTPException(status_code=404, detail="No ranking found for this job. Please rank candidates first.")
        
        # Extract top candidates
        ranked_candidates = ranking.get("ranked_candidates", [])[:num_interviews]
        candidates_list = [
            (cand["candidate_id"], cand["name"])
            for cand in ranked_candidates
        ]
        
        # Optimize schedule using Activity Selection
        schedule_result = optimize_schedule(
            candidates=candidates_list,
            available_hours=(start_hour, end_hour),
            interview_duration=interview_duration,
            date=schedule_date
        )
        
        # Save schedule to MongoDB
        schedule_col = mongo_manager.get_collection("schedules")
        schedule_doc = {
            "job_id": job_id,
            "scheduled_date": schedule_date,
            "schedule": schedule_result,
            "created_at": datetime.now()
        }
        schedule_col.insert_one(schedule_doc)
        
        return {
            "status": "success",
            "job_id": job_id,
            "scheduled_date": scheduled_date,
            "total_interviews": schedule_result['total_candidates'],
            "scheduled_count": schedule_result['scheduled_interviews'],
            "schedule": schedule_result['schedule']
        }
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-schedule/{job_id}", response_model=dict)
async def get_schedule(job_id: str):
    """
    Get the interview schedule for a job.
    
    - **job_id**: MongoDB object ID of the job
    """
    try:
        schedule_col = mongo_manager.get_collection("schedules")
        schedule_doc = schedule_col.find_one({"job_id": job_id})
        
        if not schedule_doc:
            raise HTTPException(status_code=404, detail="No schedule found for this job")
        
        schedule_doc['_id'] = str(schedule_doc['_id'])
        
        return {
            "status": "success",
            "job_id": job_id,
            "schedule": schedule_doc
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-ranking/{job_id}", response_model=dict)
async def get_ranking(job_id: str):
    """
    Get the candidate ranking for a job.
    
    - **job_id**: MongoDB object ID of the job
    """
    try:
        ranking_col = mongo_manager.get_collection("rankings")
        ranking = ranking_col.find_one({"job_id": job_id})
        
        if not ranking:
            raise HTTPException(status_code=404, detail="No ranking found for this job")
        
        ranking['_id'] = str(ranking['_id'])
        
        return {
            "status": "success",
            "job_id": job_id,
            "ranking": ranking
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
