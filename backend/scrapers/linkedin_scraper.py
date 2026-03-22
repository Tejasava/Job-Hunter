"""
LinkedIn Job Scraper
Scrapes job listings from LinkedIn
"""

import logging
from typing import List, Dict, Any, Optional
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)


class LinkedInScraper:
    """Scrapes jobs from LinkedIn"""

    BASE_URL = "https://www.linkedin.com/jobs/search"
    PLATFORM_NAME = "linkedin"

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
        Search for jobs on LinkedIn
        
        Note: LinkedIn has strong anti-scraping measures.
        This uses the official LinkedIn Jobs search parameters.
        
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
                    "keywords": query,
                    "location": location or "",
                    "pageNum": page,
                }

                response = requests.get(
                    self.BASE_URL,
                    params=params,
                    headers=self.headers,
                    timeout=10,
                )
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "html.parser")
                # LinkedIn uses dynamic JS, so this will have limited success
                job_cards = soup.find_all("div", class_="base-card")

                if not job_cards:
                    logger.warning(
                        "LinkedIn returned no results. LinkedIn has strong anti-scraping measures."
                    )
                    break

                for card in job_cards:
                    try:
                        job = self._extract_job_data(card)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.warning(f"Error extracting job data: {e}")
                        continue

            logger.info(f"Found {len(jobs)} jobs on LinkedIn")

        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {e}")
            logger.info(
                "Note: Consider using LinkedIn API or Selenium for better results"
            )

        return jobs

    def _extract_job_data(self, card) -> Optional[Dict[str, Any]]:
        """Extract job information from card"""
        try:
            title = card.find("h3", class_="base-search-card__title")
            company = card.find("h4", class_="base-search-card__subtitle")
            location = card.find("span", class_="job-search-card__location")
            link = card.find("a", class_="base-card__full-link")

            if not all([title, company]):
                return None

            apply_link = link.get("href", "") if link else ""

            job_id = hashlib.md5(apply_link.encode()).hexdigest()

            return {
                "job_id": job_id,
                "title": title.get_text(strip=True),
                "company": company.get_text(strip=True),
                "location": location.get_text(strip=True) if location else "Remote",
                "salary": None,  # LinkedIn requires authentication for salary data
                "description": "",  # Requires separate page load
                "apply_link": apply_link,
                "source": self.PLATFORM_NAME,
                "posted_date": datetime.utcnow(),
                "job_type": "Full-time",
            }

        except Exception as e:
            logger.warning(f"Error extracting job: {e}")
            return None
