"""
Telegram Bot Commands
Main command handlers for the bot
"""

import logging
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    welcome_message = f"""
Welcome to 🤖 AI Job Hunter Agent!

Hi {user_name}! I'm your personal AI-powered job search assistant.

I can help you:
✅ Search for jobs globally across 50+ platforms
✅ Filter jobs by your salary requirements
✅ Analyze job descriptions with AI
✅ Generate tailored resumes for each job
✅ Identify skill gaps and suggest learning resources
✅ Automatically apply to jobs (with your confirmation)
✅ Track all your applications

Available Commands:
/profile - Setup your profile
/jobs <salary> <role> - Search for jobs (e.g., /jobs 12 AI Engineer)
/salary <amount> - Set minimum salary in LPA
/skills - View and update your skills
/status - Check job application status
/applications - View all your applications
/help - Get more information

Let's get started! First, set up your profile:
"""

    keyboard = [
        [InlineKeyboardButton("📋 Setup Profile", callback_data="setup_profile")],
        [InlineKeyboardButton("🔍 Search Jobs", callback_data="search_jobs")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_message, reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_message = """
🤖 AI Job Hunter Agent - Help

COMMANDS:

/start - Welcome and main menu
/profile - Setup/update your profile
/jobs <salary> <role> - Search for jobs
  Example: /jobs 12 Python Developer
  
/salary <amount> - Set minimum salary bar in LPA
  Example: /salary 15
  
/skills - View and update your skills

/status - Check job search and application status

/applications - View all applications with status

FEATURES:

🌍 Global Job Search
- Searches across LinkedIn, Indeed, Naukri, RemoteOK, GitHub Jobs, and more
- Filters by salary, location, and job type

🤖 AI Job Analysis
- Analyzes job descriptions with AI
- Extracts required skills and responsibilities
- Calculates match score with your skills

📄 Smart Resume Generation
- Generates tailored resumes for each job
- Optimizes for ATS (Applicant Tracking Systems)
- Customizes based on job requirements

🧠 Skill Gap Analysis
- Compares your skills with job requirements
- Suggests learning resources
- Creates learning roadmaps

🚀 Auto-Apply (with confirmation)
- Automatically fills application forms
- Uploads your resume
- Requires your confirmation before applying

📊 Application Tracking
- Tracks all applications
- Shows status and dates
- Maintains history for future reference

WORKFLOW:

1️⃣ Setup your profile (/profile)
2️⃣ Search for jobs (/jobs)
3️⃣ Review job details with AI analysis
4️⃣ Press "Apply" to generate a tailored resume
5️⃣ Confirm and auto-apply
6️⃣ Track applications (/applications)

TIPS:

💡 Set a salary bar to filter jobs faster
💡 Update skills to get better job matches
💡 Review skill gaps to identify learning priorities
💡 Save interesting jobs for later

Need more help? Contact support or check our documentation.
"""

    await update.message.reply_text(help_message)


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /profile command"""
    user_id = update.effective_user.id

    profile_message = """
👤 Profile Setup

Let's create your profile for job matching and resume generation.

I'll ask you the following information:
1️⃣ Full Name
2️⃣ Email
3️⃣ Phone Number
4️⃣ Current Role
5️⃣ Years of Experience
6️⃣ Technical Skills
7️⃣ Education
8️⃣ Preferred Locations
9️⃣ Preferred Job Roles

This information will be used to:
✅ Match you with suitable jobs
✅ Generate tailored resumes
✅ Identify skill gaps
✅ Auto-fill application forms

Ready to get started?
"""

    keyboard = [
        [InlineKeyboardButton("✅ Start Profile Setup", callback_data="start_profile")],
        [InlineKeyboardButton("👁️ View Current Profile", callback_data="view_profile")],
        [
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(profile_message, reply_markup=reply_markup)


async def salary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /salary command"""
    try:
        if not context.args:
            await update.message.reply_text(
                "Please provide a salary amount in LPA.\nExample: /salary 12"
            )
            return

        salary = int(context.args[0])
        user_id = update.effective_user.id

        # Save salary bar to database
        from backend.database.mongo import get_db

        db = get_db()
        db.update_user_salary_bar(user_id, salary)

        await update.message.reply_text(
            f"✅ Salary bar set to {salary} LPA!\n\n"
            f"I'll now only show you jobs with salary >= {salary} LPA."
        )

    except (ValueError, IndexError):
        await update.message.reply_text(
            "Invalid salary format. Please use: /salary 12"
        )


async def jobs_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /jobs command"""
    if len(context.args) < 2:
        await update.message.reply_text(
            "Please provide salary and role.\n"
            "Example: /jobs 12 AI Engineer\n"
            "or: /jobs 10 \"Full Stack Developer\""
        )
        return

    try:
        salary_bar = int(context.args[0])
        job_role = " ".join(context.args[1:])

        await update.message.reply_text(
            f"🔍 Searching for {job_role} roles with salary >= {salary_bar} LPA...\n"
            "This may take a minute..."
        )

        # Trigger job search
        context.user_data["search_query"] = job_role
        context.user_data["salary_bar"] = salary_bar

        # Update context to process search
        context.user_data["waiting_for_search_results"] = True

    except ValueError:
        await update.message.reply_text("Invalid salary. Please use: /jobs 12 AI Engineer")


async def applications_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /applications command"""
    user_id = update.effective_user.id

    try:
        from backend.database.mongo import get_db

        db = get_db()
        applications = db.get_user_applications(user_id)

        if not applications:
            await update.message.reply_text(
                "You haven't applied to any jobs yet.\n\n"
                "Start by searching for jobs: /jobs 12 AI Engineer"
            )
            return

        message = "📊 Your Applications\n\n"

        for app in applications[:10]:  # Show last 10 applications
            status_emoji = {
                "pending": "⏳",
                "applied": "✅",
                "rejected": "❌",
                "interview": "🎤",
                "offer": "🎉",
                "accepted": "👍",
            }.get(app.get("status"), "❓")

            message += (
                f"{status_emoji} {app.get('job_title', 'Job')}\n"
                f"   Company: {app.get('company', 'Unknown')}\n"
                f"   Status: {app.get('status', 'pending')}\n"
                f"   Applied: {app.get('applied_at', 'N/A')}\n\n"
            )

        if len(applications) > 10:
            message += f"... and {len(applications) - 10} more applications"

        await update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Error retrieving applications: {e}")
        await update.message.reply_text("Error retrieving applications. Please try again.")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command"""
    user_id = update.effective_user.id

    try:
        from backend.database.mongo import get_db

        db = get_db()
        user_profile = db.get_user_profile(user_id)
        applications = db.get_user_applications(user_id)

        if not user_profile:
            await update.message.reply_text(
                "❌ No profile found. Please setup your profile first: /profile"
            )
            return

        status_message = "📈 Your Job Search Status\n\n"
        status_message += f"👤 Profile: Complete\n"
        status_message += f"💰 Salary Bar: {user_profile.get('salary_bar_lpa', 10)} LPA\n"
        status_message += f"🎯 Skills: {len(user_profile.get('skills', []))} skills\n"
        status_message += f"📝 Applications: {len(applications)} total\n\n"

        # Count by status
        status_counts = {}
        for app in applications:
            status = app.get("status", "pending")
            status_counts[status] = status_counts.get(status, 0) + 1

        status_message += "Application Breakdown:\n"
        for status, count in status_counts.items():
            status_message += f"  {status.capitalize()}: {count}\n"

        await update.message.reply_text(status_message)

    except Exception as e:
        logger.error(f"Error getting status: {e}")
        await update.message.reply_text("Error retrieving status. Please try again.")
