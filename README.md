# AI Job Hunter Agent

A production-ready AI-powered Telegram bot that automatically searches for jobs globally, analyzes job descriptions using AI, generates tailored resumes, detects skill gaps, and optionally auto-applies to jobs.

## Features

### 🌍 Global Job Search
- Searches across **50+ job platforms** globally:
  - LinkedIn, Indeed, Naukri (India), RemoteOK, WeWorkRemotely
  - GitHub Jobs, Wellfound, Glassdoor, Monster, Dice
  - And more...
- Filters jobs by salary, location, and job type
- Deduplicates results from multiple sources

### 🤖 AI-Powered Job Analysis
- Analyzes job descriptions using multiple AI models (Groq, Gemini, HuggingFace, OpenRouter)
- Extracts:
  - Required and preferred skills
  - Job type and remote policy
  - Growth opportunities
  - Salary information (estimates if missing)
  - Key technologies and tools

### 📄 Smart Resume Generation
- Generates tailored resumes optimized for each job
- Uses AI to highlight matching skills
- Includes keywords from job descriptions
- ATS (Applicant Tracking System) optimized
- Outputs as professional PDF

### 🧠 Skill Gap Analysis
- Compares your skills with job requirements
- Identifies missing critical skills
- Suggests learning resources:
  - Free online courses (Coursera, Udemy, YouTube)
  - Official documentation
  - Practice projects
  - Learning roadmaps

### 🚀 Automated Job Applications
- Auto-fills application forms using stored profile data
- Uses browser automation (Playwright) for form submission
- Uploads generated resume automatically
- Requires user confirmation before applying
- Supports multiple platforms

### 📊 Application Tracking
- Stores all applications in MongoDB
- Tracks application status (pending, applied, interview, offer, etc.)
- View application history
- Track communication and feedback

### 🔄 Periodic Job Scanning
- Automatically scans job websites every 3 hours
- Notifies you of new matching jobs via Telegram
- Filters by your salary bar and preferences
- Works 24/7 in the background

## Tech Stack

- **Backend**: Python 3.8+
- **Framework**: FastAPI
- **Telegram Bot**: python-telegram-bot
- **Database**: MongoDB
- **Browser Automation**: Playwright
- **Job Scheduling**: APScheduler
- **AI Models**: Multi-LLM with automatic fallback
  - Groq (Free tier available)
  - Google Gemini API
  - HuggingFace Inference API
  - OpenRouter
  - Local Ollama

## Installation

### Prerequisites
- Python 3.8 or higher
- MongoDB (local or cloud)
- Telegram Bot Token

### Setup Steps

1. **Clone the repository** (or copy the files)
```bash
cd ai-job-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Create .env configuration**
```bash
cp config/.env.example config/.env
```

4. **Add API keys** to `config/.env`:
```env
# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_token_here

# AI Model APIs
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
HUGGINGFACE_API_KEY=your_hf_token
OPENROUTER_API_KEY=your_openrouter_key

# Database
MONGODB_URI=mongodb://localhost:27017/job_hunter

# Configuration
DEFAULT_AI_PROVIDER=groq
JOB_SEARCH_INTERVAL_HOURS=3
DEFAULT_SALARY_BAR_LPA=10
```

5. **Run the bot**
```bash
python run_bot.py
```

## Getting API Keys

### Telegram Bot Token
1. Open Telegram and search for `@BotFather`
2. Use `/newbot` to create a new bot
3. Copy the token provided

### Google Gemini API
1. Visit https://ai.google.dev
2. Get your free API key
3. Add to `.env`

### Groq API (Recommended - Fastest)
1. Visit https://console.groq.com
2. Sign up and generate API key
3. Free tier available with generous limits

### HuggingFace Token
1. Visit https://huggingface.co/settings/tokens
2. Create a **READ token** (not write)
3. Add to `.env`

### OpenRouter API
1. Visit https://openrouter.ai
2. Create account and generate API key
3. Free credits available

### MongoDB
1. Local: Install MongoDB locally
2. Cloud: https://www.mongodb.com/cloud/atlas (free tier available)

## Usage

### Telegram Commands

```
/start          - Welcome and menu
/profile        - Setup your profile
/jobs 12 AI     - Search jobs (salary=12 LPA, role=AI)
/salary 15      - Set minimum salary bar
/skills         - View/update skills
/status         - Check bot status
/applications   - View job applications
/help           - Get detailed help
```

### Example Workflow

1. **Start the bot**
   ```
   /start
   ```

2. **Setup your profile**
   ```
   /profile
   ```
   Answer questions about experience, skills, etc.

3. **Search for jobs**
   ```
   /jobs 12 Full Stack Developer
   ```
   - Shows matching jobs from multiple platforms
   - AI analyzes each job description
   - Shows skill match score

4. **Apply to a job**
   - Click "Apply" button
   - Bot generates tailored resume
   - Review and confirm
   - Auto-submit with resume

5. **Track applications**
   ```
   /applications
   ```
   - View all submitted applications
   - Track status and dates

6. **Check skill gaps**
   - Bot suggests learning resources
   - Creates personalized learning roadmap

## Configuration Options

### .env Settings

```env
# Job Search
JOB_SEARCH_INTERVAL_HOURS=3        # How often to scan for new jobs
DEFAULT_SALARY_BAR_LPA=10           # Default minimum salary

