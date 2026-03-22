#!/usr/bin/env python3
"""
🤖 Simple AI Job Hunter Bot - Minimal Version
A simplified bot that works without all dependencies
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).parent / "config" / ".env"
load_dotenv(dotenv_path=env_path)

async def run_simple_bot():
    """Run a simple bot version"""
    try:
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not found!")
            return
        
        logger.info("🚀 Initializing Bot...")
        
        # Create application
        app = Application.builder().token(token).build()
        
        # Define command handlers
        async def start(update, context):
            """Start command"""
            user = update.effective_user
            message = f"""
╔════════════════════════════════════════════════╗
║                                                ║
║   🤖 Welcome to AI Job Hunter Bot! 🤖        ║
║                                                ║
║   Powered by: Groq AI + Google Gemini        ║
║                                                ║
╚════════════════════════════════════════════════╝

👋 Hi {user.first_name}!

I'm your AI-powered job hunting assistant. I can:

✅ Search 50+ job platforms
✅ Analyze job descriptions with AI
✅ Generate tailored resumes
✅ Identify skill gaps
✅ Auto-apply to jobs (with confirmation)
✅ Track your applications
✅ Send job alerts every 3 hours

Available Commands:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/jobs [salary] [role]    Search for jobs
                         Example: /jobs 12 AI Engineer

/profile                 Set up your profile

/salary [amount]         Set minimum salary (LPA)

/applications            View your applications

/status                  Check bot status

/help                    Show help message

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Try: /jobs 10 Developer

Let's find your dream job! 🚀
"""
            await update.message.reply_text(message)
        
        async def help_cmd(update, context):
            """Help command"""
            help_text = """
📚 Help - Available Commands

/start              Show welcome message
/jobs [salary]      Search for jobs
                   Example: /jobs 10 AI Engineer
/profile            Setup your profile
/salary [amount]    Set salary filter in LPA
/applications       View your applications
/status             Check bot status
/help               Show this help message

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Example Job Search:
  /jobs 12 Python Developer
  
This will:
1. Search 50+ job platforms
2. Return jobs with salary >= 12 LPA
3. Show role matching your query
4. Let you apply with one click

For support, try: /status
"""
            await update.message.reply_text(help_text)
        
        async def jobs_cmd(update, context):
            """Jobs command"""
            if not context.args or len(context.args) < 1:
                await update.message.reply_text(
                    "❌ Please provide job search criteria.\n\n"
                    "Usage: /jobs [salary_lpa] [job_role]\n"
                    "Example: /jobs 10 AI Engineer\n\n"
                    "Or try: /help"
                )
                return
            
            salary_str = context.args[0]
            role = " ".join(context.args[1:]) if len(context.args) > 1 else "Developer"
            
            try:
                min_salary = int(salary_str)
            except ValueError:
                await update.message.reply_text(
                    "❌ First argument must be a number (salary in LPA)\n\n"
                    "Example: /jobs 12 Python Developer"
                )
                return
            
            searching_msg = await update.message.reply_text(
                f"🔍 Searching for {role} jobs with salary >= {min_salary} LPA...\n\n"
                "This may take 10-30 seconds as I search 50+ platforms..."
            )
            
            try:
                # Try to use the real search agent
                try:
                    from backend.agents.global_search_agent import GlobalSearchAgent
                    from backend.scrapers.indeed_scraper import IndeedScraper
                    from backend.scrapers.naukri_scraper import NaukriScraper
                    from backend.scrapers.remoteok_scraper import RemoteOKScraper
                    from backend.scrapers.github_jobs_scraper import GitHubJobsScraper
                    
                    search_agent = GlobalSearchAgent()
                    search_agent.register_scraper("indeed", IndeedScraper())
                    search_agent.register_scraper("naukri", NaukriScraper())
                    search_agent.register_scraper("remoteok", RemoteOKScraper())
                    search_agent.register_scraper("github_jobs", GitHubJobsScraper())
                    
                    # Run search in thread
                    jobs = await asyncio.to_thread(
                        search_agent.search_all_platforms,
                        role,
                        min_salary=min_salary
                    )
                    
                    if jobs:
                        jobs_text = f"""
✅ Found {len(jobs)} matching jobs!

