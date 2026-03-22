"""
Skill Gap Analysis Agent
Identifies missing skills and recommends learning resources
"""

import logging
import json
from typing import Dict, Any, List
from backend.providers.ai_router import get_ai_router

logger = logging.getLogger(__name__)


class SkillGapAgent:
    """Analyzes skill gaps and recommends learning resources"""

    def __init__(self):
        self.ai_router = get_ai_router()

    async def analyze_gaps(
        self,
        user_skills: List[str],
        required_skills: List[str],
        user_experience_years: int = 0,
    ) -> Dict[str, Any]:
        """
        Analyze skill gaps between user and job requirements
        
        Args:
            user_skills: Skills user currently has
            required_skills: Skills required by job
            user_experience_years: Years of experience
        
        Returns:
            Gap analysis with recommendations
        """
        missing_skills = [
            s for s in required_skills
            if s.lower() not in [u.lower() for u in user_skills]
        ]

        partial_match = [
            s for s in required_skills
            if s.lower() in [u.lower() for u in user_skills]
        ]

        gap_analysis = {
            "total_required_skills": len(required_skills),
            "matched_skills": len(partial_match),
            "missing_skills": missing_skills,
            "match_percentage": (len(partial_match) / len(required_skills) * 100)
            if required_skills
            else 100,
            "gap_severity": self._calculate_gap_severity(
                len(missing_skills), len(required_skills)
            ),
        }

        return gap_analysis

    async def get_learning_recommendations(
        self,
        skill: str,
        user_experience_years: int = 0,
    ) -> Dict[str, Any]:
        """
        Get learning recommendations for a skill
        
        Args:
            skill: Skill to learn
            user_experience_years: User's experience level
        
        Returns:
            Learning resources and recommendations
        """
        difficulty = "advanced" if user_experience_years >= 5 else "intermediate"

        prompt = f"""Provide learning resources for: {skill}

User Experience Level: {user_experience_years} years

Recommend:
1. Free online courses (Coursera, Udemy, YouTube, etc.)
2. Official documentation/tutorials
3. Practice projects
4. Communities/forums
5. Estimated time to learn (for {difficulty} level)
6. Prerequisites

Format as JSON with keys: courses, documentation, projects, communities, time_estimate, prerequisites"""

        try:
            response = await self.ai_router.generate(prompt, max_tokens=1024)
            
            try:
                recommendations = json.loads(response)
            except json.JSONDecodeError:
                recommendations = {"raw_response": response}
            
            return recommendations
        except Exception as e:
            logger.error(f"Error getting learning recommendations: {e}")
            return {"error": str(e)}

    async def get_learning_roadmap(
        self,
        missing_skills: List[str],
        time_available_hours_per_week: int = 10,
    ) -> Dict[str, Any]:
        """
        Create a learning roadmap for multiple skills
        
        Args:
            missing_skills: List of skills to learn
            time_available_hours_per_week: Hours per week available to learn
        
        Returns:
            Structured learning roadmap
        """
        skills_str = ", ".join(missing_skills)

        prompt = f"""Create a learning roadmap for someone wanting to learn these skills:
{skills_str}

Available time: {time_available_hours_per_week} hours per week

Provide:
1. Prioritized skill learning order (which to learn first)
2. Weekly schedule
3. Milestones (what to achieve each month)
4. Projects to build (hands-on practice)
5. Timeline to job-readiness
6. Success metrics

Format as JSON with keys: priority_order, weekly_schedule, milestones, projects, timeline, success_metrics"""

        try:
            response = await self.ai_router.generate(prompt, max_tokens=2048)
            
            try:
                roadmap = json.loads(response)
            except json.JSONDecodeError:
                roadmap = {"raw_response": response}
            
            return roadmap
        except Exception as e:
            logger.error(f"Error creating learning roadmap: {e}")
            return {"error": str(e)}

    def _calculate_gap_severity(self, missing_count: int, total_required: int) -> str:
        """
        Calculate severity of skill gap
        
        Returns:
            "low", "medium", or "high"
        """
        if total_required == 0:
            return "low"

        percentage = (missing_count / total_required) * 100

        if percentage <= 25:
            return "low"
        elif percentage <= 50:
            return "medium"
        else:
            return "high"

    async def suggest_quick_wins(
        self,
        missing_skills: List[str],
    ) -> List[Dict[str, str]]:
        """
        Suggest quick wins - skills that are easiest to learn quickly
        
        Args:
            missing_skills: List of missing skills
        
        Returns:
            Skills sorted by learning ease/speed
        """
        if not missing_skills:
            return []

        prompt = f"""Rate these skills by how quickly someone can learn them (1 week to 3 months):
{', '.join(missing_skills)}

Consider:
- Online resource availability
- Complexity
- Learning curve
- Time to basic proficiency

Return as JSON: {{"quick_wins": [skill list], "medium_term": [skill list], "long_term": [skill list]}}"""

        try:
            response = await self.ai_router.generate(prompt, max_tokens=512)
            result = json.loads(response)
            return result
        except Exception as e:
            logger.error(f"Error suggesting quick wins: {e}")
            return {"quick_wins": missing_skills[:3]}
