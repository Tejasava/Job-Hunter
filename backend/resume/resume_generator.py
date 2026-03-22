"""
Resume Generator Module
High-level resume generation interface
"""

import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.resume.pdf_builder import PDFResumeBuilder
from backend.agents.resume_agent import ResumeAgent

logger = logging.getLogger(__name__)


class ResumeGenerator:
    """Main resume generation module"""

    def __init__(self):
        self.pdf_builder = PDFResumeBuilder()
        self.resume_agent = ResumeAgent()
        self.resumes_dir = "/Users/tejasavayadav/Desktop/job searcher/ai-job-agent/resumes"
        os.makedirs(self.resumes_dir, exist_ok=True)

    async def generate_resume(
        self,
        user_profile: Dict[str, Any],
        job_description: str,
        required_skills: List[str],
        job_id: str,
        company_name: str,
    ) -> Dict[str, Any]:
        """
        Generate a complete tailored resume
        
        Args:
            user_profile: User's profile data
            job_description: Target job description
            required_skills: Skills required by job
            job_id: Job ID (for file naming)
            company_name: Company name (for file naming)
        
        Returns:
            {
                "success": bool,
                "resume_path": str,
                "resume_data": dict,
                "error": str (if failed)
            }
        """
        try:
            # Check for missing information
            missing_fields = await self.resume_agent.identify_missing_fields(
                user_profile
            )

            if missing_fields:
                return {
                    "success": False,
                    "missing_fields": missing_fields,
                    "questions": await self.resume_agent.ask_missing_info(
                        missing_fields
                    ),
                    "error": "Missing required information",
                }

            # Generate tailored resume content
            resume_data = await self.resume_agent.generate_tailored_resume(
                user_profile, job_description, required_skills
            )

            # Generate PDF
            filename = f"{company_name}_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_path = os.path.join(self.resumes_dir, filename)

            success = self.pdf_builder.generate_pdf(resume_data, output_path)

            if success:
                return {
                    "success": True,
                    "resume_path": output_path,
                    "resume_data": resume_data,
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to generate PDF",
                }

        except Exception as e:
            logger.error(f"Error in resume generation: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def get_saved_resumes(self) -> List[Dict[str, Any]]:
        """Get list of all saved resumes"""
        resumes = []

        try:
            for filename in os.listdir(self.resumes_dir):
                if filename.endswith(".pdf"):
                    filepath = os.path.join(self.resumes_dir, filename)
                    resumes.append({
                        "filename": filename,
                        "path": filepath,
                        "size": os.path.getsize(filepath),
                        "created": datetime.fromtimestamp(
                            os.path.getctime(filepath)
                        ),
                    })

            return sorted(resumes, key=lambda x: x["created"], reverse=True)

        except Exception as e:
            logger.error(f"Error listing resumes: {e}")
            return []

    def get_latest_resume(self) -> Optional[str]:
        """Get path to latest generated resume"""
        resumes = self.get_saved_resumes()
        return resumes[0]["path"] if resumes else None
