"""
MongoDB Connection and Operations
"""

import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)


class MongoDBClient:
    """MongoDB Client with connection pooling"""

    def __init__(self, uri: Optional[str] = None):
        self.uri = uri or os.getenv(
            "MONGODB_URI", "mongodb://localhost:27017/job_hunter"
        )
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")
            self.db = self.client.job_hunter
            logger.info("Connected to MongoDB successfully")
            self._create_indexes()
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.warning(f"MongoDB connection failed: {e}. Using in-memory storage.")
            self.db = None

    def _create_indexes(self):
        """Create database indexes for performance"""
        if not self.db:
            return

        try:
            # User profiles
            self.db.users.create_index("user_id", unique=True)

            # Jobs
            self.db.jobs.create_index("job_id", unique=True)
            self.db.jobs.create_index("source")
            self.db.jobs.create_index("salary")
            self.db.jobs.create_index("created_at")

            # Applications
            self.db.applications.create_index([("user_id", 1), ("job_id", 1)])
            self.db.applications.create_index("status")
            self.db.applications.create_index("applied_at")

            # Saved jobs
            self.db.saved_jobs.create_index([("user_id", 1), ("job_id", 1)])

            logger.info("Database indexes created")
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")

    # User Profile Operations
    def save_user_profile(self, user_profile: Dict[str, Any]) -> bool:
        """Save or update user profile"""
        if not self.db:
            return False

        try:
            result = self.db.users.update_one(
                {"user_id": user_profile["user_id"]},
                {"$set": user_profile},
                upsert=True,
            )
            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as e:
            logger.error(f"Error saving user profile: {e}")
            return False

    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile by ID"""
        if not self.db:
            return None

        try:
            return self.db.users.find_one({"user_id": user_id})
        except Exception as e:
            logger.error(f"Error retrieving user profile: {e}")
            return None

    def update_user_salary_bar(self, user_id: int, salary_bar: int) -> bool:
        """Update user salary bar"""
        if not self.db:
            return False

        try:
            result = self.db.users.update_one(
                {"user_id": user_id},
                {"$set": {"salary_bar_lpa": salary_bar, "updated_at": datetime.utcnow()}},
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating salary bar: {e}")
            return False

    # Job Operations
    def save_job(self, job: Dict[str, Any]) -> bool:
        """Save job to database"""
        if not self.db:
            return False

        try:
            result = self.db.jobs.update_one(
                {"job_id": job["job_id"]},
                {"$set": job},
                upsert=True,
            )
            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as e:
            logger.error(f"Error saving job: {e}")
            return False

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        if not self.db:
            return None

        try:
            return self.db.jobs.find_one({"job_id": job_id})
        except Exception as e:
            logger.error(f"Error retrieving job: {e}")
            return None

    def get_jobs_by_salary(
        self, min_salary: int, max_salary: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get jobs by salary range (in LPA)"""
        if not self.db:
            return []

        try:
            query = {"salary": {"$gte": min_salary}}
            if max_salary:
                query["salary"]["$lte"] = max_salary

            return list(self.db.jobs.find(query).sort("salary", -1).limit(50))
        except Exception as e:
            logger.error(f"Error retrieving jobs by salary: {e}")
            return []

    def get_recent_jobs(self, hours: int = 24, limit: int = 50) -> List[Dict[str, Any]]:
        """Get jobs posted in the last N hours"""
        if not self.db:
            return []

        try:
            from datetime import timedelta

            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            return list(
                self.db.jobs.find({"posted_date": {"$gte": cutoff_time}})
                .sort("posted_date", -1)
                .limit(limit)
            )
        except Exception as e:
            logger.error(f"Error retrieving recent jobs: {e}")
            return []

    # Application Operations
    def save_application(self, application: Dict[str, Any]) -> bool:
        """Save job application"""
        if not self.db:
            return False

        try:
            result = self.db.applications.insert_one(application)
            return result.inserted_id is not None
        except Exception as e:
            logger.error(f"Error saving application: {e}")
            return False

    def get_user_applications(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all applications by user"""
        if not self.db:
            return []

        try:
            return list(self.db.applications.find({"user_id": user_id}).sort("applied_at", -1))
        except Exception as e:
            logger.error(f"Error retrieving applications: {e}")
            return []

    def update_application_status(
        self, user_id: int, job_id: str, status: str
    ) -> bool:
        """Update application status"""
        if not self.db:
            return False

        try:
            result = self.db.applications.update_one(
                {"user_id": user_id, "job_id": job_id},
                {"$set": {"status": status, "updated_at": datetime.utcnow()}},
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating application status: {e}")
            return False

    # Saved Jobs Operations
    def save_job_for_user(self, user_id: int, job: Dict[str, Any]) -> bool:
        """Save job for later"""
        if not self.db:
            return False

        try:
            result = self.db.saved_jobs.insert_one(
                {
                    "user_id": user_id,
                    "job_id": job["job_id"],
                    "job_title": job.get("title"),
                    "company": job.get("company"),
                    "saved_at": datetime.utcnow(),
                }
            )
            return result.inserted_id is not None
        except Exception as e:
            logger.error(f"Error saving job: {e}")
            return False

    def get_saved_jobs(self, user_id: int) -> List[Dict[str, Any]]:
        """Get saved jobs by user"""
        if not self.db:
            return []

        try:
            return list(
                self.db.saved_jobs.find({"user_id": user_id}).sort("saved_at", -1)
            )
        except Exception as e:
            logger.error(f"Error retrieving saved jobs: {e}")
            return []

    def remove_saved_job(self, user_id: int, job_id: str) -> bool:
        """Remove saved job"""
        if not self.db:
            return False

        try:
            result = self.db.saved_jobs.delete_one(
                {"user_id": user_id, "job_id": job_id}
            )
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error removing saved job: {e}")
            return False

    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Global database instance
_db_client = None


def get_db() -> MongoDBClient:
    """Get or create database client"""
    global _db_client
    if _db_client is None:
        _db_client = MongoDBClient()
    return _db_client
