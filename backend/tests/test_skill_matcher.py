import pytest
from backend.core.skill_matcher import calculate_skill_match_score, longest_common_subsequence


class TestLCS:
    """Test cases for Longest Common Subsequence algorithm"""
    
    def test_basic_lcs(self):
        """Test basic LCS calculation"""
        lcs, score = longest_common_subsequence("python,react", "python,javascript")
        assert "python" in lcs
        assert score > 0
    
    def test_lcs_no_match(self):
        """Test LCS with no common elements"""
        lcs, score = longest_common_subsequence("java,c++", "python,javascript")
        # Should still compute, but score should be low
        assert isinstance(score, float)
    
    def test_lcs_identical_strings(self):
        """Test LCS with identical strings"""
        lcs, score = longest_common_subsequence("python,react,docker", "python,react,docker")
        assert score == 100.0
    
    def test_lcs_empty_strings(self):
        """Test LCS with empty strings"""
        lcs, score = longest_common_subsequence("", "python,react")
        assert score == 0.0
    
    def test_lcs_single_element(self):
        """Test LCS with single element"""
        lcs, score = longest_common_subsequence("python", "python,javascript")
        assert score > 0


class TestSkillMatchScore:
    """Test cases for skill matching"""
    
    def test_perfect_skill_match(self):
        """Test with perfect skill overlap"""
        candidate_skills = ["python", "react", "docker"]
        required_skills = ["python", "react", "docker"]
        
        score, matched, missing = calculate_skill_match_score(candidate_skills, required_skills)
        assert score == 100.0
        assert len(matched) == 3
        assert len(missing) == 0
    
    def test_partial_skill_match(self):
        """Test with partial skill overlap"""
        candidate_skills = ["python", "react", "docker"]
        required_skills = ["python", "react", "kubernetes", "jenkins"]
        
        score, matched, missing = calculate_skill_match_score(candidate_skills, required_skills)
        assert 0 < score < 100
        assert "python" in matched
        assert "react" in matched
        assert "kubernetes" in missing
    
    def test_no_skill_match(self):
        """Test with no skill overlap"""
        candidate_skills = ["java", "spring"]
        required_skills = ["python", "react", "docker"]
        
        score, matched, missing = calculate_skill_match_score(candidate_skills, required_skills)
        # Score should be very low when no skills match
        assert score < 20.0
        assert len(matched) == 0
    
    def test_case_insensitive_matching(self):
        """Test that skill matching is case insensitive"""
        candidate_skills = ["Python", "REACT"]
        required_skills = ["python", "React"]
        
        score, matched, missing = calculate_skill_match_score(candidate_skills, required_skills)
        assert score == 100.0
    
    def test_empty_candidate_skills(self):
        """Test with empty candidate skills"""
        candidate_skills = []
        required_skills = ["python", "react"]
        
        score, matched, missing = calculate_skill_match_score(candidate_skills, required_skills)
        assert score == 0.0
