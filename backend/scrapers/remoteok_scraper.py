"""
RemoteOK Job Scraper
Scrapes remote jobs from RemoteOK
"""

import logging
from typing import List, Dict, Any, Optional
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)


class RemoteOKScraper:
    """Scrapes jobs from RemoteOK - Remote work focused"""

    BASE_URL = "https://remoteok.com"
    PLATFORM_NAME = "remoteok"

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
        Search for remote jobs on RemoteOK
        
        Args:
            query: Job title/keywords
            location: Ignored for remote jobs
            pages: Number of pages to scrape
        
        Returns:
            List of job postings
        """
        jobs = []

        try:
            import requests
            from bs4 import BeautifulSoup

            # RemoteOK has JSON API
            url = f"{self.BASE_URL}/api?tag={query}"

            response = requests.get(url, headers=self.headers, timeout=10)
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

            logger.info(f"Found {len(jobs)} jobs on RemoteOK")

        except Exception as e:
            logger.error(f"Error scraping RemoteOK: {e}")

        return jobs

    def _extract_job_from_json(self, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract job from JSON response"""
        try:
            title = job_data.get("title", "")
            company = job_data.get("company", "")
            description = job_data.get("description", "")
            url = job_data.get("url", "")
            salary_max = job_data.get("salary_max", 0)
            salary_min = job_data.get("salary_min", 0)

            if not all([title, company, url]):
                return None

            # Convert salary to LPA (assuming USD, rough conversion)
            salary = None
            if salary_max:
                # Rough conversion: 1 USD per hour * 2000 hours/year = $2000 annual
                # Convert to INR and then to LPA
                salary_usd_annual = (salary_max + (salary_min or 0)) / 2 * 2000
                salary_inr = salary_usd_annual * 82  # Rough USD to INR
                salary = int(salary_inr / 100000)  # Convert to LPA

            job_id = hashlib.md5(url.encode()).hexdigest()

            return {
                "job_id": job_id,
                "title": title,
                "company": company,
                "location": "Remote",
                "salary": salary,
                "description": description,
                "apply_link": url,
                "source": self.PLATFORM_NAME,
                "posted_date": datetime.utcnow(),
                "job_type": "Full-time",
            }

        except Exception as e:
            logger.warning(f"Error extracting job: {e}")
            return None
