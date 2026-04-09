def longest_common_subsequence(str1: str, str2: str) -> tuple[str, float]:
    """
    Compute the Longest Common Subsequence (LCS) between two strings.
    
    This algorithm is used to find the degree of overlap between candidate skills
    and job description required skills.
    
    Args:
        str1: First string (e.g., sorted candidate skills)
        str2: Second string (e.g., sorted job skills)
    
    Returns:
        tuple: (lcs_string, similarity_score) where similarity_score is normalized
               against the length of str2 (job requirements)
    
    Time Complexity: O(m*n) where m and n are lengths of strings
    Space Complexity: O(m*n) for the DP table
    """
    m, n = len(str1), len(str2)
    
    # Create DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Fill the DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    
    # Reconstruct the LCS
    lcs_str = ""
    i, j = m, n
    while i > 0 and j > 0:
        if str1[i - 1] == str2[j - 1]:
            lcs_str = str1[i - 1] + lcs_str
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    
    # Calculate similarity score as percentage of job requirements matched
    similarity_score = (len(lcs_str) / max(n, 1)) * 100 if n > 0 else 0.0
    
    return lcs_str, similarity_score


def calculate_skill_match_score(candidate_skills: list[str], required_skills: list[str]) -> tuple[float, list[str], list[str]]:
    """
    Calculate skill match score using LCS algorithm.
    
    Args:
        candidate_skills: List of skills from candidate's resume
        required_skills: List of skills required by the job
    
    Returns:
        tuple: (match_score, matched_skills, missing_skills)
    """
    # Normalize and sort for canonical comparison
    candidate_set = set(skill.lower().strip() for skill in candidate_skills)
    required_set = set(skill.lower().strip() for skill in required_skills)
    
    # Create sorted strings for LCS
    candidate_str = ",".join(sorted(candidate_set))
    required_str = ",".join(sorted(required_set))
    
    # Get LCS and score
    _, match_score = longest_common_subsequence(candidate_str, required_str)
    
    # Find matched and missing skills
    matched = candidate_set.intersection(required_set)
    missing = required_set - candidate_set
    
    return match_score, list(matched), list(missing)