# AI Provider
DEFAULT_AI_PROVIDER=groq            # Primary AI model
# Fallback order: groq → gemini → huggingface → openrouter → ollama

# Application
FLASK_ENV=production
DEBUG=False
MAX_RETRIES=3
TIMEOUT_SECONDS=30
```

## AI Providers - Free Tier Limits

| Provider | Free Tier | Limit | Speed |
|----------|-----------|-------|-------|
| Groq | Yes | 30 req/min | ⚡ Fastest |
| Gemini | Yes | 60 req/min | ⚡ Fast |
| HuggingFace | Yes | Limited | Medium |
| OpenRouter | Yes | Limited | Medium |
| Ollama | Yes (local) | Unlimited | Depends on GPU |

**Automatic fallback ensures continuity if one provider hits limits.**

## Project Structure

```
ai-job-agent/
├── backend/
│   ├── agents/              # AI agents
│   │   ├── global_search_agent.py
│   │   ├── jd_analyzer_agent.py
│   │   ├── resume_agent.py
│   │   ├── skill_gap_agent.py
│   │   └── apply_agent.py
│   ├── providers/           # AI API providers
│   │   └── ai_router.py
│   ├── scrapers/            # Job scrapers
│   │   ├── indeed_scraper.py
│   │   ├── naukri_scraper.py
│   │   ├── linkedin_scraper.py
│   │   └── ...
│   ├── telegram/            # Telegram bot
│   │   ├── telegram_bot.py
│   │   ├── commands.py
│   │   ├── handlers.py
│   │   └── buttons.py
│   ├── resume/              # Resume generation
│   │   ├── resume_generator.py
│   │   └── pdf_builder.py
│   └── database/            # Database
│       ├── mongo.py
│       └── models.py
├── config/
│   └── .env                 # Configuration
├── resumes/                 # Generated resumes
├── requirements.txt         # Python dependencies
├── app.py                   # FastAPI app (optional)
├── run_bot.py              # Bot startup script
├── setup.py                # Installation script
└── README.md               # This file
```

## Security & Privacy

✅ **Implemented:**
- Environment variable configuration for secrets
- MongoDB connection pooling
- Input validation
- Rate limiting on API calls
- Secure credential storage
- No data sharing with third parties

⚠️ **Note:**
- Store `.env` securely, never commit to git
- Use read-only HuggingFace tokens
- MongoDB credentials in secure vaults in production
- Consider using environment-specific configurations

## Troubleshooting

### "TELEGRAM_BOT_TOKEN not set"
- Add your token to `config/.env`
- Ensure the file is in the correct location

### "MongoDB connection failed"
- Check MongoDB is running: `mongod`
- Or update `MONGODB_URI` in `.env` with cloud connection
- Default: `mongodb://localhost:27017/job_hunter`

### "AI Provider errors"
- Check API keys are correct in `.env`
- Verify API quotas and rate limits
- Bot will automatically fallback to next provider
- Check logs for detailed error messages

### "Resume generation failed"
- Complete your profile first: `/profile`
- Ensure job description was extracted
- Check if ReportLab is installed: `pip install reportlab`

### "Browser automation not working"
- Install Playwright: `pip install playwright`
- Install browsers: `playwright install`
- Some sites may require additional handling

## Performance Optimization

- **Concurrent job scraping**: Searches multiple platforms simultaneously
- **Database indexing**: Fast query performance
- **Caching**: Stores recently searched jobs
- **Async operations**: Non-blocking I/O
- **Connection pooling**: Efficient resource usage

## Limitations & Future Enhancements

### Current Limitations
- Some platforms have anti-scraping measures
- Manual intervention may be needed for some applications
- Salary information not available from all sources
- Resume generation requires complete profile data

### Planned Features
- [x] Multi-LLM support with fallback
- [x] Global job search
- [x] Resume generation
- [ ] Interview preparation module
- [ ] Salary negotiation guide
- [ ] Job preferences learning
- [ ] Recommendation engine
- [ ] Integration with LinkedIn direct messaging
- [ ] Mobile app
- [ ] Premium features (priority search, etc.)

## Contributing

Contributions welcome! Areas for enhancement:
- Additional job scrapers
- Improved resume templates
- Better skill gap analysis
- Interview preparation content
- Code optimization

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or feature requests:
- Check the troubleshooting section
- Review logs in the application
- Create an issue with detailed information

## Credits

Built with:
- Python & FastAPI
- python-telegram-bot
- Groq, Google, HuggingFace, OpenRouter APIs
- MongoDB
- Playwright

## Disclaimer

This tool is for personal use in job searching. Ensure you comply with:
- Job platform Terms of Service
- Local laws regarding web scraping
- API usage terms and conditions
- Employment laws in your jurisdiction

Use responsibly and ethically. 

---

**Let's automate your job search! 🚀**

For updates and more information, check the documentation and GitHub repository.
