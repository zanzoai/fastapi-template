from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from api.routes.v1.router import router as api_router_v1
from api.routes.v2.router import router as api_router_v2
from core.db import engine, Base
from infrastructure.db.models import (
    User,
    Blog,
    Job,
    ZanUser,
    ZanCrew,
    ChatRoom,
    ChatParticipant,
    ChatMessage,
    MessageRead,
)  # Import models to register them
from core.cache import get_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created/verified successfully")
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
        print("Make sure your CONNECTION_STRING is correct and the database is accessible")

    try:
        redis_client = get_redis_client()
        redis_client.ping()
        print("Redis connection established successfully")
    except Exception as e:
        print(f"Warning: Could not connect to Redis: {e}")
        print("Caching will be disabled. Make sure Redis is running and configured correctly.")

    yield
    # Shutdown (add cleanup here if needed)


app = FastAPI(title="Zanzo Service", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return validation errors in a consistent, API-friendly format."""
    errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err.get("loc", []) if loc != "body")
        msg = err.get("msg", "Validation error")
        # Extract message from "Value error, <message>" for cleaner output
        if msg.startswith("Value error, "):
            msg = msg.replace("Value error, ", "")
        errors.append({"field": field or "body", "message": msg})
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": errors[0]["message"] if len(errors) == 1 else "Validation failed",
                "details": errors,
            },
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Return HTTP errors in a consistent, API-friendly format."""
    detail = exc.detail
    if isinstance(detail, dict):
        message = detail.get("message", detail.get("error", str(detail)))
    else:
        message = str(detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": "HTTP_ERROR",
                "message": message,
                "details": detail if isinstance(detail, dict) else None,
            },
        },
    )


@app.get("/")
def main():
    return {"message": "Welcome to Zanzo Backend API"}

app.include_router(api_router_v1)
app.include_router(api_router_v2)
