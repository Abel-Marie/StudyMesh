import os
from dotenv import load_dotenv
from google.genai import types

# Load environment variables
load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# LLM Configuration
def get_retry_config():
    """Returns retry configuration for LLM calls."""
    return types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )

# App Configuration
APP_TITLE = "🎯 AI Productivity Planner"
APP_ICON = "🎯"

# Task Types
TASK_TYPES = ["daily", "weekly", "long-term"]

# Task Status
TASK_STATUS = ["pending", "in_progress", "completed", "overdue"]

# Deadline Categories
DEADLINE_CATEGORIES = [
    "Scholarship",
    "Internship",
    "Fellowship",
    "Conference",
    "Application",
    "Project",
    "Other"
]

# Social Media Platforms
SOCIAL_PLATFORMS = ["linkedin", "twitter", "medium"]
