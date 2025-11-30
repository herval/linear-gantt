"""
Configuration management for Linear Gantt Chart Visualizer
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Linear API Configuration
LINEAR_API_KEY = os.getenv("LINEAR_API_KEY", "")
LINEAR_API_URL = "https://api.linear.app/graphql"

# Cache Configuration
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # Default: 1 hour

# Rate Limiting
LINEAR_RATE_LIMIT = 1000  # requests per hour
BACKOFF_FACTOR = 2  # Exponential backoff multiplier

# Color Schemes
STATUS_COLORS = {
    "todo": "#6B7280",      # Gray
    "in_progress": "#3B82F6",  # Blue
    "done": "#10B981",      # Green
    "cancelled": "#EF4444"  # Red
}

PRIORITY_COLORS = {
    "urgent": "#EF4444",    # Red
    "high": "#F97316",      # Orange
    "medium": "#EAB308",    # Yellow
    "low": "#10B981"        # Green
}

# Performance Settings
MAX_ISSUES_PER_REQUEST = 100
PAGE_LOAD_TARGET = 3  # seconds
API_RESPONSE_TARGET = 2  # seconds

# UI Configuration
DEFAULT_GROUPING = "project"
AVAILABLE_GROUPINGS = ["project", "assignee", "status", "cycle", "label"]

def validate_config():
    """Validate required configuration is present"""
    if not LINEAR_API_KEY:
        raise ValueError("LINEAR_API_KEY is required. Please set it in your .env file")
    return True
