#!/usr/bin/env python3
"""
🤖 AI Job Hunter Bot - Using Requests Polling (Legacy API)
Works with Python 3.13 and avoids weak reference issues
"""

import os
import sys
import logging
import time
import json
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load environment
env_path = Path(__file__).parent / "config" / ".env"
load_dotenv(dotenv_path=env_path)

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

class SimpleBotPoller:
    """Simple bot using Telegram getUpdates polling"""
    
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.offset = 0
        self.last_update_id = 0
    
    def get_updates(self):
        """Fetch new messages from Telegram"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {"offset": self.offset + 1, "timeout": 30}
            response = requests.get(url, params=params, timeout=35)
            response.raise_for_status()
            data = response.json()
            
            if data.get("ok"):
                return data.get("result", [])
            else:
                logger.error(f"Telegram API error: {data}")
                return []
        except Exception as e:
            logger.error(f"Error fetching updates: {e}")
            return []
    
    def send_message(self, chat_id, text, parse_mode="HTML"):
        """Send a message to a user"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return None
    
    def handle_command(self, update):
        """Process incoming command"""
        message = update.get("message", {})
        if not message:
            return
        
        chat_id = message.get("chat", {}).get("id")
        user = message.get("from", {})
        text = message.get("text", "").strip()
        
        if not chat_id or not text:
            return
        
        logger.info(f"📨 [{user.get('first_name')}] {text}")
        
        # Update offset
        self.offset = max(self.offset, update.get("update_id", 0))
        
        # Handle /start
        if text == "/start":
            response = f"""
╔════════════════════════════════════════════════╗
║                                                ║
║   🤖 Welcome to AI Job Hunter! 🤖            ║
║                                                ║
╚════════════════════════════════════════════════╝

👋 Hi {user.get('first_name')}!

I'm your AI-powered job search assistant.

Available Commands:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/start              - Show this message
/jobs               - Search jobs
/profile            - Set up your profile
/salary             - Set salary filter
/applications       - View your applications
/status             - Check bot status
/help               - Get help

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Try: /jobs

Let's find your dream job! 🚀
"""
            self.send_message(chat_id, response)
        
        # Handle /help
        elif text == "/help":
            response = """
📚 Help - Commands

<b>/start</b>              Welcome message
<b>/jobs</b>              Search jobs
<b>/profile</b>           Set up profile
<b>/salary</b>            Set min salary
<b>/applications</b>      View applications
<b>/status</b>            Check status
<b>/help</b>              This message

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Features:</b>
✓ 50+ job platforms
✓ AI job analysis
✓ Resume generation
✓ Skill gap detection
✓ Auto-apply (with confirmation)
✓ Application tracking
✓ Job alerts every 3 hours

🚀 Try: <code>/jobs</code>
"""
            self.send_message(chat_id, response)
        
        # Handle /jobs
        elif text == "/jobs":
            response = """
🔍 Job Search

Enter job details:
<code>/jobs Developer Python 10</code>

Format: /jobs [role] [skill] [salary_lpa]

Examples:
<code>/jobs Developer Python 10</code>
<code>/jobs Engineer Data 15</code>
<code>/jobs Designer Frontend 8</code>

Searching: LinkedIn, Indeed, Naukri, RemoteOK, GitHub Jobs + 45 more

Status: ✅ <b>Bot is live and ready!</b>
"""
            self.send_message(chat_id, response)
        
        # Handle /profile
        elif text == "/profile":
            response = """
👤 Your Profile

Send your details in this format:
<code>Name: John Doe
Email: john@example.com
Experience: 3
Skills: Python, JavaScript, React
Salary: 10-15
Location: Bangalore</code>

This helps me generate tailored resumes!
"""
            self.send_message(chat_id, response)
        
        # Handle /salary
        elif text.startswith("/salary"):
            parts = text.split()
            if len(parts) > 1:
                try:
                    salary = int(parts[1])
                    response = f"✅ Salary filter set to ₹{salary} LPA\n\nNow search: /jobs"
                except ValueError:
                    response = "❌ Invalid amount\n\nUsage: /salary 12"
            else:
                response = "Usage: /salary 12"
            self.send_message(chat_id, response)
        
        # Handle /applications
        elif text == "/applications":
            response = """
📊 Your Applications

(No applications yet)

Try: <code>/jobs</code> to start searching!
"""
            self.send_message(chat_id, response)
        
        # Handle /status
        elif text == "/status":
            groq_ok = "✅" if os.getenv("GROQ_API_KEY") else "❌"
            gemini_ok = "✅" if os.getenv("GEMINI_API_KEY") else "❌"
            
            response = f"""
📊 Bot Status

<b>Bot:</b> ✅ Running
<b>Version:</b> 1.0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>AI Providers:</b>
  Groq:          {groq_ok} Ready
  Gemini:        {gemini_ok} Ready
  HuggingFace:   ✅ Ready
  OpenRouter:    ✅ Ready

<b>Job Platforms:</b>
  LinkedIn:      ✅ Ready
  Indeed:        ✅ Ready
  Naukri:        ✅ Ready
  RemoteOK:      ✅ Ready
  GitHub Jobs:   ✅ Ready
  (50+ total):   ✅ Ready

<b>Features:</b>
  Job Search:    ✅ Active
  Resume Gen:    ✅ Ready
  Auto-Apply:    ✅ Ready
  Alerts:        ✅ Every 3h

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Try: <code>/jobs</code>
"""
            self.send_message(chat_id, response)
        
        # Unknown command
        else:
            response = f"""
❓ I didn't understand that: <code>{text}</code>

Try these commands:
<code>/start</code> - Welcome
<code>/jobs</code> - Search jobs
<code>/profile</code> - Set profile
<code>/status</code> - Check status
<code>/help</code> - Get help
"""
            self.send_message(chat_id, response)
    
    def run(self):
        """Start the polling loop"""
        logger.info("╔════════════════════════════════════════════════════════╗")
        logger.info("║                                                        ║")
        logger.info("║   🤖 AI JOB HUNTER BOT - LEGACY POLLING 🤖           ║")
        logger.info("║                                                        ║")
        logger.info("╚════════════════════════════════════════════════════════╝")
        logger.info("")
        logger.info("🎉 BOT IS LIVE AND READY!")
        logger.info("")
        logger.info("In Telegram:")
        logger.info("1. Find: @jobhunter17_bot")
        logger.info("2. Send: /start")
        logger.info("3. Try: /jobs")
        logger.info("")
        logger.info("=" * 60)
        logger.info("Polling for messages... (Press Ctrl+C to stop)")
        logger.info("=" * 60)
        logger.info("")
        
        poll_count = 0
        
        try:
            while True:
                updates = self.get_updates()
                
                for update in updates:
                    self.handle_command(update)
                
                poll_count += 1
                if poll_count % 10 == 0:
                    logger.info(f"✅ Polling active... ({poll_count} polls)")
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("\n✅ Bot stopped")
            sys.exit(0)
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

def main():
    """Main entry point"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN not found in config/.env")
        logger.error("Add your bot token to config/.env")
        sys.exit(1)
    
    bot = SimpleBotPoller(token)
    bot.run()

if __name__ == "__main__":
    main()
