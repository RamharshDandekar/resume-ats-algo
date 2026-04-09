from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List
from bson import ObjectId

from db import mongo_manager
from models import CandidateProfile, Education, Experience
from core import ResumeParser, ResumeTextExtractor

router = APIRouter()


@router.post("/upload-resume", response_model=dict)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and parse a resume file (PDF or DOCX).
    
    - **file**: Resume file (PDF or DOCX)
    
    Returns structured candidate profile with extracted information.
    """
    try:
        # Read file
        contents = await file.read()
        file_extension = file.filename.split(".")[-1]
        
        # Extract text from file
        raw_text = ResumeTextExtractor.extract_text(contents, f".{file_extension}")
        
        # Parse resume using NLP
        parsed_data = ResumeParser.parse_resume(raw_text)
        
        # Create candidate profile
        candidate = CandidateProfile(
            name=parsed_data['name'],
            email=parsed_data['email'],
            phone=parsed_data['phone'],
            skills=parsed_data['skills'],
            raw_text=parsed_data['raw_text'],
            education=[Education(**edu) for edu in parsed_data['education']],
            experience=[Experience(**exp) for exp in parsed_data['experience']]
        )
        
        # Save to MongoDB
        candidates_col = mongo_manager.get_collection("candidates")
        candidate_dict = candidate.model_dump()
        candidate_dict['created_at'] = candidate_dict.get('created_at')
        
        result = candidates_col.insert_one(candidate_dict)
        candidate.candidate_id = str(result.inserted_id)
        
        return {
            "status": "success",
            "candidate_id": str(result.inserted_id),
            "name": candidate.name,
            "email": candidate.email,
            "skills_count": len(candidate.skills),
            "education_count": len(candidate.education),
            "experience_count": len(candidate.experience)
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing resume: {str(e)}")


@router.get("/list", response_model=dict)
async def list_candidates(skip: int = 0, limit: int = 10):
    """
    List all candidates with pagination.
    
    - **skip**: Number of candidates to skip (for pagination)
    - **limit**: Number of candidates to return
    """
    try:
        candidates_col = mongo_manager.get_collection("candidates")
        
        # Fetch candidates
        candidates = list(candidates_col.find().skip(skip).limit(limit))
        total = candidates_col.count_documents({})
        
        # Convert ObjectId to string
        for candidate in candidates:
            candidate['_id'] = str(candidate['_id'])
        
        return {
            "status": "success",
            "total": total,
            "skip": skip,
            "limit": limit,
            "candidates": candidates
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{candidate_id}", response_model=dict)
async def get_candidate(candidate_id: str):
    """
    Get a specific candidate profile by ID.
    
    - **candidate_id**: MongoDB object ID of the candidate
    """
    try:
        candidates_col = mongo_manager.get_collection("candidates")
        candidate = candidates_col.find_one({"_id": ObjectId(candidate_id)})
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        candidate['_id'] = str(candidate['_id'])
        return {
            "status": "success",
            "candidate": candidate
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{candidate_id}", response_model=dict)
async def delete_candidate(candidate_id: str):
    """
    Delete a candidate from the system.
    
    - **candidate_id**: MongoDB object ID of the candidate
    """
    try:
        candidates_col = mongo_manager.get_collection("candidates")
        result = candidates_col.delete_one({"_id": ObjectId(candidate_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        return {
            "status": "success",
            "message": "Candidate deleted successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/search/by-skill", response_model=dict)
async def search_by_skill(skill: str):
    """
    Search candidates by a specific skill.
    
    - **skill**: Skill name to search for
    """
    try:
        candidates_col = mongo_manager.get_collection("candidates")
        candidates = list(candidates_col.find({"skills": skill.lower().strip()}))
        
        for candidate in candidates:
            candidate['_id'] = str(candidate['_id'])
        
        return {
            "status": "success",
            "skill": skill,
            "count": len(candidates),
            "candidates": candidates
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
