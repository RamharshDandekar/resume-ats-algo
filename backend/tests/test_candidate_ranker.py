import pytest
from backend.core.candidate_ranker import select_top_candidates, CandidateValue, calculate_knapsack_value


class TestCandidateValue:
    """Test CandidateValue class"""
    
    def test_calculate_value_default_weights(self):
        """Test value calculation with default weights"""
        candidate = CandidateValue(
            candidate_id="c1",
            name="John Doe",
            skill_score=80,
            experience_score=70,
            education_score=90
        )
        value = candidate.calculate_value()
        # 80*0.6 + 70*0.3 + 90*0.1 = 48 + 21 + 9 = 78
        assert value == 78.0
    
    def test_calculate_value_custom_weights(self):
        """Test value calculation with custom weights"""
        candidate = CandidateValue(
            candidate_id="c1",
            name="John Doe",
            skill_score=100,
            experience_score=50,
            education_score=50,
            skill_weight=0.8,
            experience_weight=0.1,
            education_weight=0.1
        )
        value = candidate.calculate_value()
        # 100*0.8 + 50*0.1 + 50*0.1 = 80 + 5 + 5 = 90
        assert value == 90.0


class TestSelectTopCandidates:
    """Test cases for candidate selection (Knapsack)"""
    
    def test_select_all_when_enough_slots(self):
        """Test selecting all candidates when slots are available"""
        candidates = [
            CandidateValue("c1", "Alice", 90, 80, 85),
            CandidateValue("c2", "Bob", 70, 60, 75),
            CandidateValue("c3", "Charlie", 85, 75, 80)
        ]
        selected = select_top_candidates(candidates, interview_slots=5)
        assert len(selected) == 3
    
    def test_select_top_candidates_by_score(self):
        """Test that top candidates are selected by score (descending)"""
        candidates = [
            CandidateValue("c1", "Alice", 90, 80, 85),     # Value: 85.5
            CandidateValue("c2", "Bob", 70, 60, 75),       # Value: 69
            CandidateValue("c3", "Charlie", 85, 75, 80)    # Value: 81
        ]
        selected = select_top_candidates(candidates, interview_slots=2)
        assert len(selected) == 2
        assert selected[0][0] == 1  # Rank 1
        assert selected[0][1].name == "Alice"  # Highest score
        assert selected[1][0] == 2  # Rank 2
        assert selected[1][1].name == "Charlie"  # Second highest
    
    def test_select_zero_slots(self):
        """Test with zero available slots"""
        candidates = [
            CandidateValue("c1", "Alice", 90, 80, 85),
        ]
        selected = select_top_candidates(candidates, interview_slots=0)
        assert len(selected) == 0
    
    def test_select_empty_candidates(self):
        """Test with empty candidate list"""
        selected = select_top_candidates([], interview_slots=5)
        assert len(selected) == 0
    
    def test_rank_assignment(self):
        """Test that ranks are assigned correctly"""
        candidates = [
            CandidateValue("c1", "Alice", 95, 85, 90),
            CandidateValue("c2", "Bob", 75, 65, 70),
            CandidateValue("c3", "Charlie", 80, 70, 75)
        ]
        selected = select_top_candidates(candidates, interview_slots=3)
        ranks = [item[0] for item in selected]
        assert ranks == [1, 2, 3]


class TestCalculateKnapsackValue:
    """Test cases for knapsack value calculation"""
    
    def test_calculate_values_with_default_weights(self):
        """Test value calculation with default weights"""
        candidates = [
            CandidateValue("c1", "Alice", 80, 70, 90),
            CandidateValue("c2", "Bob", 70, 60, 75)
        ]
        result = calculate_knapsack_value(candidates)
        assert result['total_candidates'] == 2
        assert len(result['candidates']) == 2
        assert result['average_score'] > 0
    
    def test_calculate_values_with_custom_weights(self):
        """Test value calculation with custom weights"""
        candidates = [
            CandidateValue("c1", "Alice", 100, 50, 50)
        ]
        weights = {'skill': 0.7, 'experience': 0.2, 'education': 0.1}
        result = calculate_knapsack_value(candidates, weights)
        # 100*0.7 + 50*0.2 + 50*0.1 = 70 + 10 + 5 = 85
        assert result['candidates'][0]['overall_value'] == 85.0
    
    def test_average_score_calculation(self):
        """Test that average score is calculated correctly"""
        candidates = [
            CandidateValue("c1", "Alice", 80, 80, 80),  # Value: 80
            CandidateValue("c2", "Bob", 60, 60, 60)      # Value: 60
        ]
        result = calculate_knapsack_value(candidates)
        # Average should be (80 + 60) / 2 = 70
        assert result['average_score'] == 70.0
