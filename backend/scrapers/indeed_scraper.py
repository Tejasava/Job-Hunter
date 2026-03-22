"""
Indeed Job Scraper
Scrapes job listings from Indeed.com
"""

import logging
from typing import List, Dict, Any, Optional
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)


class IndeedScraper:
    """Scrapes jobs from Indeed"""

    BASE_URL = "https://www.indeed.com/jobs"
    PLATFORM_NAME = "indeed"

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
        Search for jobs on Indeed
        
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
            from bs4 import BeautifulSoup

            for page in range(pages):
                params = {
                    "q": query,
                    "l": location or "",
                    "start": page * 10,
                }

                response = requests.get(
                    self.BASE_URL,
                    params=params,
                    headers=self.headers,
                    timeout=10,
                )
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "html.parser")
                job_cards = soup.find_all("div", class_="job_seen_beacon")

                if not job_cards:
                    break

                for card in job_cards:
                    try:
                        job = self._extract_job_data(card)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.warning(f"Error extracting job data: {e}")
                        continue

                logger.info(f"Found {len(jobs)} jobs on Indeed")

        except Exception as e:
            logger.error(f"Error scraping Indeed: {e}")

        return jobs

    def _extract_job_data(self, card) -> Optional[Dict[str, Any]]:
        """Extract job information from card"""
        try:
            title = card.find("h2", class_="jobTitle")
            company = card.find("span", class_="companyName")
            location = card.find("div", class_="companyLocation")
            salary = card.find("div", class_="salary-snippet")
            snippet = card.find("div", class_="job-snippet")

            if not all([title, company]):
                return None

            # Extract apply link
            job_link = title.find("a")
            apply_link = f"https://www.indeed.com{job_link['href']}" if job_link else ""

            job_id = hashlib.md5(apply_link.encode()).hexdigest()

            return {
                "job_id": job_id,
                "title": title.get_text(strip=True),
                "company": company.get_text(strip=True),
                "location": location.get_text(strip=True) if location else "Remote",
                "salary": self._parse_salary(salary.get_text() if salary else ""),
                "description": snippet.get_text(strip=True) if snippet else "",
                "apply_link": apply_link,
                "source": self.PLATFORM_NAME,
                "posted_date": datetime.utcnow(),
                "job_type": "Full-time",
            }

        except Exception as e:
            logger.warning(f"Error extracting job: {e}")
            return None

    def _parse_salary(self, salary_text: str) -> Optional[int]:
        """Extract salary in LPA from text"""
        import re

        # Look for salary patterns
        pattern = r"₹?\s*(\d+(?:,\d+)?)\s*(?:L|Lakh|LPA)"
        match = re.search(pattern, salary_text, re.IGNORECASE)

        if match:
            salary_str = match.group(1).replace(",", "")
            try:
                return int(float(salary_str))
            except ValueError:
                pass

        return None
