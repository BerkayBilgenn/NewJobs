# Reverse Job Search Dashboard

A POC that lets you upload your CV and uses a Selenium bot to find matching jobs on LinkedIn.

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r ../requirements.txt

# Create .env file with your LinkedIn bot credentials
copy ..\.env.example .env
# Edit .env and add your LinkedIn credentials

# Start the API server
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies (already done if you ran create-vite)
npm install

# Start development server
npm run dev
```

### 3. Usage

1. Open `http://localhost:5173` in your browser
2. Drag and drop your CV (PDF)
3. Click "Analyze CV" to extract keywords
4. Click "Search Jobs on LinkedIn" to let the bot find matching jobs
5. View matched jobs with compatibility scores

## ⚠️ Important Notes

- **LinkedIn Bot Account**: Use a dedicated bot account, NOT your personal LinkedIn
- **First Run**: The bot will log in and save cookies to `backend/cookies.pkl`
- **Rate Limiting**: The bot uses random delays to avoid detection
- **Chrome Required**: Make sure Chrome browser is installed

## 🛠️ Tech Stack

- **Backend**: FastAPI, Selenium, PyPDF2, Scikit-Learn
- **Frontend**: React, Vite, Tailwind CSS, Axios
- **Bot**: undetected-chromedriver for LinkedIn scraping

## 📁 Project Structure

```
CV_PROJE/
├── backend/
│   ├── main.py         # API endpoints
│   ├── bot.py          # LinkedIn Selenium bot
│   ├── matcher.py      # ML matching engine
│   └── uploads/        # Uploaded CVs
├── frontend/
│   └── src/
│       ├── App.jsx     # Main dashboard
│       └── components/
│           └── JobCard.jsx
└── requirements.txt
```
