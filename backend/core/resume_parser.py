import io
import re
from typing import Optional
import PyPDF2
from docx import Document
import dateparser


class ResumeTextExtractor:
    """Extract text from PDF and DOCX files"""
    
    @staticmethod
    def extract_from_pdf(file_bytes: bytes) -> str:
        """Extract text from PDF file"""
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    @staticmethod
    def extract_from_docx(file_bytes: bytes) -> str:
        """Extract text from DOCX file"""
        doc = Document(io.BytesIO(file_bytes))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    @staticmethod
    def extract_text(file_bytes: bytes, file_extension: str) -> str:
        """
        Extract text from resume file (PDF or DOCX)
        
        Args:
            file_bytes: File contents as bytes
            file_extension: File extension (.pdf or .docx)
        
        Returns:
            Extracted text from the file
        """
        file_extension = file_extension.lower()
        
        if file_extension == ".pdf":
            return ResumeTextExtractor.extract_from_pdf(file_bytes)
        elif file_extension == ".docx":
            return ResumeTextExtractor.extract_from_docx(file_bytes)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")


class ResumeParser:
    """Parse resume text and extract structured information using NLP patterns"""
    
    # Define skill keywords for matching
    TECHNICAL_SKILLS = {
        "python", "java", "c++", "c#", "javascript", "typescript", "golang", "rust",
        "react", "angular", "vue", "fastapi", "django", "flask", "express", "node.js",
        "mongodb", "postgresql", "mysql", "sql", "oracle", "redis", "elasticsearch",
        "docker", "kubernetes", "aws", "azure", "gcp", "terraform", "jenkins",
        "git", "linux", "windows", "macos", "html", "css", "tailwindcss",
        "rest api", "graphql", "microservices", "agile", "scrum", "devops"
    }
    
    SOFT_SKILLS = {
        "leadership", "communication", "teamwork", "problem solving", "project management",
        "critical thinking", "collaboration", "negotiation", "presentation", "time management",
        "attention to detail", "adaptability", "creativity", "analytical thinking"
    }
    
    @staticmethod
    def extract_email(text: str) -> Optional[str]:
        """Extract email from resume text"""
        pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        match = re.search(pattern, text)
        return match.group(0) if match else None
    
    @staticmethod
    def extract_phone(text: str) -> Optional[str]:
        """Extract phone number from resume text"""
        pattern = r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
        match = re.search(pattern, text)
        return match.group(0) if match else None
    
    @staticmethod
    def extract_name(text: str, email: Optional[str] = None) -> str:
        """Extract name from resume (usually first few lines)"""
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) > 2 and len(line) < 40:
                # Filter out common section headers
                if not any(keyword in line.lower() for keyword in 
                          ['resume', 'cv', 'curriculum', 'email:', 'phone:', 'address:', 'date:']):
                    return line
        return "Unknown"
    
    @staticmethod
    def extract_skills(text: str) -> list[str]:
        """Extract skills from resume text using keyword matching"""
        text_lower = text.lower()
        found_skills = set()
        
        # Check technical skills
        for skill in ResumeParser.TECHNICAL_SKILLS:
            if skill in text_lower:
                found_skills.add(skill)
        
        # Check soft skills
        for skill in ResumeParser.SOFT_SKILLS:
            if skill in text_lower:
                found_skills.add(skill)
        
        return sorted(list(found_skills))
    
    @staticmethod
    def extract_education(text: str) -> list[dict]:
        """Extract education entries from resume"""
        education = []
        
        # Degree patterns
        degree_pattern = r"(B\.?Tech|B\.?Sc|M\.?Tech|M\.?Sc|Bachelor|Master|B\.?A|B\.?S|MBA|Ph\.?D)"
        degrees = re.finditer(degree_pattern, text, re.IGNORECASE)
        
        for degree_match in degrees:
            # Extract degree and surrounding context (next 100 chars)
            start = degree_match.start()
            end = min(start + 150, len(text))
            context = text[start:end]
            
            # Try to extract CGPA/GPA
            gpa_pattern = r"(CGPA|GPA)?\s*[:\s=]*(\d+\.?\d*)/(\d+)|(\d+\.?\d*)\s*(CGPA|GPA)"
            gpa_match = re.search(gpa_pattern, context, re.IGNORECASE)
            gpa = None
            if gpa_match:
                if gpa_match.group(2):
                    gpa = float(gpa_match.group(2))
                elif gpa_match.group(4):
                    gpa = float(gpa_match.group(4))
            
            # Extract institution (usually in capitals or proper noun)
            institution_pattern = r"(?:from|at|of|in)?\s*([A-Z][A-Za-z\s&]*(?:University|Institute|College|School|Academy))"
            inst_match = re.search(institution_pattern, context)
            institution = inst_match.group(1) if inst_match else "Unknown Institution"
            
            education.append({
                "degree": degree_match.group(1),
                "institution": institution,
                "cgpa": gpa
            })
        
        return education
    
    @staticmethod
    def extract_experience(text: str) -> list[dict]:
        """Extract experience entries from resume"""
        experience = []
        
        # Look for job title patterns (usually followed by company name)
        job_pattern = r"(Software Engineer|Developer|Manager|Analyst|Architect|Designer|Lead|Senior|Junior|Intern)"
        company_pattern = r"(?:at|for)\s+([A-Z][A-Za-z\s&]*(?:Inc|Ltd|Corp|Company|LLC)?)"
        
        job_matches = re.finditer(job_pattern, text, re.IGNORECASE)
        
        for job_match in job_matches:
            start = job_match.start()
            end = min(start + 200, len(text))
            context = text[start:end]
            
            # Find company
            company_match = re.search(company_pattern, context)
            company = company_match.group(1) if company_match else "Unknown Company"
            
            # Estimate duration (look for year ranges or month/year)
            duration_pattern = r"(\d{4})\s*[-–]\s*(\d{4})|(\d{1,2})\s*(?:months?|years?)"
            duration_match = re.search(duration_pattern, context)
            duration_months = 12  # Default 1 year
            
            if duration_match:
                if duration_match.group(1) and duration_match.group(2):
                    # Year range
                    duration_months = (int(duration_match.group(2)) - int(duration_match.group(1))) * 12
                elif duration_match.group(3):
                    # Explicit duration
                    duration_months = int(duration_match.group(3))
            
            experience.append({
                "role": job_match.group(1),
                "company": company,
                "duration_months": max(1, duration_months)
            })
        
        return experience
    
    @staticmethod
    def parse_resume(text: str) -> dict:
        """
        Parse resume text and extract all structured information.
        
        Args:
            text: Raw resume text
        
        Returns:
            Dictionary with extracted resume data
        """
        email = ResumeParser.extract_email(text)
        phone = ResumeParser.extract_phone(text)
        name = ResumeParser.extract_name(text, email)
        skills = ResumeParser.extract_skills(text)
        education = ResumeParser.extract_education(text)
        experience = ResumeParser.extract_experience(text)
        
        return {
            "name": name,
            "email": email,
            "phone": phone,
            "skills": skills,
            "education": education,
            "experience": experience,
            "raw_text": text
        }
