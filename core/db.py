# app/core/db.py
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import DATABASE_URL

logger = logging.getLogger(__name__)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not configured. Please set CONNECTION_STRING in your environment.")

# Warn if using direct connection instead of pooler for Supabase
if "supabase.co" in DATABASE_URL and ":5432" in DATABASE_URL and "pooler" not in DATABASE_URL:
    print("⚠️  WARNING: You are using Supabase direct connection (port 5432).")
    print("   This may cause connection timeouts. Consider using the connection pooler (port 6543).")
    print("   Get it from: Supabase Dashboard → Settings → Database → Connection Pooling")

# Configure engine with SSL support for Supabase/cloud databases
# Supabase connection strings typically already include sslmode in the URL
# If not present, we'll add it via connect_args
connect_args = {}
if "supabase.co" in DATABASE_URL:
    # Supabase requires SSL connections - add if not already in URL
    if "sslmode" not in DATABASE_URL.lower():
        connect_args = {"sslmode": "require"}
    # Add connection timeout and keepalive settings for Supabase
    connect_args.update({
        "connect_timeout": 10,  # 10 second connection timeout
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    })

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,  # Number of connections to maintain
    max_overflow=10,  # Additional connections beyond pool_size
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args=connect_args,
)

# Supabase pooler (PgBouncer) in transaction mode: disable prepared statements
# so each command runs in a single round-trip and isn't tied to a session.
if "supabase.co" in DATABASE_URL and "pooler" in DATABASE_URL:
    @event.listens_for(engine, "connect")
    def _set_prepare_threshold(dbapi_conn, connection_record):
        try:
            dbapi_conn.prepare_threshold = 0
        except AttributeError:
            pass  # not psycopg2

logger.info("Engine created successfully")

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
