"""
Database Models for Job Hunter Agent
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class JobStatus(str, Enum):
    """Job application status"""

    PENDING = "pending"
    APPLIED = "applied"
    REJECTED = "rejected"
    INTERVIEW = "interview"
    OFFER = "offer"
    ACCEPTED = "accepted"


class UserProfile:
    """User Profile Model"""

    def __init__(
        self,
        user_id: int,
        first_name: str = "",
        last_name: str = "",
        email: str = "",
        phone: str = "",
        current_role: str = "",
        experience_years: int = 0,
        skills: List[str] = None,
        education: List[Dict[str, Any]] = None,
        salary_bar_lpa: int = 10,
        preferred_locations: List[str] = None,
        preferred_roles: List[str] = None,
    ):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.current_role = current_role
        self.experience_years = experience_years
        self.skills = skills or []
        self.education = education or []
        self.salary_bar_lpa = salary_bar_lpa
        self.preferred_locations = preferred_locations or []
        self.preferred_roles = preferred_roles or []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "current_role": self.current_role,
            "experience_years": self.experience_years,
            "skills": self.skills,
            "education": self.education,
            "salary_bar_lpa": self.salary_bar_lpa,
            "preferred_locations": self.preferred_locations,
            "preferred_roles": self.preferred_roles,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class Job:
    """Job Model"""

    def __init__(
        self,
        job_id: str,
        title: str,
        company: str,
        location: str,
        salary: Optional[int] = None,
        salary_currency: str = "INR",
        description: str = "",
        required_skills: List[str] = None,
        apply_link: str = "",
        source: str = "",
        posted_date: Optional[datetime] = None,
        job_type: str = "Full-time",
    ):
        self.job_id = job_id
        self.title = title
        self.company = company
        self.location = location
        self.salary = salary
        self.salary_currency = salary_currency
        self.description = description
        self.required_skills = required_skills or []
        self.apply_link = apply_link
        self.source = source
        self.posted_date = posted_date or datetime.utcnow()
        self.job_type = job_type
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "salary": self.salary,
            "salary_currency": self.salary_currency,
            "description": self.description,
            "required_skills": self.required_skills,
            "apply_link": self.apply_link,
            "source": self.source,
            "posted_date": self.posted_date,
            "job_type": self.job_type,
            "created_at": self.created_at,
        }


class Application:
    """Job Application Model"""

    def __init__(
        self,
        user_id: int,
        job_id: str,
        job_title: str,
        company: str,
        resume_path: str = "",
        applied_at: Optional[datetime] = None,
        status: JobStatus = JobStatus.PENDING,
    ):
        self.user_id = user_id
        self.job_id = job_id
        self.job_title = job_title
        self.company = company
        self.resume_path = resume_path
        self.applied_at = applied_at or datetime.utcnow()
        self.status = status
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "job_id": self.job_id,
            "job_title": self.job_title,
            "company": self.company,
            "resume_path": self.resume_path,
            "applied_at": self.applied_at,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class SavedJob:
    """Saved Job Model"""

    def __init__(
        self,
        user_id: int,
        job_id: str,
        job_title: str,
        company: str,
        saved_at: Optional[datetime] = None,
    ):
        self.user_id = user_id
        self.job_id = job_id
        self.job_title = job_title
        self.company = company
        self.saved_at = saved_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "job_id": self.job_id,
            "job_title": self.job_title,
            "company": self.company,
            "saved_at": self.saved_at,
        }
