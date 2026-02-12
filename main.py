from fastapi import FastAPI
from api.routes.v1.router import router as api_router_v1
from api.routes.v2.router import router as api_router_v2
from core.db import engine, Base
from infrastructure.db.models import User, Blog, Job  # Import models to register them

app = FastAPI(title="Zanzo Service")

@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created/verified successfully")
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
        print("Make sure your CONNECTION_STRING is correct and the database is accessible")

@app.get("/")
def main():
    return {"message": "Welcome to Zanzo Backend API"}

app.include_router(api_router_v1)
app.include_router(api_router_v2)