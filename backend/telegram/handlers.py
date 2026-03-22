"""
Telegram Bot Button Handlers
Handles inline button callbacks
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

logger = logging.getLogger(__name__)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    if callback_data == "setup_profile":
        await handle_setup_profile(query, context)
    elif callback_data == "start_profile":
        await handle_start_profile_questions(query, context)
    elif callback_data == "view_profile":
        await handle_view_profile(query, context)
    elif callback_data.startswith("apply_job_"):
        await handle_apply_job(query, context, callback_data)
    elif callback_data.startswith("skip_job_"):
        await handle_skip_job(query, context, callback_data)
    elif callback_data.startswith("save_job_"):
        await handle_save_job(query, context, callback_data)
    elif callback_data == "confirm_apply":
        await handle_confirm_apply(query, context)
    elif callback_data == "cancel_apply":
        await handle_cancel_apply(query, context)
    elif callback_data == "search_jobs":
        await handle_search_jobs(query, context)
    elif callback_data == "help":
        await handle_help(query, context)
    elif callback_data == "cancel":
        await query.edit_message_text("✅ Cancelled.")
    else:
        await query.edit_message_text("Unknown action.")


async def handle_setup_profile(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle profile setup initiation"""
    message = "Let's set up your profile!\n\nPlease enter your information step by step.\n\nStart with: What is your first name?"

    context.user_data["profile_setup"] = True
    context.user_data["profile_step"] = "first_name"

    await query.edit_message_text(message)


