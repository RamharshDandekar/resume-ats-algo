from typing import List, Tuple

class CandidateValue:
    """Represents a candidate with their weighted score"""
    def __init__(self, candidate_id: str, name: str, skill_score: float, 
                 experience_score: float, education_score: float,
                 skill_weight: float = 0.6, experience_weight: float = 0.3, 
                 education_weight: float = 0.1):
        self.candidate_id = candidate_id
        self.name = name
        self.skill_score = skill_score
        self.experience_score = experience_score
        self.education_score = education_score
        self.skill_weight = skill_weight
        self.experience_weight = experience_weight
        self.education_weight = education_weight
        
    def calculate_value(self) -> float:
        """Calculate overall weighted score"""
        return (
            self.skill_score * self.skill_weight +
            self.experience_score * self.experience_weight +
            self.education_score * self.education_weight
        )


def select_top_candidates(candidates: List[CandidateValue], interview_slots: int) -> List[Tuple[int, CandidateValue, float]]:
    """
    Use 0/1 Knapsack (Greedy Approach) to select the best candidates for interview.
    
    In this simplified case:
    - Each candidate takes 1 interview slot (weight = 1)
    - Each candidate has a value (weighted score)
    - We want to fill 'interview_slots' with maximum total value
    
    Greedy Strategy: Sort by value descending, select top N candidates.
    This is optimal for the knapsack problem when all weights are equal.
    
    Args:
        candidates: List of CandidateValue objects
        interview_slots: Maximum number of candidates to select
    
    Returns:
        List of tuples: (rank, candidate, overall_score) sorted by rank
    
    Time Complexity: O(n log n) due to sorting
    Space Complexity: O(n) for the result list
    """
    if not candidates:
        return []
    
    # Calculate values for all candidates
    candidates_with_values = []
    for candidate in candidates:
        value = candidate.calculate_value()
        candidates_with_values.append((candidate, value))
    
    # Sort by value in descending order (Greedy: highest value first)
    candidates_with_values.sort(key=lambda x: x[1], reverse=True)
    
    # Select top N candidates up to interview_slots
    selected = []
    for rank, (candidate, value) in enumerate(candidates_with_values[:interview_slots], 1):
        selected.append((rank, candidate, value))
    
    return selected


def calculate_knapsack_value(candidates: List[CandidateValue], 
                            weights: dict = None) -> dict:
    """
    Calculate individual candidate values with custom weights.
    
    Args:
        candidates: List of CandidateValue objects
        weights: Dict with keys: 'skill', 'experience', 'education'
    
    Returns:
        Dictionary with candidate details and their calculated values
    """
    if weights:
        for candidate in candidates:
            candidate.skill_weight = weights.get('skill', 0.6)
            candidate.experience_weight = weights.get('experience', 0.3)
            candidate.education_weight = weights.get('education', 0.1)
    
    result = {
        'candidates': [],
        'total_candidates': len(candidates),
        'average_score': 0
    }
    
    total_score = 0
    for candidate in candidates:
        value = candidate.calculate_value()
        result['candidates'].append({
            'candidate_id': candidate.candidate_id,
            'name': candidate.name,
            'skill_score': candidate.skill_score,
            'experience_score': candidate.experience_score,
            'education_score': candidate.education_score,
            'overall_value': round(value, 2)
        })
        total_score += value
    
    result['average_score'] = round(total_score / len(candidates), 2) if candidates else 0
    
    return result
