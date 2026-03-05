# fastapi-template

### Generate evironment for the project
```python3 -m venv venv```
### Enable the Environment
```
# For macOS / linux
~ source venv/bin/activate

# For PowerShell
~ .\venv\Scripts\Active
```
### If cloned install requirements
```pip install -r requirements.txt```
### Run the server locally
```uvicorn main:app --reload```
### Lock the downloaded packages once installed
```pip freeze > requirements.txt```

## Docker

### Build and run with Docker

```bash
# Build the image
docker build -t fastapi-template .

# Run with .env file (ensure .env has SUPABASE_URL, SERVICE_ROLE_KEY or SUPABASE_ANON_KEY, DATABASE_URL)
docker run -p 8000:8000 --env-file .env fastapi-template

# Run with env vars bypassing
docker run -p 8000:8000 \
  -e SUPABASE_URL="https://your-project.supabase.co" \
  -e SERVICE_ROLE_KEY="your-service-role-key" \
  -e REDIS_HOST="host.docker.internal" \
  fastapi-template
```

### Run with Docker Compose (includes Redis)

```bash
docker compose up -d
```

API available at http://localhost:8000. Redis runs as a separate service; the API connects to it automatically.

### Environment variables for Docker

Required in `.env`:
- `SUPABASE_URL` – Supabase project URL
- `SERVICE_ROLE_KEY` or `SUPABASE_ANON_KEY` – Supabase API key
- `DATABASE_URL` – PostgreSQL connection string

Optional (for Redis when running standalone):
- `REDIS_HOST=host.docker.internal` – Use when running `docker run` without compose (macOS/Windows)

## Database Migrations

This project uses Alembic for database migrations. 

### First Time Setup

After installing dependencies, you may need to create an initial migration:

```bash
# Create initial migration (if tables don't exist yet)
alembic revision --autogenerate -m "initial migration"

# Apply migrations
alembic upgrade head
```

### Common Migration Commands

```bash
# Create a new migration after model changes
alembic revision --autogenerate -m "description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Check current migration status
alembic current
```

For detailed migration guide, see [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)