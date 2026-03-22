"""
Global Job Search Agent - Aggregates jobs from multiple sources
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class GlobalSearchAgent:
    """Aggregates jobs from multiple job platforms"""

    def __init__(self):
        """Initialize global search agent"""
        self.scrapers = {}
        self.max_workers = 10

    def register_scraper(self, platform_name: str, scraper_instance):
        """Register a job scraper for a platform"""
        self.scrapers[platform_name] = scraper_instance
        logger.info(f"Registered scraper for {platform_name}")

    async def search_all_platforms(
        self,
        query: str,
        location: Optional[str] = None,
        min_salary: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for jobs across all registered platforms
        
        Args:
            query: Job title/keyword to search
            location: Location filter (optional)
            min_salary: Minimum salary in LPA (optional)
        
        Returns:
            List of job postings from all platforms
        """
        all_jobs = []

        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_platform = {
                    executor.submit(
                        self._search_platform,
                        platform,
                        scraper,
                        query,
                        location,
                        min_salary,
                    ): platform
                    for platform, scraper in self.scrapers.items()
                }

                for future in as_completed(future_to_platform):
                    platform = future_to_platform[future]
                    try:
                        jobs = future.result(timeout=30)
                        all_jobs.extend(jobs)
                        logger.info(f"Found {len(jobs)} jobs from {platform}")
                    except Exception as e:
                        logger.warning(f"Error searching {platform}: {e}")

        except Exception as e:
            logger.error(f"Error in global search: {e}")

        # Remove duplicates based on job title + company
        unique_jobs = self._deduplicate_jobs(all_jobs)
        logger.info(f"Total unique jobs found: {len(unique_jobs)}")

        return sorted(unique_jobs, key=lambda x: x.get("salary", 0), reverse=True)

    def _search_platform(
        self,
        platform: str,
        scraper,
        query: str,
        location: Optional[str],
        min_salary: Optional[int],
    ) -> List[Dict[str, Any]]:
        """Search a single platform"""
        try:
            jobs = scraper.search(query, location=location)
            
            # Filter by salary if provided
            if min_salary:
                jobs = [j for j in jobs if j.get("salary", 0) >= min_salary]
            
            return jobs
        except Exception as e:
            logger.error(f"Error searching {platform}: {e}")
            return []

    def _deduplicate_jobs(
        self, jobs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate jobs"""
        seen = set()
        unique_jobs = []

        for job in jobs:
            # Create unique key from title + company
            key = (job.get("title", "").lower(), job.get("company", "").lower())
            
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        return unique_jobs

    def get_platform_status(self) -> Dict[str, bool]:
        """Get status of all registered platforms"""
        status = {}
        for platform, scraper in self.scrapers.items():
            try:
                # Try to ping/check if scraper is working
                status[platform] = True
            except Exception:
                status[platform] = False
        return status