async def handle_start_profile_questions(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start asking profile setup questions"""
    message = (
        "Let's create your profile! 📝\n\n"
        "I'll ask you a series of questions.\n"
        "Just reply with the information when asked.\n\n"
        "Question 1️⃣: What is your first name?"
    )

    context.user_data["profile_setup"] = True
    context.user_data["profile_step"] = "first_name"
    context.user_data["profile_data"] = {}

    await query.edit_message_text(message)


async def handle_view_profile(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View current profile"""
    user_id = query.from_user.id

    try:
        from backend.database.mongo import get_db

        db = get_db()
        profile = db.get_user_profile(user_id)

        if not profile:
            await query.edit_message_text(
                "❌ No profile found. Setup your profile first!"
            )
            return

        message = "👤 Your Current Profile:\n\n"
        message += f"Name: {profile.get('first_name')} {profile.get('last_name')}\n"
        message += f"Email: {profile.get('email')}\n"
        message += f"Phone: {profile.get('phone')}\n"
        message += f"Current Role: {profile.get('current_role')}\n"
        message += f"Experience: {profile.get('experience_years')} years\n"
        message += f"Skills: {', '.join(profile.get('skills', []))}\n"
        message += f"Salary Bar: {profile.get('salary_bar_lpa')} LPA\n"

        keyboard = [
            [InlineKeyboardButton("✏️ Edit Profile", callback_data="setup_profile")],
            [InlineKeyboardButton("❌ Close", callback_data="cancel")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(message, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error viewing profile: {e}")
        await query.edit_message_text("Error retrieving profile. Please try again.")


async def handle_apply_job(query, context: ContextTypes.DEFAULT_TYPE, callback_data: str) -> None:
    """Handle apply button for a job"""
    job_id = callback_data.replace("apply_job_", "")

    try:
        # Get job details
        from backend.database.mongo import get_db

        db = get_db()
        job = db.get_job(job_id)

        if not job:
            await query.edit_message_text("❌ Job not found.")
            return

        user_id = query.from_user.id
        user_profile = db.get_user_profile(user_id)

        if not user_profile:
            await query.edit_message_text(
                "❌ Please complete your profile first: /profile"
            )
            return

        # Generate resume
        await query.edit_message_text(
            f"📄 Generating tailored resume for {job.get('company')}...\n"
            "Please wait..."
        )

        from backend.resume.resume_generator import ResumeGenerator

        resume_gen = ResumeGenerator()
        result = await resume_gen.generate_resume(
            user_profile,
            job.get("description", ""),
            job.get("required_skills", []),
            job_id,
            job.get("company", ""),
        )

        if result.get("success"):
            # Store job and resume for confirmation
            context.user_data["pending_application"] = {
                "job_id": job_id,
                "job_title": job.get("title"),
                "company": job.get("company"),
                "resume_path": result.get("resume_path"),
                "apply_link": job.get("apply_link"),
            }

            message = (
                f"✅ Resume generated!\n\n"
                f"Job: {job.get('title')}\n"
                f"Company: {job.get('company')}\n"
                f"Location: {job.get('location')}\n"
                f"Salary: {job.get('salary', 'N/A')} LPA\n\n"
                f"Ready to apply?"
            )

            keyboard = [
                [InlineKeyboardButton("✅ Confirm Apply", callback_data="confirm_apply")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_apply")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(message, reply_markup=reply_markup)

        else:
            # Handle missing information
            missing_fields = result.get("missing_fields", [])
            if missing_fields:
                message = (
                    "⚠️ Missing Information\n\n"
                    "To generate a resume, I need the following information:\n"
                )
                for field in missing_fields:
                    message += f"• {field}\n"

                message += "\nPlease update your profile: /profile"
                await query.edit_message_text(message)
            else:
                await query.edit_message_text(
                    f"❌ Error: {result.get('error', 'Could not generate resume')}"
                )

    except Exception as e:
        logger.error(f"Error applying to job: {e}")
        await query.edit_message_text(f"❌ Error: {str(e)}")


async def handle_skip_job(query, context: ContextTypes.DEFAULT_TYPE, callback_data: str) -> None:
    """Handle skip button for a job"""
    job_id = callback_data.replace("skip_job_", "")

    await query.edit_message_text(
        "⏭️ Skipped! Here's the next job...\n"
        "(Next job would be fetched and displayed)"
    )


async def handle_save_job(query, context: ContextTypes.DEFAULT_TYPE, callback_data: str) -> None:
    """Handle save job button"""
    job_id = callback_data.replace("save_job_", "")
    user_id = query.from_user.id

    try:
        from backend.database.mongo import get_db

        db = get_db()
        job = db.get_job(job_id)

        if job:
            db.save_job_for_user(user_id, job)
            await query.answer("✅ Job saved for later!")
        else:
            await query.answer("❌ Job not found", show_alert=True)

    except Exception as e:
        logger.error(f"Error saving job: {e}")
        await query.answer("❌ Error saving job", show_alert=True)


async def handle_confirm_apply(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle confirm apply button"""
    application = context.user_data.get("pending_application")

    if not application:
        await query.edit_message_text("❌ No pending application found.")
        return

    try:
        await query.edit_message_text(
            "🚀 Submitting your application...\n"
            "Please wait..."
        )

        from backend.database.mongo import get_db
        from backend.agents.apply_agent import ApplyAgent

        db = get_db()
        apply_agent = ApplyAgent()
        user_id = query.from_user.id
        user_profile = db.get_user_profile(user_id)

        # Attempt auto-apply
        result = await apply_agent.auto_apply(
            application["job_id"],
            application["apply_link"],
            user_profile,
            application["resume_path"],
            application["job_title"],
            application["company"],
        )

        if result.get("status") == "success":
            message = (
                f"✅ Application submitted successfully!\n\n"
                f"Job: {application['job_title']}\n"
                f"Company: {application['company']}\n\n"
                f"Good luck! 🍀"
            )
        else:
            message = (
                f"⚠️ {result.get('message', 'Error submitting application')}\n\n"
                f"You can apply manually here:\n"
                f"{application['apply_link']}"
            )

        # Save application record
        app_record = {
            "user_id": user_id,
            "job_id": application["job_id"],
            "job_title": application["job_title"],
            "company": application["company"],
            "resume_path": application["resume_path"],
            "status": "applied" if result.get("status") == "success" else "pending",
        }
        db.save_application(app_record)

        context.user_data.pop("pending_application", None)
        await query.edit_message_text(message)

    except Exception as e:
        logger.error(f"Error confirming apply: {e}")
        await query.edit_message_text(f"❌ Error: {str(e)}")


async def handle_cancel_apply(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle cancel apply button"""
    context.user_data.pop("pending_application", None)
    await query.edit_message_text("❌ Application cancelled.")


async def handle_search_jobs(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle search jobs button"""
    message = (
        "🔍 Search for Jobs\n\n"
        "Use the command: /jobs <salary> <role>\n\n"
        "Examples:\n"
        "/jobs 12 AI Engineer\n"
        "/jobs 15 Full Stack Developer\n"
        "/jobs 10 Data Scientist\n\n"
        "The salary should be in LPA (Lakhs Per Annum for India)"
    )

    await query.edit_message_text(message)


async def handle_help(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle help button"""
    help_message = (
        "🆘 Help & Support\n\n"
        "Available Commands:\n"
        "/start - Welcome\n"
        "/profile - Setup profile\n"
        "/jobs - Search jobs\n"
        "/salary - Set salary bar\n"
        "/applications - View applications\n"
        "/status - Check status\n"
        "/help - This help message\n\n"
        "For detailed help, use: /help"
    )

    await query.edit_message_text(help_message)
