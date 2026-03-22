"""
GitHub Jobs Scraper
Scrapes job listings from GitHub Jobs (legacy API)
"""

import logging
from typing import List, Dict, Any, Optional
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)


class GitHubJobsScraper:
    """Scrapes jobs from GitHub Jobs API"""

    API_URL = "https://jobs.github.com/positions.json"
    PLATFORM_NAME = "github_jobs"

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def search(
        self,
        query: str,
        location: Optional[str] = None,
        pages: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Search for jobs on GitHub Jobs API
        
        Args:
            query: Job title/keywords
            location: Job location
            pages: Number of pages to scrape
        
        Returns:
            List of job postings
        """
        jobs = []

        try:
            import requests

            params = {
                "description": query,
                "location": location or "",
                "full_time": True,
            }

            response = requests.get(
                self.API_URL,
                params=params,
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()

            for job_data in data:
                try:
                    job = self._extract_job_from_json(job_data)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.warning(f"Error extracting job data: {e}")
                    continue

            logger.info(f"Found {len(jobs)} jobs on GitHub Jobs")

        except Exception as e:
            logger.error(f"Error scraping GitHub Jobs: {e}")

        return jobs

    def _extract_job_from_json(self, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract job from GitHub Jobs API response"""
        try:
            title = job_data.get("title", "")
            company = job_data.get("company", "")
            location = job_data.get("location", "Remote")
            description = job_data.get("description", "")
            url = job_data.get("url", "")

            if not all([title, company, url]):
                return None

            job_id = hashlib.md5(url.encode()).hexdigest()

            return {
                "job_id": job_id,
                "title": title,
                "company": company,
                "location": location,
                "salary": None,  # GitHub Jobs doesn't provide salary
                "description": description,
                "apply_link": url,
                "source": self.PLATFORM_NAME,
                "posted_date": datetime.utcnow(),
                "job_type": "Full-time",
            }

        except Exception as e:
            logger.warning(f"Error extracting job: {e}")
            return None
