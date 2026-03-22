"""
Job Description Analyzer Agent
Analyzes JDs and extracts key information
"""

import logging
import json
from typing import Dict, Any, List
from backend.providers.ai_router import get_ai_router

logger = logging.getLogger(__name__)


class JDAnalyzerAgent:
    """Analyzes job descriptions and extracts structured data"""

    def __init__(self):
        self.ai_router = get_ai_router()

    async def analyze_jd(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze job description and extract key information
        
        Args:
            job_description: Full job description text
        
        Returns:
            Structured data from JD
        """
        prompt = f"""Analyze this job description and extract:
1. Key responsibilities (list)
2. Required skills (list)
3. Preferred skills (list)
4. Experience level (junior/mid/senior)
5. Salary range (if mentioned)
6. Job type (full-time/part-time/contract)
7. Remote work policy (remote/hybrid/onsite)
8. Key technologies/tools
9. Growth opportunities
10. Unique benefits

Job Description:
{job_description}

Return as JSON format only."""

        try:
            response = await self.ai_router.generate(prompt, max_tokens=1024)
            
            # Parse JSON response
            try:
                analysis = json.loads(response)
            except json.JSONDecodeError:
                # Fallback: extract from text
                analysis = self._parse_text_response(response)
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing JD: {e}")
            return self._get_default_analysis()

    async def extract_required_skills(self, job_description: str) -> List[str]:
        """Extract required skills from JD"""
        prompt = f"""Extract all REQUIRED technical skills from this job description.
Return as a JSON list of skills only.

Job Description:
{job_description}

Return format: {{"skills": ["skill1", "skill2", ...]}}"""

        try:
            response = await self.ai_router.generate(prompt, max_tokens=512)
            result = json.loads(response)
            return result.get("skills", [])
        except Exception as e:
            logger.error(f"Error extracting skills: {e}")
            return []

    async def calculate_match_score(
        self, user_skills: List[str], required_skills: List[str]
    ) -> int:
        """
        Calculate match score between user and job
        
        Args:
            user_skills: Skills user has
            required_skills: Skills required by job
        
        Returns:
            Match score (0-100)
        """
        if not required_skills:
            return 100

        user_skills_lower = [s.lower() for s in user_skills]
        required_skills_lower = [s.lower() for s in required_skills]

        # Count matches
        matches = sum(
            1 for req in required_skills_lower
            if any(req in user for user in user_skills_lower)
        )

        score = (matches / len(required_skills_lower)) * 100
        return min(100, max(0, int(score)))

    async def identify_skill_gaps(
        self, user_skills: List[str], required_skills: List[str]
    ) -> Dict[str, List[str]]:
        """
        Identify missing skills
        
        Returns:
            {
                "missing_required": [...],
                "nice_to_have": [...]
            }
        """
        user_skills_lower = [s.lower() for s in user_skills]

        missing_required = [
            s for s in required_skills
            if s.lower() not in user_skills_lower
        ]

        return {
            "missing_required": missing_required,
            "count": len(missing_required),
        }

    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """Fallback parser for text responses"""
        return {
            "raw_response": response,
            "error": "Could not parse structured response",
        }

    def _get_default_analysis(self) -> Dict[str, Any]:
        """Return default empty analysis"""
        return {
            "responsibilities": [],
            "required_skills": [],
            "preferred_skills": [],
            "experience_level": "unknown",
            "salary_range": None,
            "job_type": "full-time",
            "remote_policy": "unknown",
            "technologies": [],
            "growth_opportunities": [],
            "benefits": [],
        }
