import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME")
DEBUG = os.getenv("DEBUG") == "true"
DATABASE_URL = os.getenv("DATABASE_URL")

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SERVICE_ROLE_KEY")
# Use service role key if set (server-side, bypasses RLS), otherwise anon key
SUPABASE_KEY = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY
# SSL verification for Supabase (set to "false" to disable SSL verification in development)
SUPABASE_VERIFY_SSL = os.getenv("SUPABASE_VERIFY_SSL", "true").lower() == "true"

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL or CONNECTION_STRING environment variable is not set. "
        "Please set it in your .env file or environment variables. "
        "For Supabase (recommended - use connection pooler): "
        "DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require"
    )

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL and either SUPABASE_ANON_KEY or SERVICE_ROLE_KEY (or SUPABASE_SERVICE_ROLE_KEY) are required. "
        "Please set them in your .env file. "
        "You can find these in your Supabase Dashboard → Settings → API"
    )

# Redis configuration for caching
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_URL = os.getenv("REDIS_URL", None)  # Optional: full Redis URL (e.g., redis://:password@host:port/db)

# Cache TTL settings (in seconds)
CACHE_TTL_JOBS_LIST = int(os.getenv("CACHE_TTL_JOBS_LIST", "300"))  # 5 minutes default
CACHE_TTL_JOB_DETAIL = int(os.getenv("CACHE_TTL_JOB_DETAIL", "600"))  # 10 minutes default
CACHE_TTL_JOBS_BY_USER = int(os.getenv("CACHE_TTL_JOBS_BY_USER", "300"))  # 5 minutes default