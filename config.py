"""
Configuration file for Vaibhav Social Monitor
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Person to monitor
PERSON_NAME = "Vaibhav Sisinity"

# Email settings
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "gaurav.sabhani@lenskart.com")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")

# Scheduling
RUN_TIME = "07:00"  # 7 AM IST

# Logging
DEBUG = False
