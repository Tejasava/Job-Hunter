"""
Main Telegram Bot Entry Point
"""

import logging
import os
import asyncio
from datetime import datetime
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ChatAction

from backend.telegram.commands import (
    start_command,
    help_command,
    profile_command,
    salary_command,
    jobs_command,
    applications_command,
    status_command,
)
from backend.telegram.handlers import button_callback
from backend.agents.global_search_agent import GlobalSearchAgent
from backend.agents.jd_analyzer_agent import JDAnalyzerAgent
from backend.database.mongo import get_db
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)

# Conversation states
(
    PROFILE_STEP,
    SEARCH_QUERY,
    SEARCH_LOCATION,
) = range(3)


class TelegramBot:
    """Main Telegram Bot Class"""

    def __init__(self, token: str):
        self.token = token
        self.application = None
        self.global_search_agent = GlobalSearchAgent()
        self.jd_analyzer = JDAnalyzerAgent()
        self.db = get_db()
        self.scheduler = None
        self._setup_scrapers()

    def _setup_scrapers(self):
        """Setup all job scrapers"""
        try:
            from backend.scrapers.indeed_scraper import IndeedScraper
            from backend.scrapers.naukri_scraper import NaukriScraper
            from backend.scrapers.remoteok_scraper import RemoteOKScraper
            from backend.scrapers.github_jobs_scraper import GitHubJobsScraper

            self.global_search_agent.register_scraper("indeed", IndeedScraper())
            self.global_search_agent.register_scraper("naukri", NaukriScraper())
            self.global_search_agent.register_scraper("remoteok", RemoteOKScraper())
            self.global_search_agent.register_scraper("github_jobs", GitHubJobsScraper())

            logger.info("Job scrapers registered successfully")
        except ImportError as e:
            logger.warning(f"Error importing scrapers: {e}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle regular text messages"""
        user_id = update.effective_user.id
        message_text = update.message.text

        # Check if we're in profile setup
        if context.user_data.get("profile_setup"):
            return await self._handle_profile_setup(update, context)

        # Otherwise, acknowledge the message
        await update.message.reply_text(
            "👋 I didn't understand that command.\n\n"
            "Use /help to see available commands."
        )
        return -1

    async def _handle_profile_setup(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Handle profile setup conversation"""
        user_id = update.effective_user.id
        message_text = update.message.text
        step = context.user_data.get("profile_step")
        profile_data = context.user_data.get("profile_data", {})

        # Define conversation flow
        steps = {
            "first_name": ("first_name", "What is your last name?"),
            "last_name": ("last_name", "What is your email address?"),
            "email": ("email", "What is your phone number?"),
            "phone": ("phone", "What is your current job role/title?"),
            "current_role": ("current_role", "How many years of experience do you have?"),
            "experience_years": ("experience_years", "What are your technical skills? (comma-separated)"),
            "skills": ("skills", "What is your education? (e.g., B.Tech CSE, M.Tech)")
        }

        if step in steps:
            field_name, next_question = steps[step]

            # Parse data based on step
            if step == "experience_years":
                try:
                    profile_data[field_name] = int(message_text)
                except ValueError:
                    await update.message.reply_text(
                        "Please enter a valid number for experience."
                    )
                    return PROFILE_STEP
            elif step == "skills":
                profile_data[field_name] = [s.strip() for s in message_text.split(",")]
            else:
                profile_data[field_name] = message_text

            context.user_data["profile_data"] = profile_data

            # Check if we're done with profile setup
            if step == "skills":
                # Save profile to database
                await self._save_profile(user_id, profile_data)
                await update.message.reply_text(
                    "✅ Profile saved successfully!\n\n"
                    "Now you can search for jobs: /jobs 12 AI Engineer"
                )
                context.user_data["profile_setup"] = False
                return -1

            # Ask next question
            context.user_data["profile_step"] = steps[step][0]  # Move to next step
            # Find next step key
            step_keys = list(steps.keys())
            current_idx = step_keys.index(step)
            if current_idx + 1 < len(step_keys):
                next_step = step_keys[current_idx + 1]
                context.user_data["profile_step"] = next_step

            await update.message.reply_text(next_question)
            return PROFILE_STEP

        return -1

    async def _save_profile(self, user_id: int, profile_data: dict):
        """Save profile to database"""
        try:
            profile = {
                "user_id": user_id,
                "first_name": profile_data.get("first_name", ""),
                "last_name": profile_data.get("last_name", ""),
                "email": profile_data.get("email", ""),
                "phone": profile_data.get("phone", ""),
                "current_role": profile_data.get("current_role", ""),
                "experience_years": profile_data.get("experience_years", 0),
                "skills": profile_data.get("skills", []),
                "education": profile_data.get("education", []),
                "salary_bar_lpa": 10,  # Default
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            self.db.save_user_profile(profile)
            logger.info(f"Profile saved for user {user_id}")
        except Exception as e:
            logger.error(f"Error saving profile: {e}")

    async def search_jobs_internal(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, query: str, salary_bar: int
    ):
        """Internal job search handler"""
        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            # Search jobs
            jobs = await asyncio.to_thread(
                self.global_search_agent.search_all_platforms,
                query,
                min_salary=salary_bar
            )

            if not jobs:
                await update.message.reply_text(
                    f"❌ No jobs found for {query} with salary >= {salary_bar} LPA\n\n"
                    "Try adjusting your criteria."
                )
                return

            # Save top jobs to database and send to user
            displayed = 0
            for job in jobs[:5]:  # Show top 5 jobs
                # Save job to database
                self.db.save_job(job)

                # Analyze job description
                try:
                    required_skills = await self.jd_analyzer.extract_required_skills(
                        job.get("description", "")
                    )
                    job["required_skills"] = required_skills
                except Exception as e:
                    logger.warning(f"Error analyzing job: {e}")
                    required_skills = []

                # Create job message
                job_message = f"""
🏢 {job.get('title', 'Job')}
Company: {job.get('company', 'Unknown')}
Location: {job.get('location', 'Remote')}
Salary: {job.get('salary', 'N/A')} LPA
Type: {job.get('job_type', 'Full-time')}

Required Skills: {', '.join(required_skills[:5])}

Apply Link: {job.get('apply_link', 'N/A')}
"""

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "✅ Apply",
                            callback_data=f"apply_job_{job['job_id']}"
                        ),
                        InlineKeyboardButton(
                            "⏭️ Skip",
                            callback_data=f"skip_job_{job['job_id']}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "💾 Save",
                            callback_data=f"save_job_{job['job_id']}"
                        )
                    ],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(job_message, reply_markup=reply_markup)
                displayed += 1

            await update.message.reply_text(
                f"\n✅ Showing {displayed} matching jobs.\n\n"
                f"Press 'Apply' to generate a tailored resume!"
            )

        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            await update.message.reply_text(
                f"❌ Error searching jobs: {str(e)}\n\n"
                "Please try again later."
            )

    async def setup_scheduler(self):
        """Setup APScheduler for periodic job scanning"""
        self.scheduler = AsyncIOScheduler()

        # Scan for new jobs every 3 hours
        self.scheduler.add_job(
            self._periodic_job_scan,
            "interval",
            hours=3,
            id="job_scan"
        )

        self.scheduler.start()
        logger.info("APScheduler started for periodic job scanning")

    async def _periodic_job_scan(self):
        """Periodically scan for new jobs and notify users"""
        logger.info("Running periodic job scan...")
        # This would fetch recent jobs and notify subscribed users
        # Implementation depends on user subscription management

    def setup_handlers(self):
        """Setup all message and command handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("profile", profile_command))
        self.application.add_handler(CommandHandler("salary", salary_command))
        self.application.add_handler(CommandHandler("jobs", jobs_command))
        self.application.add_handler(CommandHandler("applications", applications_command))
        self.application.add_handler(CommandHandler("status", status_command))

        # Conversation handler for profile setup
        profile_conv = ConversationHandler(
            entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)],
            states={
                PROFILE_STEP: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
                ],
            },
            fallbacks=[CommandHandler("cancel", self.handle_message)],
        )

        self.application.add_handler(profile_conv)

        # Button callbacks
        self.application.add_handler(CallbackQueryHandler(button_callback))

        # Message handler
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start(self):
        """Start the bot"""
        self.application = Application.builder().token(self.token).build()

        self.setup_handlers()

        logger.info("Starting Telegram Bot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

    async def stop(self):
        """Stop the bot"""
        if self.scheduler:
            self.scheduler.shutdown()
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
        logger.info("Bot stopped")


async def main():
    """Main entry point"""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in environment")

    bot = TelegramBot(token)

    try:
        await bot.start()
        await bot.setup_scheduler()

        # Keep running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
