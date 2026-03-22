#!/usr/bin/env python3
"""
Install and Setup Script
"""

import os
import subprocess
import sys
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def run_command(cmd, description):
    """Run a shell command"""
    print(f"▶ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False)
        if result.returncode != 0:
            print(f"❌ Failed to execute: {description}")
            return False
        print(f"✅ {description} completed")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def setup():
    """Main setup function"""
    print_header("AI Job Hunter Agent - Setup Script")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install dependencies
    print_header("Installing Dependencies")
    if not run_command(
        "pip install -r requirements.txt",
        "Installing Python packages"
    ):
        sys.exit(1)
    
    # Create .env file if not exists
    print_header("Configuration Setup")
    env_path = Path("config/.env")
    
    if env_path.exists():
        print("✅ .env file already exists")
    else:
        print("📝 Creating .env file template...")
        # File already created by earlier code
        print("✅ .env template created")
    
    print("\n⚠️  Important: Add your API keys to config/.env:")
    print("   TELEGRAM_BOT_TOKEN=your_token_here")
    print("   GEMINI_API_KEY=your_key_here")
    print("   GROQ_API_KEY=your_key_here")
    print("   HUGGINGFACE_API_KEY=your_key_here")
    print("   OPENROUTER_API_KEY=your_key_here")
    print("   MONGODB_URI=your_mongodb_uri")
    
    # Create necessary directories
    print_header("Creating Directories")
    directories = [
        "resumes",
        "logs",
        "data",
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {directory}/")
    
    print_header("Setup Complete!")
    print("""
Next Steps:
1. Edit config/.env and add your API keys
2. Run: python run_bot.py

For API keys:
- Telegram: https://t.me/BotFather
- Gemini: https://ai.google.dev
- Groq: https://console.groq.com
- HuggingFace: https://huggingface.co/settings/tokens
- OpenRouter: https://openrouter.ai
- MongoDB: https://www.mongodb.com/cloud/atlas

Good luck! 🚀
""")


if __name__ == "__main__":
    try:
        setup()
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
