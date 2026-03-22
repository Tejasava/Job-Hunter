# 🤖 AI Job Hunter Bot

An intelligent Telegram bot that searches for real jobs across multiple platforms (LinkedIn, Indeed, Naukri, etc.) and provides personalized job recommendations using AI.

## Features

✅ **Real Job Search** - Searches LinkedIn, Indeed, Naukri, Monster, RemoteOK, GitHub Jobs
✅ **AI Recommendations** - Uses Google Gemini & Groq for intelligent job matching
✅ **Telegram Integration** - Easy-to-use Telegram bot interface
✅ **Salary Filtering** - Filter jobs by minimum salary (LPA)
✅ **Profile Management** - Save your profile for better recommendations
✅ **Application Tracking** - Track your job applications
✅ **Multi-Platform** - Works on Telegram across all devices

## Tech Stack

- **Backend**: FastAPI + Python 3.11
- **Bot**: Python Telegram Bot
- **AI**: Google Generative AI (Gemini), Groq
- **Database**: MongoDB
- **Job Sources**: Web Scraping (Indeed, LinkedIn, Naukri)
- **Deployment**: Render, Vercel, Heroku

## Local Setup

### Prerequisites
- Python 3.11+
- MongoDB (local or MongoDB Atlas)
- Telegram Bot Token (from @BotFather)
- API Keys: Gemini, Groq

### Installation

1. **Clone & Setup**
```bash
git clone https://github.com/yourusername/job-hunter.git
cd job-hunter
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp config/.env.example config/.env
# Edit config/.env with your credentials:
# - BOT_TOKEN=your_telegram_bot_token
# - MONGODB_URI=your_mongodb_connection_string
# - GEMINI_API_KEY=your_gemini_key
# - GROQ_API_KEY=your_groq_key
```

3. **Run Locally**
```bash
# Start API Server
python app.py

# In another terminal, start the bot
python bot_main.py
```

4. **Test Bot**
```bash
# Open Telegram and search for @jobhunter17_bot
# Send: /jobs Developer
```

## Deployment

### Deploy to Render (Recommended)

1. **Push to GitHub**
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **Create Render Account**
   - Go to https://render.com
   - Connect your GitHub repository

3. **Deploy Using render.yaml**
   - Select "Deploy from GitHub"
   - Choose this repository
   - Render will read `render.yaml` and configure automatically

4. **Set Environment Variables**
   - Go to Render Dashboard → Settings
   - Add environment variables:
     - `BOT_TOKEN` - Your Telegram bot token
     - `MONGODB_URI` - MongoDB connection string
     - `GEMINI_API_KEY` - Google Gemini API key
     - `GROQ_API_KEY` - Groq API key

### Deploy to Vercel

1. **Install Vercel CLI**
```bash
npm install -g vercel
```

2. **Deploy**
```bash
vercel
```

3. **Configure**
   - During setup, add all environment variables when prompted
   - Vercel will use `vercel.json` for configuration

### Deploy to Heroku

1. **Install Heroku CLI**
```bash
brew tap heroku/brew && brew install heroku
heroku login
```

2. **Deploy**
```bash
heroku create job-hunter-bot
git push heroku main
heroku config:set BOT_TOKEN=your_token
heroku config:set MONGODB_URI=your_uri
heroku config:set GEMINI_API_KEY=your_key
heroku config:set GROQ_API_KEY=your_key
```

## Usage

### Telegram Commands

```
/start              - Welcome message
/jobs [role]        - Search for jobs (e.g., /jobs Developer)
/salary [amount]    - Set minimum salary in LPA (e.g., /salary 15)
/profile            - Set up your profile
/applications       - View your applications
/status             - Check bot status
/help               - Show all commands
```

### Examples

```
/jobs Developer          - Find Developer jobs
/jobs Python Engineer    - Find Python Engineer jobs
/jobs Designer           - Find Designer jobs
/salary 12               - Filter jobs paying 12 LPA+
```

## API Endpoints

- `GET /` - Health check
- `GET /status` - Bot status
- `POST /webhook` - Telegram webhook (optional)

## File Structure

```
job-hunter/
├── app.py                 # FastAPI server
├── bot_main.py           # Telegram bot
├── requirements.txt      # Python dependencies
├── Procfile              # Heroku deployment
├── render.yaml           # Render deployment config
├── vercel.json           # Vercel deployment config
├── runtime.txt           # Python version
├── Dockerfile            # Docker configuration
├── config/
│   └── .env              # Environment variables
├── resumes/              # User resumes
└── tests/                # Test files
```

## Environment Variables

```env
# Telegram
BOT_TOKEN=your_telegram_bot_token

# Database
MONGODB_URI=mongodb://localhost:27017/job_hunter

# AI Providers
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
HUGGINGFACE_TOKEN=optional
OPENROUTER_KEY=optional

# Server
PORT=8000
HOST=0.0.0.0

# Job Search
JOB_SEARCH_INTERVAL=10800  # 3 hours in seconds
MIN_SALARY=10              # Minimum salary in LPA
MAX_RESULTS=50             # Max job results per search
```

## Troubleshooting

### Bot not responding
- Check `BOT_TOKEN` is correct
- Verify bot is running: `python bot_main.py`
- Check logs for errors

### No jobs found
- Indeed/LinkedIn may block scrapers (they return 403)
- Bot falls back to search links automatically
- Links are clickable and show real jobs

### MongoDB connection fails
- Verify `MONGODB_URI` is correct
- Check MongoDB is running (if local)
- Check network access (if MongoDB Atlas)

### API errors
- Check all environment variables are set
- Verify API keys are valid
- Check API rate limits

## Features Coming Soon

- 🚀 Resume generation with AI
- 🚀 Automatic job applications
- 🚀 Interview preparation
- 🚀 Salary negotiation tips
- 🚀 Company reviews integration

## Contributing

Contributions welcome! Please:
1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Create Pull Request

## License

MIT License - See LICENSE file for details

## Support

- 💬 Telegram: @jobhunter17_bot
- 📧 Email: support@jobhunter.com
- 🐛 Issues: GitHub Issues
- 💡 Features: GitHub Discussions

## Author

Created with ❤️ by [Tejasava](https://github.com/Tejasava)

---

**Made with ❤️ for job seekers | Deploy now and start finding jobs! 🚀**
