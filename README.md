# Vaibhav Social Media Monitor

Automated system that monitors Vaibhav Sisinity's social media presence and sends daily email summaries.

## Features
- ✅ Automated daily emails at 7 AM IST
- ✅ Searches: Google, LinkedIn, Twitter
- ✅ AI-powered summaries with bullet points
- ✅ 100% Free
- ✅ Zero manual work

## Tech Stack
- Python 3.11
- GitHub Actions (Scheduling)
- Groq AI (Summarization)
- Gmail API (Email)

## How It Works
```
7 AM IST
  ↓
GitHub Actions triggers
  ↓
Search for Vaibhav on web
  ↓
Extract results
  ↓
Summarize with AI
  ↓
Send email with bullet points
```

## Setup
See the documentation for step-by-step setup instructions.

## Status
🚀 Ready to deploy
```
```
4. Click "Commit changes"
5. Done! ✅
```

---

### **FILE 2: requirements.txt**

**What to do:**
```
1. Click "Add file" > "Create new file"
2. Name: requirements.txt
3. Paste this:
```
```
requests==2.31.0
beautifulsoup4==4.12.2
python-dotenv==1.0.0
groq==0.4.2
```
```
4. Click "Commit changes"
5. Done! ✅
```

---

### **FILE 3: config.py**

**What to do:**
```
1. Click "Add file" > "Create new file"
2. Name: config.py
3. Paste this:
