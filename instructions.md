### **Project Title: IntelliHire - An AI-Driven Talent Acquisition Platform**

### **Project Vision:**
To create an intelligent, end-to-end hiring platform that automates the tedious and time-consuming tasks of resume screening, candidate matching, and interview scheduling. By leveraging powerful algorithms and a clean, data-driven dashboard, IntelliHire will empower HR professionals to make faster, more accurate, and unbiased hiring decisions.

---

### **🧠 Core Features (The "Major Project" Foundation)**

#### **1. Resume Analyzer & Profile Generator**
This is the data ingestion engine of the platform. Its goal is to transform unstructured resumes into structured, queryable data.

*   **Input:** Multi-format resume uploads (PDF, DOCX, TXT).
*   **Processing Pipeline:**
    1.  **Text Extraction:** Use libraries like `PyPDF2` or `python-docx` to parse raw text from files.
    2.  **NLP-Powered Entity Recognition:** Use a powerful NLP library like **`spaCy`** to perform Named Entity Recognition (NER).
        *   **Skills:** Extract technical and soft skills. This can be done by matching against a predefined skill dictionary (e.g., 'Python', 'React', 'Team Leadership') and using `spaCy`'s phrase matchers.
        *   **Education:** Identify institutions, degrees (B.Tech, M.Sc), and CGPA/GPA using regular expressions and keyword matching.
        *   **Experience:** Extract company names (as `ORG` entities), job titles, and employment duration (using date-parsing libraries like `dateparser`).
*   **Output:** A structured JSON object for each candidate, stored in the database.
    ```json
    {
      "candidate_id": "c_12345",
      "name": "Jane Doe",
      "email": "jane.doe@email.com",
      "phone": "123-456-7890",
      "education": [
        { "degree": "B.Tech in Computer Science", "institution": "Tech University", "cgpa": 8.5 }
      ],
      "experience": [
        { "role": "Software Engineer", "company": "Innovate Corp", "duration_months": 24 },
        { "role": "Intern", "company": "Code Solutions", "duration_months": 6 }
      ],
      "skills": ["Python", "FastAPI", "React", "MongoDB", "Docker"],
      "raw_text": "..."
    }
    ```

#### **2. Job Description (JD) Matching Engine**
This feature quantifies how well a candidate's profile aligns with a specific job opening.

*   **Input:** A job description or job role title. The system can either take a full JD text or have pre-defined role templates.
*   **JD Parsing:** Apply the same NLP pipeline from the Resume Analyzer to extract key requirements (required skills, years of experience, education level) from the JD.
*   **Algorithm: Longest Common Subsequence (LCS)**
    *   **Application:** Instead of running LCS on the entire raw text (which would be noisy), we apply it intelligently.
    1.  Extract the list of skills from the candidate's profile and the JD.
    2.  Sort both lists alphabetically to create canonical "skill strings" (e.g., `Docker,FastAPI,MongoDB,Python,React`).
    3.  Compute the LCS between the candidate's skill string and the JD's skill string.
    4.  **Match Score Calculation:**
        `Match Score (%) = (Length of LCS / Length of JD Skills String) * 100`
    *   This score specifically reflects the **skill overlap**, which is the most critical matching factor.

---

### **⭐ "Bestest" Features (To Elevate the Project)**

Here are the best 3 extras to implement for maximum impact:

#### **⭐ 1. Interactive Resume & Keyword Highlighting**
When a recruiter views a candidate on the dashboard, they shouldn't just see the extracted data.
*   **Implementation:**
    *   Display the candidate's raw resume text in a scrollable panel.
    *   When a job is selected, use JavaScript to dynamically find all the required skills from the JD within the resume text.
    *   Wrap these matched keywords in a `<mark>` tag or a `<span>` with a CSS class for highlighting (e.g., a bright yellow background).
    *   **Impact:** This provides immediate visual confirmation of the match score, allowing recruiters to verify the extracted skills in their original context.

#### **⭐ 2. Score Visualization & Breakdown**
A single percentage isn't enough. A professional dashboard shows the "why."
*   **Implementation:**
    *   For each candidate, display a primary progress bar for their overall match score.
    *   Next to it, show a breakdown using smaller bars or a donut chart (using `Chart.js` or a similar library):
        *   **Skill Match:** The score from the LCS algorithm.
        *   **Experience Match:** Score based on required vs. actual years of experience.
        *   **Education Match:** A binary or tiered score (e.g., meets/exceeds requirement).
    *   **Impact:** This allows recruiters to see if a candidate is strong in skills but weak in experience, or vice-versa, enabling more nuanced decisions.

#### **⭐ 3. Advanced Filtering & Export**
Give the user control over the data.
*   **Implementation:**
    *   **Filtering:** Add UI controls (dropdowns, sliders) to filter the candidate list by:
        *   Match Score (e.g., > 80%)
        *   Experience (e.g., > 3 years)
        *   Show Top 5, Top 10, or all candidates.
    *   **Export:** An "Export to CSV" button that generates a report of the filtered candidates with their key details and scores. This is a highly practical feature for sharing shortlists.

---

### **🚀 Advanced Features (DAA-Driven Decision Making)**

#### **3. Candidate Ranking & Selection System**
After scoring, the system needs to suggest the optimal shortlist of candidates to interview.

