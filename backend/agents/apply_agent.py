"""
Job Application Agent
Handles automated job applications via browser automation
"""

import logging
import os
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ApplyAgent:
    """Handles automated job applications"""

    def __init__(self):
        self.playwright_available = False
        try:
            from playwright.async_api import async_playwright

            self.async_playwright = async_playwright
            self.playwright_available = True
        except ImportError:
            logger.warning("Playwright not installed. Application automation disabled.")

    async def auto_apply(
        self,
        job_id: str,
        apply_link: str,
        user_profile: Dict[str, Any],
        resume_path: str,
        job_title: str = "",
        company_name: str = "",
    ) -> Dict[str, Any]:
        """
        Attempt to automatically apply to a job
        
        Args:
            job_id: Job ID
            apply_link: Direct application link
            user_profile: User's profile data
            resume_path: Path to generated resume PDF
            job_title: Job title
            company_name: Company name
        
        Returns:
            Application result
        """
        if not self.playwright_available:
            logger.warning("Playwright not available for auto-apply")
            return {
                "status": "pending",
                "message": "Automation not available. Manual application required.",
                "apply_link": apply_link,
            }

        try:
            result = await self._apply_via_automation(
                apply_link, user_profile, resume_path
            )
            return result
        except Exception as e:
            logger.error(f"Error applying to job: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "apply_link": apply_link,
            }

    async def _apply_via_automation(
        self,
        apply_link: str,
        user_profile: Dict[str, Any],
        resume_path: str,
    ) -> Dict[str, Any]:
        """
        Use Playwright to automate application
        """
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            try:
                # Navigate to application page
                await page.goto(apply_link, wait_until="networkidle", timeout=30000)

                # Detect platform and fill form
                await self._fill_application_form(page, user_profile, resume_path)

                # Submit application
                await self._submit_application(page)

                result = {
                    "status": "success",
                    "message": "Application submitted successfully",
                    "applied_at": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Automation error: {e}")
                result = {
                    "status": "partial",
                    "message": f"Application partially completed: {str(e)}",
                    "manual_action_required": True,
                }

            finally:
                await browser.close()

            return result

    async def _fill_application_form(
        self, page, user_profile: Dict[str, Any], resume_path: str
    ) -> bool:
        """
        Fill application form with user data
        """
        try:
            # Try to find and fill email field
            email_fields = await page.query_selector_all(
                'input[type="email"], input[name*="email"]'
            )
            if email_fields:
                await email_fields[0].fill(user_profile.get("email", ""))
                await page.wait_for_timeout(500)

            # Try to find and fill name field
            name_fields = await page.query_selector_all(
                'input[name*="name"], input[placeholder*="Name"]'
            )
            if name_fields:
                full_name = f"{user_profile.get('first_name', '')} {user_profile.get('last_name', '')}"
                await name_fields[0].fill(full_name)
                await page.wait_for_timeout(500)

            # Try to find and fill phone field
            phone_fields = await page.query_selector_all(
                'input[type="tel"], input[name*="phone"]'
            )
            if phone_fields:
                await phone_fields[0].fill(user_profile.get("phone", ""))
                await page.wait_for_timeout(500)

            # Try to upload resume
            if os.path.exists(resume_path):
                file_inputs = await page.query_selector_all('input[type="file"]')
                if file_inputs:
                    await file_inputs[0].set_input_files(resume_path)
                    await page.wait_for_timeout(1000)

            return True

        except Exception as e:
            logger.warning(f"Error filling form: {e}")
            return False

    async def _submit_application(self, page) -> bool:
        """
        Find and click submit button
        """
        try:
            # Try to find submit button
            submit_selectors = [
                'button[type="submit"]',
                'button:has-text("Submit")',
                'button:has-text("Apply")',
                'button:has-text("Send")',
            ]

            for selector in submit_selectors:
                try:
                    button = await page.query_selector(selector)
                    if button:
                        await button.click()
                        await page.wait_for_timeout(2000)
                        return True
                except Exception:
                    continue

            return False

        except Exception as e:
            logger.warning(f"Error submitting application: {e}")
            return False

    def check_application_support(self, apply_link: str) -> bool:
        """
        Check if automation is supported for this job link
        """
        supported_patterns = [
            "linkedin.com",
            "indeed.com",
            "naukri.com",
            "glassdoor.com",
        ]

        return any(pattern in apply_link.lower() for pattern in supported_patterns)
