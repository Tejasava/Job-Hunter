"""
Naukri Job Scraper
Scrapes job listings from Naukri.com (India's largest job portal)
"""

import logging
from typing import List, Dict, Any, Optional
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)


class NaukriScraper:
    """Scrapes jobs from Naukri"""

    BASE_URL = "https://www.naukri.com/jobs"
    PLATFORM_NAME = "naukri"

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
        Search for jobs on Naukri
        
        Args:
            query: Job title/keywords
            location: Job location (India-specific)
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
                    "k": query,
                    "l": location or "India",
                    "pageNo": page + 1,
                }

                url = f"{self.BASE_URL}-{query.replace(' ', '-')}"
                response = requests.get(
                    url,
                    params=params,
                    headers=self.headers,
                    timeout=10,
                )
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "html.parser")
                job_cards = soup.find_all("article", class_="jobTuple")

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

                logger.info(f"Found {len(jobs)} jobs on Naukri")

        except Exception as e:
            logger.error(f"Error scraping Naukri: {e}")

        return jobs

    def _extract_job_data(self, card) -> Optional[Dict[str, Any]]:
        """Extract job information from card"""
        try:
            title = card.find("a", class_="jobTitle")
            company = card.find("a", class_="companyName")
            location = card.find("span", class_="locWid")
            salary = card.find("span", class_="sal")
            job_description = card.find("span", class_="job-description")

            if not all([title, company]):
                return None

            apply_link = title.get("href", "") if title else ""
            if apply_link and not apply_link.startswith("http"):
                apply_link = f"https://www.naukri.com{apply_link}"

            job_id = hashlib.md5(apply_link.encode()).hexdigest()

            return {
                "job_id": job_id,
                "title": title.get_text(strip=True) if title else "",
                "company": company.get_text(strip=True) if company else "",
                "location": location.get_text(strip=True) if location else "India",
                "salary": self._parse_naukri_salary(salary.get_text() if salary else ""),
                "description": job_description.get_text(strip=True)
                if job_description
                else "",
                "apply_link": apply_link,
                "source": self.PLATFORM_NAME,
                "posted_date": datetime.utcnow(),
                "job_type": "Full-time",
            }

        except Exception as e:
            logger.warning(f"Error extracting job: {e}")
            return None

    def _parse_naukri_salary(self, salary_text: str) -> Optional[int]:
        """Extract salary in LPA from Naukri format"""
        import re

        # Naukri format: "5-10 L p.a." or "₹5L p.a."
        pattern = r"([\d.]+)\s*(?:-\s*([\d.]+))?\s*[L|Lakh]"
        match = re.search(pattern, salary_text, re.IGNORECASE)

        if match:
            try:
                min_salary = float(match.group(1))
                max_salary = float(match.group(2)) if match.group(2) else min_salary
                avg_salary = (min_salary + max_salary) / 2
                return int(avg_salary)
            except (ValueError, TypeError):
                pass

        return None
