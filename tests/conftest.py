"""Pytest configuration and fixtures."""
import os

# Set minimal env before any app imports (for CI)
os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/test")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SERVICE_ROLE_KEY", "test-key-for-ci")
os.environ.setdefault("REDIS_HOST", "localhost")
