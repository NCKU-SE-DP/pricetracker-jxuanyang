PAGES_INFO_URL = "sqlite:///./news_database.db"
OPENAI_API_KEY = "your_news_api_key"

import dotenv
import os

dotenv.load_dotenv()
class Config:
        FASTAPI_PREFIX = "/api/v1"
        SENTRY_DSN = "https://4001ffe917ccb261aa0e0c34026dc343@o4505702629834752.ingest.us.sentry.io/4507694792704000"
        SENTRY_TRACES_SAMPLE_RATE = 1.0
        SENTRY_PROFILES_SAMPLE_RATE = 1.0
        ALLOWED_ORIGINS = ["http://localhost:8080"]
        LLM_ENABLED = True
        OPENAI_TOKEN = os.getenv("OPENAI_TOKEN", "")
        OPENAI_LLM_MODEL = "gpt-3.5-turbo"
        ANTHROPIC_TOKEN = os.getenv("ANTHROPIC_TOKEN", "")
        ANTHROPIC_LLM_MODEL = "claude-3-5-sonnet-20240620"
        SECRET_KEY = "1892dhianiandowqd0n"
        USERNAME_MAX_LENGTH = 50
        HASHED_PASSWORD_MAX_LENGTH = 200
        TOKEN_ENTRY_URL = "/api/v1/users/login"
        ACCESS_TOKEN_EXPIRE_MINUTES = 30
        NEWS_FETCH_INTERVAL_MINUTES = 100