*   **Algorithm: 0/1 Knapsack (Greedy Approach)**
    *   **Problem Mapping:** We have a limited number of interview slots (`Knapsack Capacity, W`). We want to fill these slots with the "most valuable" candidates.
    *   **Item:** Each candidate is an "item."
    *   **Weight (`w_i`):** Each candidate takes up 1 interview slot, so `w_i = 1` for all.
    *   **Value (`v_i`):** This is a weighted "Overall Score" calculated for each candidate:
        `Value = (0.6 * SkillMatchScore) + (0.3 * ExperienceScore) + (0.1 * CGPAScore)`
        *(These weights can be adjusted in the UI)*.
    *   **Greedy Strategy:** Since all weights are 1, the optimal greedy strategy for the 0/1 Knapsack problem simplifies to: **"Sort all candidates in descending order of their Value (`v_i`) and pick the top `W` candidates."**
    *   **Output:** A ranked list of the top `N` candidates recommended for an interview.

#### **4. Automated Interview Scheduler**
Avoids the logistical nightmare of scheduling interviews for the selected candidates.

*   **Algorithm: Activity Selection Problem**
    *   **Problem Mapping:** We need to schedule a maximum number of non-overlapping interviews in a given set of available time slots.
    *   **Activity:** An interview for a selected candidate. Each interview has a fixed duration (e.g., 45 minutes).
    *   **Start Time (`s_i`) & Finish Time (`f_i`):** The available slots for interviews (e.g., from 10:00 AM to 5:00 PM).
    *   **Greedy Strategy:**
        1.  Create a list of all possible interview slots for the top candidates (e.g., Candidate A: 10:00-10:45, 11:00-11:45; Candidate B: 10:00-10:45, etc.).
        2.  **Sort all potential interview "activities" by their finish time in ascending order.**
        3.  Select the first activity in the sorted list and add it to the final schedule.
        4.  Iterate through the remaining activities. For each activity, if its start time is after or equal to the finish time of the previously selected activity, select it and add it to the schedule.
    *   **Output:** A conflict-free interview schedule for the day.

---

### **💻 Tech Stack & Architecture**

*   **Backend:** **Python (FastAPI)** - Modern, high-performance, and provides automatic interactive API documentation (Swagger UI), which is perfect for development and project presentations.
*   **Frontend:** **React.js** - Ideal for building a dynamic, component-based user interface like the dashboard. Use libraries like `Axios` for API calls and `Chart.js` for visualizations.
*   **Database:** **MongoDB** - A NoSQL database that stores data in JSON-like documents. It's a perfect fit for our structured candidate profiles, which don't have a rigid, uniform schema.
*   **NLP Library:** **`spaCy`** - State-of-the-art library for industrial-strength Natural Language Processing.
*   **Deployment:** **Docker** - Containerize the frontend, backend, and database for easy setup and deployment.

### **📁 High-Level Project Structure**

```
/intelli-hire
├── /backend
│   ├── main.py             # FastAPI app
│   ├── /routers            # API endpoints (candidates, jobs)
│   ├── /core               # Core logic (parsing, scoring)
│   ├── /models             # Database models (Pydantic)
│   └── requirements.txt
├── /frontend
│   ├── /src
│   │   ├── /components     # React components (Dashboard, UploadForm, Scheduler)
│   │   ├── /pages          # Main pages
│   │   └── App.js
│   └── package.json
└── docker-compose.yml      # To orchestrate all services
```

### **🎨 UI/UX Design (Professional Look & Feel)**

*   **Upload Page:** A clean, minimal page with a large drag-and-drop area for resumes and a simple text input for the job description.
*   **Dashboard Page:** This is the centerpiece.
    *   Use a **card-based layout** for each candidate.
    *   Each card displays: Candidate Name, Overall Match Score (with a prominent progress bar), and key info (e.g., last role).
    *   Status tags (e.g., `Pending`, `Shortlisted`, `Rejected`) with different colors.
    *   Clicking a card expands to show details: skill breakdown, highlighted resume, etc.
*   **Scheduler Page:** A calendar or timeline view (e.g., a simple table with time slots) showing the final, conflict-free interview schedule.

---

### **💯 DAA Connection (The "Viva Gold" Table)**

This table explicitly links the project's features to the algorithms from a Design and Analysis of Algorithms (DAA) course, explaining the "why."

| Feature                    | DAA Algorithm Used           | Justification & Implementation Details                                                                                                                                                                                                                                                             |
| -------------------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Skill Matching**         | **Longest Common Subsequence (LCS)** - *Dynamic Programming* | Measures the similarity between the sequence of skills in a resume and a job description. Applied on sorted skill lists to provide a stable, quantifiable score for skill overlap. The score is normalized against the JD's skill count.                                                      |
| **Candidate Selection**    | **0/1 Knapsack (Greedy Approach)** | Selects the optimal set of candidates for a limited number of interview slots (`W`). Each candidate has a `weight` of 1 and a `value` based on their weighted score. The greedy strategy is to sort candidates by value and pick the top `W`, maximizing the total "value" of the interview batch. |
| **Interview Scheduling**   | **Activity Selection Problem (Greedy Approach)** | Maximizes the number of non-conflicting interviews that can be conducted in a single day. Activities (interviews) are sorted by their finish times, and the earliest-finishing, non-conflicting activities are greedily selected to create an optimal, dense schedule.                        |