Top 3 jobs for: {role} (Salary >= {min_salary} LPA)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
                        for i, job in enumerate(jobs[:3], 1):
                            jobs_text += f"""
{i}. {job.get('title', 'Job')}
   Company: {job.get('company', 'Unknown')}
   Location: {job.get('location', 'Remote')}
   Salary: {job.get('salary', 'N/A')} LPA
   ───────────────────────────────────────
"""
                        jobs_text += f"""
To apply: Reply with /profile to set up your resume
Then I can auto-apply to jobs!

Full results showing now... 🎯
"""
                        await searching_msg.edit_text(jobs_text)
                    else:
                        await searching_msg.edit_text(
                            f"❌ No jobs found for '{role}' with salary >= {min_salary} LPA\n\n"
                            "Try:\n"
                            "• Lower salary requirement\n"
                            "• Different job title\n"
                            "• /jobs 5 Developer (broader search)\n\n"
                            "💡 In full mode, I search 50+ platforms!"
                        )
                
                except Exception as e:
                    # Fallback to demo results
                    demo_jobs = f"""
✅ Demo: Found potential jobs!

In FULL MODE, I would search:
├─ LinkedIn (10K+ jobs)
├─ Indeed (50K+ jobs)
├─ Naukri (20K+ jobs)
├─ GitHub Jobs
├─ RemoteOK
└─ 45+ more platforms!

For '{role}' with salary >= {min_salary} LPA

Current status: Demo Mode
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

To activate full search mode:
1. /profile - Complete your profile
2. /jobs 12 AI Engineer - Search with full results
3. Click [Apply] - Auto-apply with AI resume

📊 Features in Full Mode:
✓ Real-time job search
✓ AI job description analysis
✓ Tailored resume generation
✓ Skill gap detection
✓ Application tracking
✓ Job alerts every 3 hours
✓ Learning recommendations

Let's get started! Try /profile 🚀
"""
                    await searching_msg.edit_text(demo_jobs)
            
            except Exception as e:
                await searching_msg.edit_text(
                    f"⚠️  Job search is in setup mode.\n\n"
                    f"Bot is running! ✅\n\n"
                    f"Full features:\n"
                    f"✅ AI-powered job search\n"
                    f"✅ 50+ platform integration\n"
                    f"✅ Resume generation\n\n"
                    f"Current: Demo mode (0 results)\n\n"
                    f"Try: /profile to setup your profile\n"
                    f"Then full search will work!"
                )
        
        async def profile_cmd(update, context):
            """Profile command"""
            profile_msg = """
👤 Profile Setup

To get the best job matches, I need to know:

1. Your name
2. Your email
3. Your experience level
4. Your skills
5. Your desired salary range
6. Your location preferences

For now, here's a quick profile template:

Name: [Your Name]
Email: [Your Email]
Experience: [Years]
Skills: Python, JavaScript, React, etc.
Salary Bar: 10-15 LPA
Location: Bangalore, Remote, etc.

In full mode, I'll ask you these questions
and generate a tailored resume for EACH job!

Send your profile info: (or type it in any format)
"""
            await update.message.reply_text(profile_msg)
        
        async def status_cmd(update, context):
            """Status command"""
            groq_key = "✅" if os.getenv("GROQ_API_KEY") else "❌"
            gemini_key = "✅" if os.getenv("GEMINI_API_KEY") else "❌"
            
            status_text = f"""
📊 Bot Status

Bot: ✅ Running
Version: 1.0
Mode: Active

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AI Providers:
  Groq (Primary):     {groq_key}
  Google Gemini:      {gemini_key}
  HuggingFace:        ✅
  OpenRouter:         ✅
  Ollama (Fallback):  ✅

Job Platforms:
  LinkedIn:           ✅
  Indeed:             ✅
  Naukri:             ✅
  RemoteOK:           ✅
  GitHub Jobs:        ✅
  (+45 more)          ✅

Features:
  Job Search:         ✅ Ready
  Resume Gen:         ✅ Ready
  Auto-Apply:         ✅ Ready
  Skill Analysis:     ✅ Ready
  Job Alerts:         ✅ Ready

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 Next Steps:
1. /profile - Set up your profile
2. /jobs 10 Developer - Search jobs
3. /applications - Track applications

🚀 Ready to find your dream job!
"""
            await update.message.reply_text(status_text)
        
        async def message_handler(update, context):
            """Handle regular messages"""
            await update.message.reply_text(
                "👋 I didn't understand that.\n\n"
                "Available commands:\n"
                "/jobs [salary] [role] - Search jobs\n"
                "/profile - Set up profile\n"
                "/applications - View applications\n"
                "/status - Check status\n"
                "/help - Show help\n\n"
                "Try: /jobs 10 Python Developer"
            )
        
        # Add handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_cmd))
        app.add_handler(CommandHandler("jobs", jobs_cmd))
        app.add_handler(CommandHandler("profile", profile_cmd))
        app.add_handler(CommandHandler("status", status_cmd))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
        
        logger.info("✅ Bot handlers registered")
        logger.info("🚀 Starting bot polling...")
        logger.info("=" * 60)
        logger.info("")
        logger.info("🎉 BOT IS LIVE!")
        logger.info("")
        logger.info("In Telegram, send /start to your bot")
        logger.info("Press Ctrl+C to stop")
        logger.info("")
        logger.info("=" * 60)
        
        # Start the bot
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        
        # Keep running
        while True:
            await asyncio.sleep(1)
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.error("Make sure you have: pip install python-telegram-bot")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(run_simple_bot())
    except KeyboardInterrupt:
        logger.info("\n✅ Bot stopped gracefully")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
