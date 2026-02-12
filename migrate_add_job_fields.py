#!/usr/bin/env python3
"""
Migration script to add job_loc and job_status columns to jobs table
Run this once to update your existing database schema
"""
from core.config import DATABASE_URL
from sqlalchemy import create_engine, text

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in .env file")
    exit(1)

try:
    # Configure SSL for Supabase if needed
    connect_args = {}
    if "supabase.co" in DATABASE_URL:
        if "sslmode" not in DATABASE_URL.lower():
            connect_args = {"sslmode": "require"}
        connect_args.update({
            "connect_timeout": 10,
        })
    
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    
    print("Connecting to database...")
    with engine.connect() as conn:
        # Start a transaction
        trans = conn.begin()
        
        try:
            # Check if columns already exist
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'jobs' 
                AND column_name IN ('job_loc', 'job_status')
            """)
            result = conn.execute(check_query)
            existing_columns = [row[0] for row in result]
            
            # Add job_loc if it doesn't exist
            if 'job_loc' not in existing_columns:
                print("Adding job_loc column...")
                conn.execute(text("ALTER TABLE jobs ADD COLUMN job_loc VARCHAR"))
                print("✅ Added job_loc column")
            else:
                print("⚠️  job_loc column already exists")
            
            # Add job_status if it doesn't exist
            if 'job_status' not in existing_columns:
                print("Adding job_status column...")
                conn.execute(text("ALTER TABLE jobs ADD COLUMN job_status VARCHAR"))
                print("✅ Added job_status column")
            else:
                print("⚠️  job_status column already exists")
            
            # Commit the transaction
            trans.commit()
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Error during migration: {e}")
            raise
        
except Exception as e:
    print(f"❌ Migration failed: {e}")
    exit(1)

