# config/settings.py
# This file reads our .env file and makes all settings available

from dotenv import load_dotenv
import os

# This line reads the .env file and loads all values into memory
load_dotenv()

# Application Settings
APP_NAME = os.getenv("APP_NAME", "ReguMind")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "True") == "True"

# OpenAI Settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Qdrant Vector Database Settings
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

# Redis Cache Settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Database Settings
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Print confirmation when this file is loaded
print(f"Configuration loaded for: {APP_NAME} v{APP_VERSION}")