"""
Resume Generation Agent
Generates tailored resumes based on job descriptions
"""

import logging
import json
from typing import Dict, Any, List, Optional
from backend.providers.ai_router import get_ai_router

logger = logging.getLogger(__name__)


class ResumeAgent:
    """Generates and tailors resumes for specific jobs"""

    def __init__(self):
        self.ai_router = get_ai_router()

    async def generate_tailored_resume(
        self,
        user_profile: Dict[str, Any],
        job_description: str,
        required_skills: List[str],
    ) -> Dict[str, Any]:
        """
        Generate resume tailored to specific job
        
        Args:
            user_profile: User's profile data
            job_description: Target job description
            required_skills: Skills required by job
        
        Returns:
            Tailored resume content
        """
        prompt = f"""Create a professional resume tailored for this job.

USER PROFILE:
Name: {user_profile.get('first_name', '')} {user_profile.get('last_name', '')}
Email: {user_profile.get('email', '')}
Phone: {user_profile.get('phone', '')}
Current Role: {user_profile.get('current_role', '')}
Years of Experience: {user_profile.get('experience_years', 0)}
Skills: {', '.join(user_profile.get('skills', []))}
Education: {json.dumps(user_profile.get('education', []))}

JOB REQUIREMENTS:
Required Skills: {', '.join(required_skills)}
Job Description: {job_description[:1000]}

Create a resume that:
1. Highlights skills matching the job requirements
2. Uses keywords from the job description
3. Emphasizes relevant experience
4. Is professional and ATS-optimized
5. Includes summary, experience, education, and skills sections

Return in JSON format with sections: summary, experience, education, skills, certifications"""

        try:
            response = await self.ai_router.generate(prompt, max_tokens=2048)
            
            try:
                resume_data = json.loads(response)
            except json.JSONDecodeError:
                resume_data = {"raw_content": response}
            
            return resume_data
        except Exception as e:
            logger.error(f"Error generating tailored resume: {e}")
            return {"error": str(e)}

    async def ask_missing_info(self, missing_fields: List[str]) -> List[Dict[str, str]]:
        """
        Generate questions for missing information
        
        Args:
            missing_fields: List of fields missing from profile
        
        Returns:
            List of questions to ask user
        """
        field_questions = {
            "email": "What is your email address?",
            "phone": "What is your phone number?",
            "current_role": "What is your current job title/role?",
            "experience_years": "How many years of professional experience do you have?",
            "skills": "What are your top technical skills? (comma-separated)",
            "education": "What degrees/certifications do you have?",
            "first_name": "What is your first name?",
            "last_name": "What is your last name?",
        }

        questions = []
        for field in missing_fields:
            questions.append({
                "field": field,
                "question": field_questions.get(field, f"Please provide your {field}"),
            })

        return questions

    async def identify_missing_fields(self, user_profile: Dict[str, Any]) -> List[str]:
        """
        Identify missing required fields
        
        Returns:
            List of missing fields
        """
        required_fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "current_role",
            "experience_years",
            "skills",
            "education",
        ]

        missing = []
        for field in required_fields:
            value = user_profile.get(field)
            
            # Check if field is empty
            if value is None or (isinstance(value, (list, str)) and not value):
                missing.append(field)

        return missing

    def validate_resume_data(self, resume_data: Dict[str, Any]) -> bool:
        """Validate resume data completeness"""
        required_sections = ["summary", "experience", "skills"]
        
        for section in required_sections:
            if section not in resume_data or not resume_data[section]:
                return False
        
        return True

    async def optimize_for_ats(self, resume_content: str) -> str:
        """
        Optimize resume content for ATS systems
        
        Args:
            resume_content: Raw resume content
        
        Returns:
            ATS-optimized resume
        """
        prompt = f"""Optimize this resume for Applicant Tracking Systems (ATS).

Rules:
1. Remove special characters that ATS might not parse
2. Use standard formatting
3. Include keywords that would be searched
4. Keep proper structure and sections
5. Avoid tables, graphics, headers
6. Use standard fonts and sizes

Resume:
{resume_content}

Return optimized version."""

        try:
            optimized = await self.ai_router.generate(prompt, max_tokens=2048)
            return optimized
        except Exception as e:
            logger.error(f"Error optimizing for ATS: {e}")
            return resume_content
